import os
import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Post, User
from ..schemas import PostCreate, PostOut
from .auth import get_current_user
from typing import List


router = APIRouter()

# إعداد وتثبيت إعدادات Cloudinary باستخدام متغيرات البيئة
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

@router.post("/upload-image")
def upload_image(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    # السماح للآدمن فقط برفع الصور للمقالات
    if current_user.role != "admin": 
        raise HTTPException(status_code=403, detail="Unauthorized to upload media")
    
    try:
        # رفع الملف مباشرة إلى الكلاود داخل مجلد مخصص للموقع
        upload_result = cloudinary.uploader.upload(
            file.file, 
            folder="cozy_blog_archives"
        )
        
        # جلب الرابط الدائم والآمن المستقر
        secure_url = upload_result.get("secure_url")
        
        # إرجاع الرابط السحابي للفرونت إند بنفس الصيغة المتوقعة تماماً
        return {"image_url": secure_url}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Cloud storage failed: {str(e)}"
        )

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