from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base, Session
import click

import sqlite3

# makes sure IXIPC database file exists
conn = sqlite3.connect('IXIPC.db')
conn.close()

engine = create_engine('sqlite:///IXIPC.db')

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

@click.command('init-IXIPC-db')
def init_IXIPC_db_command():
    """Clears the existing data and create new tables."""

    from . import models
    with get_session() as db_session:
        Base.metadata.create_all(bind=engine)
        db_session.commit()

        click.echo('Initialized the IX IPC database.')
