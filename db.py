from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base, Session
import click

import os, sqlite3

database_path = ''
if os.path.isdir('apprimatologia'):
    database_path = os.path.join('apprimatologia', 'apprimatologia.db')
else:
    database_path = 'apprimatologia.db'

conn = sqlite3.connect(database_path)
conn.close()

engine = create_engine('sqlite:///' + database_path)
_db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

Base = declarative_base()
Base.query = _db_session.query_property()

def get_session() -> Session:
    return Session(bind=engine)

@click.command('init-db')
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    
    from . import models
    Base.metadata.create_all(bind=engine)

    with get_session() as db_session:
        image_file = models.UploadedFile(
            original_name='pexels-egor-kamelev-802208_small.jpg',
            file_path='static/img/pexels-egor-kamelev-802208_small.jpg'
        )
        db_session.add(image_file)

        image = models.Image(
             image_file.id,
             subtitle_pt='APP is happy to announce the IX Iberian Primatological Conference.The conference will take place in Vila do Conde from **21 to 23 November** 2024. Registration will be available from mid-April.', 
             subtitle_en='APP is happy to announce the IX Iberian Primatological Conference.The conference will take place in Vila do Conde from **21 to 23 November** 2024. Registration will be available from mid-April.', 
             alt_pt=None, 
             alt_en=None
        )
        db_session.add(image)
        db_session.commit()

        news = models.News(
            title_pt = 'IX Congresso Ibérico de Primatologia', 
            title_en = 'IX Iberian Primatological Conference', 
            body_pt  = "APP is happy to announce the IX Iberian Primatological Conference. \
                        The conference will take place in Vila do Conde from 21 to 23 November 2024. \
                        Registration will be available from mid-April. \
                        Stay tuned!", 
            body_en  =  "APP is happy to announce the IX Iberian Primatological Conference. \
                        The conference will take place in Vila do Conde from 21 to 23 November 2024. \
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
                        Stay tuned!",
        image    =  image.id
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

        news = db_session.get(models.News, 3)
        news.title_pt = 'Notícia modificada'
        news.title_en = 'Modified news'

        db_session.commit()

    click.echo('Initialized the database.')
