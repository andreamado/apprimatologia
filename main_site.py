from flask import Blueprint, g, render_template
from .models import Image, Profile
from .db import get_session

from sqlalchemy import select

import markdown


bp = Blueprint('main_site', __name__, template_folder='templates')


@bp.route('/<language:language>/')
@bp.route('/')
def index(language='pt'):
    """Main page"""

    g.links[0]['active'] = True

    return render_template(
        'index.html', 
        background_monkey=True,
        lang=language,
    )


@bp.route('/noticias/<language:language>')
@bp.route('/noticias/')
def noticias(language='pt'):
    """News page"""
    # TODO: implement pagination for extra news

    g.links[1]['active'] = True

    from .models import News
    from sqlalchemy import select
    with get_session() as db_session:
        news_list = db_session.scalars(
            select(News)
            .order_by(News.id.desc())
            .limit(5)
        ).fetchall()

        g.news = []
        for news in news_list:
            image = None
            if news.image:
                image = db_session.get(Image, news.image).to_object(language)

            g.news.append({
                'title': getattr(news, f'title_{language}'),
                'body': markdown.markdown(getattr(news, f'body_{language}'), tab_length=2),
                'date': news.created.strftime("%d/%m/%Y"),
                'modified': news.modified.strftime("%d/%m/%Y") if news.modified else None,
                'image': image
            })

        return render_template(
            'noticias.html', 
            lang=language,
            text_column=True
        )


@bp.route('/contacto/<language:language>')
@bp.route('/contacto/')
def contacto(language='pt'):
    """Contacts page"""

    g.links[3]['active'] = True
    return render_template(
        'contacto.html', 
        background_monkey=True, 
        lang=language
    )


@bp.route('/membros/<language:language>')
@bp.route('/membros/')
def membros(language='pt'):
    """Members page"""

    g.links[4]['active'] = True

    with get_session() as db_session:
        direction = db_session.execute(
            select(Profile)
              .where(Profile.direction == True)
              .order_by(Profile.name)
        ).scalars()

        return render_template(
            'membros.html',
            direction=direction,
            lang=language
        )


def register(app) -> None:
    """Registers the main site blueprint with the Flask app"""

    app.register_blueprint(bp)
