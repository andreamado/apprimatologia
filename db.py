from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import click

import sqlite3

conn = sqlite3.connect('test.db')
conn.close()

engine = create_engine('sqlite:///test.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()    

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    from . import models
    Base.metadata.create_all(bind=engine)

    news = models.News(
        title_pt = 'IX Congresso Ibérico de Primatologia', 
        title_en = 'IX Iberian Primatological Conference', 
        body_pt  = "APP is happy to announce the IX Iberian Primatological Conference. \
                    The conference will take place in Vila do Conde from **21 to 23 November** 2024. \
                    Registration will be available from mid-April. \
                    Stay tuned!", 
        body_en  =  "APP is happy to announce the IX Iberian Primatological Conference. \
                     The conference will take place in Vila do Conde from **21 to 23 November** 2024. \
                     Registration will be available from mid-April. \
                     Stay tuned!"
    )
    db_session.add(news)
    db_session.commit()

    click.echo('Initialized the database.')


# import sqlite3

# import click
# from flask import current_app, g


# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row

#     return g.db


# def close_db(e=None):
#     db = g.pop('db', None)

#     if db is not None:
#         db.close()


# def init_db():
#     db = get_db()

#     with current_app.open_resource('schema.sql') as f:
#         db.executescript(f.read().decode('utf8'))


# @click.command('init-db')
# def init_db_command():
#     """Clear the existing data and create new tables."""
#     init_db()
#     click.echo('Initialized the database.')


# def get_db():
#     if 'db' not in g:
#         g.db = sqlite3.connect(
#             current_app.config['DATABASE'],
#             detect_types=sqlite3.PARSE_DECLTYPES
#         )
#         g.db.row_factory = sqlite3.Row

#     return g.db


# def init_app(app):
#     app.teardown_appcontext(close_db)
#     app.cli.add_command(init_db_command)