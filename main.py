from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User
from schemas import UserCreate, UserLogin, UserOut
from utils import hash_password, verify_password, create_access_token
from auth import get_db, get_current_user
from token_blacklist import add_to_blacklist
from fastapi.security import OAuth2PasswordBearer
from routes import user_router

#  Define oauth2_scheme here instead of importing from utils
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()

#  Create database tables
Base.metadata.create_all(bind=engine)

#  Register Route
@app.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    hashed = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#  Login Route
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

#  Get Current User
@app.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

#  Logout Route
@app.post("/logout")
def logout(request: Request, token: str = Depends(oauth2_scheme)):
    add_to_blacklist(token)
    return {"message": "Successfully logged out"}

app.include_router(user_router)