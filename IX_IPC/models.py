from sqlalchemy import Column, Boolean, ForeignKey, Integer, String, Text, Numeric, select
from sqlalchemy_utc import UtcDateTime, utcnow

from .db_IXIPC import Base
from secrets import token_hex
from hashlib import sha256

class PaymentStatus:
    successful = 1
    pending = 2
    failed = 3
    canceled = 4
    expired = 5

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True)
    password = Column(String(64))
    name = Column(String(200))
    first_name = Column(String(200))
    last_name = Column(String(200))
    institution = Column(String(200))
    student = Column(Boolean)
    member = Column(Boolean)
    scholarship = Column(Boolean)
    unemployed = Column(Boolean)
    competition_talk = Column(Boolean)
    competition_photography = Column(Boolean)
    organizer = Column(Boolean)
    paid_registration = Column(Boolean)
    payment_id = Column(ForeignKey('payments.id'))
    dinner = Column(Boolean)
    dinner_type = Column(Integer)
    dinner_restriction = Column(String(200))
    dinner_p1 = Column(Boolean)
    dinner_type_p1 = Column(Integer)
    dinner_restriction_p1 = Column(String(200))

    def __init__(self, name, email, password=None, first_name=None, last_name=None, institution=None, student=False, member=False, scholarship=False, unemployed=False, competition_talk=False, competition_photography=False, paid_registration=False, organizer=False, dinner=False, dinner_type=1, dinner_restriction='', dinner_p1=False, dinner_type_p1=1, dinner_restriction_p1=''):
        self.name = name
        self.email = email
        self.password = sha256(password.encode()).hexdigest() if password else sha256(token_hex(16).encode()).hexdigest()
        self.first_name = first_name
        self.last_name = last_name
        self.institution = institution
        self.student = student
        self.member = member
        self.scholarship = scholarship
        self.unemployed = unemployed
        self.competition_talk = competition_talk
        self.competition_photography = competition_photography
        self.paid_registration = paid_registration
        self.organizer = organizer
        self.dinner = dinner
        self.dinner_type = dinner_type
        self.dinner_restriction = dinner_restriction
        self.dinner_p1 = dinner_p1
        self.dinner_type_p1 = dinner_type_p1
        self.dinner_restriction_p1 = dinner_restriction_p1

    def update_password(self, password) -> None:
        self.password = sha256(password.encode()).hexdigest()
    
    def check_password(self, password) -> bool:
        return self.password == sha256(password.encode()).hexdigest()
    
    def __repr__(self):
        return f'<User {self.first_name} {self.last_name} - {self.institution} ({"paid" if self.paid_registration == True else "not paid"})>'

class PaymentMethod:
    MBWay    = 1
    Card     = 2
    Other    = 3
    Transfer = 4

    def to_str(method):
        if method == PaymentMethod.MBWay:
            return 'MBWay'
        elif method == PaymentMethod.Card:
            return 'Credit Card'
        elif method == PaymentMethod.Transfer:
            return 'Transfer'
        else:
            return 'Unknown payment method'
            


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

    def success(self, db_session):
        self.status = PaymentStatus.successful
        self.concluded = utcnow()

        user = db_session.get(User, self.user_id)
        user.payment_id = self.id
        user.paid_registration = True

    def failed(self, db_session):
        self.status = PaymentStatus.failed
        self.concluded = utcnow()

        user = db_session.get(User, self.user_id)
        user.payment_id = None
        user.paid_registration = False

    def canceled(self, db_session):
        self.status = PaymentStatus.canceled
        self.concluded = utcnow()

        user = db_session.get(User, self.user_id)
        user.payment_id = None
        user.paid_registration = False

    def expired(self, db_session):
        self.status = PaymentStatus.expired
        self.concluded = utcnow()

        user = db_session.get(User, self.user_id)
        user.payment_id = None
        user.paid_registration = False


    def __repr__(self):
        return f'<Payment user={self.user_id!r} method={self.method!r} method_id={self.method_id!r} ({self.value}€) status={self.status}>'


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

    def get_list(db_session, author_id):
        affiliations = db_session.execute(
            select(Affiliation)
              .where(Affiliation.author_id == author_id)
              .order_by(Affiliation.order)
        ).scalars().all()

        for affiliation in affiliations:
            affiliation.institution = db_session.get(Institution, affiliation.institution_id)

        return affiliations


class AbstractType:
    POSTER = 1
    PRESENTATION = 2
    BOTH = 3

    def to_string(tp):
        if tp == AbstractType.POSTER:
            return 'Poster'
        elif tp == AbstractType.PRESENTATION:
            return 'Oral presentation'
        elif tp == AbstractType.BOTH:
            return 'Both'
        else:
            return 'Unknown'
        
    def to_string_with_article(tp):
        if tp == AbstractType.POSTER:
            return 'a poster'
        elif tp == AbstractType.PRESENTATION:
            return 'an oral communication'
        else:
            return 'unknown'


class Abstract(Base):
    __tablename__ = 'abstracts'
    id = Column(Integer, primary_key=True)
    title = Column(Text)
    abstract = Column(Text)
    abstract_type = Column(Integer)
    scientific_area = Column(String(50))
    keywords = Column(Text)
    owner = Column(ForeignKey('users.id'))
    submitted = Column(Boolean)
    submitted_on = Column(UtcDateTime())

    acceptance_status = Column(Integer)

    created = Column(UtcDateTime(), default=utcnow())
    modified = Column(UtcDateTime(), onupdate=utcnow())

    def __init__(self, owner, title=None, abstract=None, abstract_type=None, scientific_area='', keywords='', submitted=False, acceptance_status=0):
        self.title = title
        self.abstract = abstract
        self.abstract_type = abstract_type
        self.scientific_area = scientific_area
        self.keywords = keywords
        self.owner = owner
        self.submitted = submitted
        self.acceptance_status = acceptance_status

    def submit(self):
        self.submitted = True
        self.submitted_on = utcnow()

    def accept(self):
        self.submitted = True
        self.acceptance_status = 1
    
    def reject(self):
        self.submitted = True
        self.acceptance_status = 2
    
    def conditionally_accept(self):
        self.submitted = False
        self.acceptance_status = 3

    def undecide(self):
        self.submitted = True
        self.acceptance_status = 0

    def unsubmit(self):
        self.submitted = False
        self.acceptance_status = 0


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
