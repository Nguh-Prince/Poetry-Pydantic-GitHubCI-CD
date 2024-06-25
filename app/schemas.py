from pydantic import BaseModel, EmailStr, validator
from typing import Optional

from .models import Users
from .database import SessionLocal

class ModelInDB(BaseModel):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserInDB(UserBase, ModelInDB):
    role: str

class UserRegisterSchema(UserBase):
    @validator('email')
    def email_must_be_unique(cls, value):
        db = SessionLocal()
        
        if db.query(Users).filter(Users.email == value).first():
            raise ValueError("Email already exists")
        return value

    @validator('name')
    def name_must_be_unique(cls, value):
        db = SessionLocal() 
        
        if db.query(Users).filter(Users.name == value).first():
            raise ValueError("Username already exists")
        return value
    
class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class ItemBase(BaseModel):
    name: str
    price: float
    qty: int
    minimum_qty: int
    max_qty: int
    image: Optional[str] = None

class AddItemSchema(ItemBase):
    @validator('price')
    def price_greater_than_0(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")

        return value

class ItemInDB(ItemBase, ModelInDB):
    pass

class Contact(BaseModel):
    name: str
    email: EmailStr
    message: str

class ContactInDB(Contact, ModelInDB):
    pass