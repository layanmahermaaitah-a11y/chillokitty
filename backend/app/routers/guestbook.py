from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import GuestbookEntry, User
from ..schemas import GuestbookCreate, GuestbookOut
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[GuestbookOut])
def get_guestbook_entries(db: Session = Depends(get_db)):
    return db.query(GuestbookEntry).order_by(GuestbookEntry.created_at.desc()).all()

@router.post("/", response_model=GuestbookOut, status_code=status.HTTP_201_CREATED)
def sign_guestbook(entry: GuestbookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_entry = GuestbookEntry(content=entry.content, user_id=current_user.id)
    db.add(new_entry); db.commit(); db.refresh(new_entry)
    return new_entry