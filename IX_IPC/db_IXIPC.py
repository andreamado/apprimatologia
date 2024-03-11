from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import click

import sqlite3

conn = sqlite3.connect('IX_IPC.db')
conn.close()

engine = create_engine('sqlite:///IX_IPC.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()    

@click.command('init-IXIPC-db')
def init_IX_IPC_db_command():
    """Clear the existing data and create new tables."""
    from . import models
    Base.metadata.create_all(bind=engine)

    db_session.commit()
    db_session.close_all()

    click.echo('Initialized the IX IPC database.')
