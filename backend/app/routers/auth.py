import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext

from ..database import get_db
from ..models import User
from ..schemas import UserCreate, UserOut

router = APIRouter()

# إعداد نظام تشفير كلمات المرور (Bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# إعداد نظام استخراج التوكن من الطلبات
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# المتغيرات السرية المأخوذة من ملف .env
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey_change_this_later_12345")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # صلاحية التوكن ساعة واحدة

# --- دالات مساعدة (Helper Functions) ---
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# دالة حماية (Dependency) للتحقق من هوية المستخدم في المسارات المحمية مستقبلاً
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


# --- مسارات الـ API (Endpoints) ---

# 1. مسار إنشاء حساب جديد
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # التأكد من أن اسم المستخدم غير مكرر
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # تشفير كلمة المرور قبل الحفظ
    hashed_pwd = hash_password(user_data.password)
    
    # أول حساب يتم إنشاؤه سيكون هو الـ Admin (أنتِ)، وباقي الحسابات guest تلقائياً
    user_count = db.query(User).count()
    user_role = "admin" if user_count == 0 else "guest"

    new_user = User(username=user_data.username, hashed_password=hashed_pwd, role=user_role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 2. مسار تسجيل الدخول وإصدار التوكن (JWT Token)
@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid username or password"
        )
    
    # إنشاء الـ Token وحقن اسم المستخدم وصلاحيته بداخلها
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}