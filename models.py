from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy_utc import UtcDateTime, utcnow
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(80))
    created = Column(UtcDateTime(), default=utcnow())

    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password

    def __repr__(self):
        return f'<User {self.email!r}>'


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    author_id = Column(ForeignKey("users.id"))
    created = Column(UtcDateTime(), default=utcnow())
    modified = Column(UtcDateTime(), onupdate=utcnow())
    title_pt = Column(String(200))
    title_en = Column(String(200))
    body_pt = Column(Text)
    body_en = Column(Text)

    def __init__(self, author_id=None, title_pt=None, title_en=None, body_pt=None, body_en=None):
        self.author_id = author_id
        self.title_pt = title_pt
        self.title_en = title_en
        self.body_pt = body_pt
        self.body_en = body_en

    def __repr__(self):
        if self.title_pt:
            return f'<News {self.title_pt!r} (id = {self.id})>'
        elif self.title_en:
            return f'<News {self.title_pt!r} (id = {self.id})>'
        else:
            return f'<News untitled (id = {self.id})>'
