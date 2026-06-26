from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Category, User
from ..schemas import CategoryCreate, CategoryOut
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(cat: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403, detail="Unauthorized")
    if db.query(Category).filter(Category.slug == cat.slug).first():
        raise HTTPException(status_code=400, detail="Slug exists")
    new_cat = Category(**cat.model_dump())
    db.add(new_cat); db.commit(); db.refresh(new_cat)
    return new_cat

@router.put("/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, cat: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403)
    db_cat = db.query(Category).filter(Category.id == cat_id).first()
    if not db_cat: raise HTTPException(status_code=404)
    db_cat.slug = cat.slug; db_cat.name = cat.name; db_cat.image_url = cat.image_url; db_cat.card_type = cat.card_type
    db.commit(); db.refresh(db_cat)
    return db_cat

@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403)
    db.query(Category).filter(Category.id == cat_id).delete(); db.commit()
    return {"message": "Deleted"}