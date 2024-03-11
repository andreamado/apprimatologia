from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
import click

import sqlite3
import os

database_path = ''
if os.path.isdir('apprimatologia'):
    database_path = os.path.join('apprimatologia', 'test.db')
else:
    database_path = 'test.db'

print('sqlite:///' + database_path)

conn = sqlite3.connect(database_path)
conn.close()

engine = create_engine('sqlite:///' + database_path)
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

    member = models.Member(given_name='Zé', family_name='Chimp', number=1, species='Homo Sapiens')
    db_session.add(member)

    member = models.Member(given_name='Tânia', family_name='Minhós', number=2, species='Colobo Vermelho')
    db_session.add(member)

    member = models.Member(given_name='Filipa', family_name='Borges', number=3, species='Chimpanzé')
    db_session.add(member)

    db_session.commit()
    db_session.close_all()

    click.echo('Initialized the database.')
