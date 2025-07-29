from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from schemas import UserUpdate, UserOut
from utils import hash_password
from auth import get_current_user, get_db

router = APIRouter()

@router.put("/update-me", response_model=UserOut)
def update_user(update_data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()

    if update_data.email:
        user.email = update_data.email
    if update_data.username:
        user.username = update_data.username
    if update_data.password:
        user.hashed_password = hash_password(update_data.password)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/delete-me")
def delete_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}