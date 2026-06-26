import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal
from . import models
from .routers import auth, posts, comments, categories

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leru's Cozy Blog API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*", # يحل مشكلة الـ CORS مع الـ Credentials فوراً
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("static/uploads"): os.makedirs("static/uploads")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])

# زارع البيانات الأولي (حتى لا تفتحي الموقع وتجديه فارغاً من الكروت)
def seed_data():
    db = SessionLocal()
    try:
        if db.query(models.Category).count() == 0:
            defaults = [
                {"slug": "diary", "name": "Diary", "image_url": "https://i.pinimg.com/736x/f0/4d/8a/f04d8a8e798d73cc5696722d11cef9b5.jpg", "card_type": "standard"},
                {"slug": "music", "name": "Music", "image_url": "https://i.pinimg.com/736x/02/e5/10/02e510a04be848d72bac9505c57f67b9.jpg", "card_type": "music"},
                {"slug": "books", "name": "Books", "image_url": "https://i.pinimg.com/736x/8a/18/d2/8a18d221d42229cbeb857a9ede3224af.jpg", "card_type": "standard"},
                {"slug": "careerpath", "name": "Career Path", "image_url": "https://i.pinimg.com/736x/f2/fb/69/f2fb69e80970e82c0e86bd33d8caed55.jpg", "card_type": "standard"},
                {"slug": "gallery", "name": "Gallery", "image_url": "https://i.pinimg.com/736x/b3/e9/86/b3e986897a609d3a631fe68ad4c3649b.jpg", "card_type": "gallery"},
                {"slug": "poetry", "name": "Poetry", "image_url": "https://i.pinimg.com/736x/f0/4d/8a/f04d8a8e798d73cc5696722d11cef9b5.jpg", "card_type": "standard"},
                {"slug": "fangirling", "name": "Fangirling", "image_url": "https://i.pinimg.com/736x/dc/4b/8c/dc4b8c2cd32e8e84a968bbeae6c1c805.jpg", "card_type": "standard"},
            ]
            for c in defaults: db.add(models.Category(**c))
            db.commit()
    finally:
        db.close()

seed_data()