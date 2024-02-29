import os
from flask import Flask, render_template, g

# check these options
import markdown
# md = markdown.Markdown()

from .db import get_db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'apprimatologia.sqlite'),
    )

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

    @app.route('/')
    def index():
        g.links[0]['active'] = True
        return render_template('index.html', background_monkey=True)

    @app.route('/noticias')
    def noticias():
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

        return render_template('noticias.html', background_monkey=False)

    @app.route('/eventos')
    def eventos():
        g.links[2]['active'] = True
        return render_template('eventos.html', background_monkey=False)

    @app.route('/contacto')
    def contacto():
        g.links[3]['active'] = True
        return render_template('contacto.html', background_monkey=True)

    @app.route('/membros')
    def membros():
        g.links[4]['active'] = True
        return render_template('membros.html', background_monkey=False)

    @app.errorhandler(404) 
    def not_found(e): 
        return render_template("404.html") 

    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    return app