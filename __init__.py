import os
from copy import deepcopy
import json

from flask import Flask, render_template, g

# check these options
import markdown

from .db import get_db

from .i18n import I18N

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'apprimatologia.sqlite'),
    )

    # register the internationalization module
    I18N().register(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with open('links.json', encoding='utf8') as f:
        links = json.load(f)

    @app.before_request
    def add_links():
        g.links = deepcopy(links)

    @app.route('/<language:language>/')
    @app.route('/')
    def index(language='pt'):
        g.links[0]['active'] = True

        return render_template(
            'index.html', 
            background_monkey=True,
            lang=language,
        )

    @app.route('/<language:language>/noticias/')
    @app.route('/noticias/')
    def noticias(language='pt'):
        g.links[1]['active'] = True

        db = get_db()
        news_list = db.execute(
            'SELECT * FROM news ORDER BY id DESC LIMIT 10'
        )

        g.news = []
        for news in news_list:
            g.news.append({
                'title': news['title'],
                # 'body': md.convert(news['body']),
                'body': markdown.markdown(news['body'], tab_length=2),
                'date': f'Published on {news["created"].strftime("%d/%m/%Y")}'
            })

        return render_template(
            'noticias.html', 
            background_monkey=False, 
            lang=language
        )

    @app.route('/<language:language>/eventos/')
    @app.route('/eventos/')
    def eventos(language='pt'):
        g.links[2]['active'] = True
        return render_template(
            'eventos.html', 
            background_monkey=False, 
            lang=language
        )

    @app.route('/<language:language>/contacto/')
    @app.route('/contacto/')
    def contacto(language='pt'):
        g.links[3]['active'] = True
        return render_template(
            'contacto.html', 
            background_monkey=True, 
            lang=language
        )

    @app.route('/<language:language>/membros/')
    @app.route('/membros/')
    def membros(language='pt'):
        g.links[4]['active'] = True
        return render_template(
            'membros.html', 
            background_monkey=False, 
            lang=language
        )

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html") 

    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    return app