from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base, Session

import click
import sqlite3, os

if os.path.isdir('apprimatologia'):
    database_path = os.path.join('instance', 'IXIPC.db')
else:
    database_path = 'IXIPC.db'

# makes sure IXIPC database file exists
conn = sqlite3.connect(database_path)
conn.close()

engine = create_engine('sqlite:///' + database_path)

def get_session() -> Session:
    """Returns an IX IPC database session"""

    return Session(bind=engine)

db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()
Base.query = db_session.query_property()

from . import models

def fill_database():
    with get_session() as db_session:
        # Zé Ninguém
        user1 = models.User(name='Zé Ninguém', email='jose.ninguem@nowhere.com', first_name='José', last_name='Ninguém', password='123456', institution='IGC', student=True)
        db_session.add(user1)
        db_session.commit()

        payment = models.Payment(user_id=user1.id, method=models.PaymentMethod.MBWay, method_id='55654546', value=35.00)
        db_session.add(payment)
        db_session.commit()

        payment.success(db_session)
        user1.payment_id = payment.id
        user1.paid_registration = True
        db_session.commit()

        abstract1 = models.Abstract(owner=user1.id, title='Fancy presentation', abstract='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', abstract_type=models.AbstractType.PRESENTATION, keywords='primate; big primate; small primate', submitted=True)
        db_session.add(abstract1)

        abstract = models.Abstract(owner=user1.id, title='Slightly nonsense poster', abstract='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', abstract_type=models.AbstractType.POSTER, keywords='primate; big primate; small primate', submitted=True)
        db_session.add(abstract)

        abstract = models.Abstract(owner=user1.id, title='Makes no sense at all', abstract='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.', abstract_type=models.AbstractType.POSTER, keywords='primate; big primate; small primate')
        db_session.add(abstract)


        author1 = models.Author(user1.id, first_name='José', last_name='Ninguém', email='jose.ninguem@nowhere.com', country='Portugal')
        author2 = models.Author(user1.id, first_name='Gertrudes', last_name='Silva', email='gs@nowhere.com', country='Australia')
        author3 = models.Author(user1.id, first_name='Joane', last_name='Doe', email='jd@nowhere.com', country='Spain')
        db_session.add_all([author1, author2, author3])
        db_session.commit()

        abstract_author1 = models.AbstractAuthor(author1.id, abstract1.id, order=0, presenter=False)
        abstract_author2 = models.AbstractAuthor(author2.id, abstract1.id, order=1, presenter=True)
        abstract_author3 = models.AbstractAuthor(author3.id, abstract1.id, order=2, presenter=False)
        db_session.add_all([abstract_author1, abstract_author2, abstract_author3])
        db_session.commit()


        # Bonifácio Madureira
        user2 = models.User(name='Bonifácio Madureira', email='bmadureira@sapo.pt', first_name='Bonifácio', last_name='Madureira', password='123456', institution='CIBIO', student=False)
        db_session.add(user2)
        db_session.commit()

        payment = models.Payment(user_id=user2.id, method=models.PaymentMethod.Card, method_id='55654546', value=50.00)
        db_session.add(payment)
        db_session.commit()

        payment.success(db_session)
        user2.payment_id = payment.id
        user2.paid_registration = True
        db_session.commit()


        # Manuel Esteves
        user3 = models.User(name='Manuel Esteves', email='esteves@cabeca.lua', first_name='Manuel', last_name='Esteves', password='123456', institution='Lua')
        db_session.add(user3)
        db_session.commit()

        payment = models.Payment(user_id=user3.id, method=models.PaymentMethod.Card, method_id='55654546', value=50.00)
        db_session.add(payment)
        db_session.commit()

        user3.payment_id = payment.id
        db_session.commit()

@click.command('init-IXIPC-db')
def init_IXIPC_db_command():
    """Clears the existing data and create new tables."""

    Base.metadata.create_all(bind=engine)

    click.echo('Initialized the IX IPC database.')


@click.command('fill-IXIPC-db')
def fill_IXIPC_db_command():
    """Fills IX IPC database with some dummy data."""

    fill_database()

    click.echo('IX IPC database filled with dummy data.')


@click.command('IXIPC-organizer')
@click.argument('id')
@click.option('--add/--remove', default=False)
def set_IXIPC_organizer(id, set):
    """Adds/removes a user from organizers"""

    with get_session() as db_session:
        user = db_session.get(models.User, id)
        if set:
            user.organizer = True
            click.echo(f'User {user.name} (id {user.id}) added to organizers')
        else:
            user.organizer = False
            click.echo(f'User {user.name} (id {user.id}) removed from organizers')

        db_session.commit()

        
