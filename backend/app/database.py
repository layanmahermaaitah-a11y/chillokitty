import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# جلب رابط قاعدة البيانات من متغيرات البيئة (Environment Variables) الخاصة بـ Render
# وفي حال التطوير المحلي، سيتم الاعتماد على SQLite تلقائياً كخيار احتياطي
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leru_blog.db")

# التصحيح البرمجي الخاص بـ Render:
# استبدال postgres:// بـ postgresql:// لضمان توافق مكتبة SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# إعدادات الاتصال: نحتاجها فقط مع SQLite لمنع مشاكل الـ Threads في البيئة المحلية
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()