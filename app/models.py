from sqlalchemy import Column, Integer, Float, String, Text
from .database import Base


class Users(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), index=True, unique=True)
    email = Column(String(150), index=True, unique=True)
    password = Column(String(255), index=True)
    role = Column(String(50), index=True)

class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    qty = Column(Integer, nullable=False)
    minimum_qty = Column(Integer, nullable=False)
    max_qty = Column(Integer, nullable=False)
    image = Column(String(100), nullable=False)

class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
