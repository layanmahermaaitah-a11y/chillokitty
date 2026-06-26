from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Comment, Post, User # تم تصحيح استيراد User هنا
from ..schemas import CommentCreate, CommentOut
from .auth import get_current_user

router = APIRouter()

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    if not post: raise HTTPException(status_code=404, detail="Post not found")
    new_comment = Comment(**comment.model_dump())
    db.add(new_comment); db.commit(); db.refresh(new_comment)
    return new_comment

@router.get("/post/{post_id}", response_model=List[CommentOut])
def get_comments_for_post(post_id: int, db: Session = Depends(get_db)):
    if not db.query(Post).filter(Post.id == post_id).first(): raise HTTPException(status_code=404)
    return db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403)
    db.query(Comment).filter(Comment.id == comment_id).delete(); db.commit()
    return {"message": "Removed"}