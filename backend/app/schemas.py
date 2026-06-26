from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)

class CategoryCreate(BaseModel):
    slug: str
    name: str
    image_url: str
    card_type: str = "standard"

class CategoryOut(BaseModel):
    id: int
    slug: str
    name: str
    image_url: str
    card_type: str
    model_config = ConfigDict(from_attributes=True)

class CommentCreate(BaseModel):
    content: str
    guest_name: Optional[str] = "Anonymous Friend"
    post_id: int

class CommentOut(BaseModel):
    id: int
    content: str
    guest_name: Optional[str]
    created_at: datetime
    post_id: int
    user_id: Optional[int]
    model_config = ConfigDict(from_attributes=True)

class PostCreate(BaseModel):
    title: str
    content: str
    category: str
    image_url: Optional[str] = None
    media_url: Optional[str] = None

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    category: str
    image_url: Optional[str]
    media_url: Optional[str]
    created_at: datetime
    owner_id: int
    model_config = ConfigDict(from_attributes=True)