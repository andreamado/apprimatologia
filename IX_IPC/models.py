from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, Text, Numeric
from sqlalchemy_utc import UtcDateTime, utcnow

from .db_IXIPC import Base
from secrets import token_hex



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True)
    password = Column(String(32))
    name = Column(String(200))
    first_name = Column(String(200))
    last_name = Column(String(200))
    institution = Column(String(200))
    student = Column(Boolean)

    def __init__(self, name, email, password=None, first_name=None, last_name=None, institution=None, student=False):
        self.name = name
        self.email = email
        self.password = password if password else token_hex(16)
        self.first_name = first_name
        self.last_name = last_name
        self.institution = institution
        self.student = student


class PaymentMethod:
    MBWay = 1
    Card  = 2
    Other = 3

class PaymentStatus:
    successful = 1
    pending = 2
    failed = 3
    canceled = 4
    expired = 5 

import time
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))

    value = Column(Numeric(6, 2))
    method = Column(Integer)
    method_id = Column(String(20))
    transaction_id = Column(String(15))
    request_id = Column(String(30))
    status_code = Column(String(5))

    status = Column(Integer)

    started = Column(UtcDateTime(), default=utcnow())
    concluded = Column(UtcDateTime())

    def __init__(self, user_id, method, method_id, value, status=PaymentStatus.pending):
        self.user_id = user_id
        self.method = method
        self.method_id = method_id
        self.value = value
        self.transaction_id = f'{user_id:04}_{int(time.time())%10000:05}_{token_hex(nbytes=3)}'
        self.status = status

    def success(self):
        self.status = PaymentStatus.successful
        self.concluded = utcnow()

    def failed(self):
        self.status = PaymentStatus.failed
        self.concluded = utcnow()

    def canceled(self):
        self.status = PaymentStatus.canceled
        self.concluded = utcnow()

    def expired(self):
        self.status = PaymentStatus.expired
        self.concluded = utcnow()


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(200))
    last_name = Column(String(200))
    email = Column(String(200), unique=True)

    country = Column(String(200))
    
    created = Column(UtcDateTime(), default=utcnow())
    modified = Column(UtcDateTime(), onupdate=utcnow())

    created_by = Column(ForeignKey('users.id'))

    def __init__(self, created_by, first_name=None, last_name=None, email=None, country=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.country = country
        self.created_by = created_by

    def __repr__(self):
        return f'<Author {self.first_name!r} {self.last_name!r} ({self.email!r})>'


class Institution(Base):
    __tablename__ = 'institutions'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    address = Column(String(200))
    country = Column(String(200))

    created_by = Column(ForeignKey('users.id'))

    def __init__(self, created_by, name=None, address=None, country=None):
        self.name = name
        self.address = address
        self.country = country
        self.created_by = created_by

    def __repr__(self):
        return f'<Institution {self.name!r}>'


class Affiliation(Base):
    __tablename__ = 'affiliation'
    id = Column(Integer, primary_key=True)
    author_id = Column(ForeignKey('authors.id'))
    institution_id = Column(ForeignKey('institutions.id'))
    order = Column(Integer)

    def __init__(self, author_id, institution_id, order):
        self.author_id = author_id
        self.institution_id = institution_id
        self.order = order


class AbstractType:
    POSTER = 1
    PRESENTATION = 2
    BOTH = 3


class Abstract(Base):
    __tablename__ = 'abstracts'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    abstract = Column(Text)
    abstract_type = Column(Integer)
    keywords = Column(Text)
    owner = Column(ForeignKey('users.id'))
    submitted = Column(Boolean)
    submitted_on = Column(UtcDateTime())

    created = Column(UtcDateTime(), default=utcnow())
    modified = Column(UtcDateTime(), onupdate=utcnow())

    def __init__(self, owner, title=None, abstract=None, abstract_type=None, keywords='', submitted=False):
        self.title = title
        self.abstract = abstract
        self.abstract_type = abstract_type
        self.keywords = keywords
        self.owner = owner
        self.submitted = submitted

    def submit(self):
        self.submitted = True
        self.submitted_on = utcnow()


class AbstractAuthor(Base):
    __tablename__ = 'abstract_author'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'))
    abstract_id = Column(Integer, ForeignKey('abstracts.id'))
    presenter = Column(Boolean)
    order = Column(Integer)
    first_author = Column(Boolean)
    corresponding_author = Column(Boolean)

    def __init__(self, author_id, abstract_id, order=0, presenter=False, first_author=False, corresponding_author=False):
        self.author_id = author_id
        self.abstract_id = abstract_id
        self.presenter = presenter
        self.first_author = first_author
        self.corresponding_author = corresponding_author
        self.order = order
