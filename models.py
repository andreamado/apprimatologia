from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy_utc import UtcDateTime, utcnow
from sqlalchemy.sql import func
from .db import Base

from flask import current_app as app

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


class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    file = Column(ForeignKey('uploaded_files.id'), nullable=False)
    subtitle_pt = Column(Text)
    subtitle_en = Column(Text)
    alt_pt = Column(Text)
    alt_en = Column(Text)

    def __init__(self, file, subtitle_pt=None, subtitle_en=None, alt_pt=None, alt_en=None):
        self.file = file
        self.subtitle_pt = subtitle_pt
        self.subtitle_en = subtitle_en
        self.alt_pt = alt_pt
        self.alt_en = alt_en

    def to_object(self, lang):
        return {
            # implement access to uploaded files
            'id': self.file,
            'subtitle': self.subtitle_pt if lang == 'pt' else self.subtitle_en,
            'alt': self.alt_pt if lang == 'pt' else self.alt_en
        }


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
    image = Column(ForeignKey('images.id'))

    def __init__(self, author_id=None, title_pt=None, title_en=None, body_pt=None, body_en=None, image=None):
        self.author_id = author_id
        self.title_pt = title_pt
        self.title_en = title_en
        self.body_pt = body_pt
        self.body_en = body_en
        self.image = image

    def __repr__(self):
        if self.title_pt:
            return f'<News {self.title_pt!r} (id = {self.id})>'
        elif self.title_en:
            return f'<News {self.title_pt!r} (id = {self.id})>'
        else:
            return f'<News untitled (id = {self.id})>'


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True)
    # Isto é o número de inscrição do sócio
    number = Column(Integer, unique=True)
    created = Column(UtcDateTime(), default=utcnow())
    modified = Column(UtcDateTime(), onupdate=utcnow())

    authorized = Column(Boolean, default=False)

    given_name = Column(String(50))
    family_name = Column(String(50))
    
    work_place = Column(String(50))
    research_line = Column(Text)
    species = Column(String(100))

    data_authorization = Column(Boolean)

    photo = Column(String(50))

    created = Column(UtcDateTime(), default=utcnow())
    modified = Column(UtcDateTime(), onupdate=utcnow())

    def __init__(self, number=None, given_name=None, family_name=None, work_place=None, research_line=None, species=None):
        self.number = number
        self.given_name = given_name
        self.family_name = family_name
        self.work_place = work_place
        self.research_line = research_line
        self.species = species

    def __repr__(self):
        return f'<Member {self.given_name!r} {self.family_name!r})>'


# direction: 0 normal member
# direction: 1 direction
# direction: 2 assembly
# direction: 3 supervisory board

class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"))

    name = Column(String(120))

    description_pt = Column(Text)
    description_en = Column(Text)

    direction = Column(Integer)
    direction_order = Column(Integer)
    position_pt = Column(Text)
    position_en = Column(Text)

    website = Column(Text)
    orcid = Column(String(20))

    photo = Column(ForeignKey("uploaded_files.id"))

    created = Column(UtcDateTime(), default=utcnow())
    modified = Column(UtcDateTime(), onupdate=utcnow())

    def __init__(self, user_id=None, name=None, description_pt=None, description_en=None, direction=False, direction_order=10000, position_pt=None, position_en=None, photo=None, website=None, orcid=None):
        self.user_id = user_id
        self.name = name
        self.description_pt = description_pt
        self.description_en = description_en
        self.direction = direction
        self.direction_order = direction_order
        self.position_pt = position_pt
        self.position_en = position_en
        self.photo = photo
        self.website = website
        self.orcid = orcid
