import enum
from sqlalchemy import Column, Boolean, Enum, ForeignKey, Integer, String, Text
from sqlalchemy_utc import UtcDateTime, utcnow

from .db_IXIPC import Base
from secrets import token_hex

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True)
    participant_id = Column(ForeignKey('participants.id'))
    password = Column(String(32))
    name = Column(String(200))

    def __init__(self, name, email, password=None, participant_id=None):
        self.name = name
        self.email = email
        self.password = password if password else token_hex(16)
        self.participant_id = participant_id


class Participant(Base):
    __tablename__ = 'participants'
    id = Column(Integer, primary_key=True)
    name =  Column(String(200))
    email = Column(String(200), unique=True)

    country = Column(String(200))
    
    created = Column(UtcDateTime(), default=utcnow())
    modified = Column(UtcDateTime(), onupdate=utcnow())

    def __init__(self, name, email, country):
        self.name = name
        self.email = email
        self.country = country

    def __repr__(self):
        return f'<Participant {self.name!r} {self.email!r}>'


class Institution(Base):
    __tablename__ = 'institutions'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    address = Column(String(200))

    def __init__(self, name, address):
        self.name = name
        self.address = address

    def __repr__(self):
        return f'<Institution {self.name!r}>'


class Affiliation(Base):
    __tablename__ = 'affiliation'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('participants.id'))
    institution_id = Column(Integer, ForeignKey('institutions.id'))

    def __init__(self, author_id, institution_id):
        self.author_id = author_id
        self.institution_id = institution_id


class WorkType(enum.Enum):
    poster = 1
    presentation = 2
    both = 3


class Work(Base):
    __tablename__ = 'works'
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    abstract = Column(Text)
    work_type = Column(Enum(WorkType))

    def __init__(self, title, abstract, work_type):
        self.title = title
        self.abstract = abstract
        self.work_type = work_type


class WorkAuthor(Base):
    __tablename__ = 'work_author'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('participants.id'))
    work_id = Column(Integer, ForeignKey('works.id'))
    presenter = Column(Boolean)
    first_author = Column(Boolean)
    corresponding_author = Column(Boolean)

    def __init__(self, author_id, poster_id, presenter=False, first_author=False, corresponding_author=False):
        self.author_id = author_id
        self.poster_id = poster_id
        self.presenter = presenter
        self.first_author = first_author
        self.corresponding_author = corresponding_author

