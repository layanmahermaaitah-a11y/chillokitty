import os, shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import Post, User
from ..schemas import PostCreate, PostOut
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[PostOut])
def get_all_posts(db: Session = Depends(get_db)):
    return db.query(Post).order_by(Post.created_at.desc()).all()

@router.get("/{category}", response_model=List[PostOut])
def get_posts_by_category(category: str, db: Session = Depends(get_db)):
    return db.query(Post).filter(Post.category == category).order_by(Post.created_at.desc()).all()

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403)
    new_post = Post(**post.model_dump(), owner_id=current_user.id)
    db.add(new_post); db.commit(); db.refresh(new_post)
    return new_post

UPLOAD_DIR = "static/uploads"

@router.post("/upload-image")
def upload_image(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403)
    if not os.path.exists(UPLOAD_DIR): os.makedirs(UPLOAD_DIR)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    clean_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
    with open(os.path.join(UPLOAD_DIR, clean_filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"image_url": f"/static/uploads/{clean_filename}"} # مسار نسبي آمن للإنتاج

@router.delete("/{post_id}")
def delete_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin": raise HTTPException(status_code=403)
    db.query(Post).filter(Post.id == post_id).delete(); db.commit()
    return {"message": "Deleted"}

@router.put("/{post_id}")
def update_post(post_id: int, post_update: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin": raise HTTPException(status_code=403)
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post: raise HTTPException(status_code=404)
    for var, value in post_update.model_dump(exclude_unset=True).items():
        setattr(post, var, value)
    db.commit(); db.refresh(post)
    return post