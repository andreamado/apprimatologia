import os
from copy import deepcopy
import json

from flask import Flask, render_template, g, request
from flask_mail import Mail, Message

from dotenv import dotenv_values
config = dotenv_values(".env")

from flask_wtf.csrf import CSRFProtect

# check these options
import markdown

from .i18n import I18N

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        CSRF_SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'apprimatologia.sqlite'),
        RECAPTCHA_PUBLIC_KEY = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J",
        RECAPTCHA_PRIVATE_KEY = "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu",
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587, # SSL: 465
        MAIL_USE_TLS = True,
        # MAIL_USE_SSL = True,
        # MAIL_DEBUG = default app.debug,
        MAIL_USERNAME = config['MAIL_USERNAME'],
        MAIL_PASSWORD = config['MAIL_PASSWORD'],
        MAIL_DEFAULT_SENDER = config['MAIL_USERNAME']
        # MAIL_MAX_EMAILS = default None,
        # MAIL_SUPPRESS_SEND = default app.testing,
        # MAIL_ASCII_ATTACHMENTS = default False
    )

    # register the internationalization module
    I18N().register(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    app.mail = Mail(app)

    def send_email(subject, body, recipients):
        with app.app_context():
            msg = Message(subject, recipients=recipients, body=body)
            app.mail.send(msg)
    
    app.send_email = send_email

    # app.send_email('Test', 'tested!', ['9546585a-a072-4f83-bd69-8b230b4ec10e@8shield.net'])

    from .db import db_session
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

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
    @app.route('/<language:language>/APP')
    @app.route('/APP')
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

        from .models import News
        from sqlalchemy import select
        news_list = db_session.scalars(select(News).order_by(News.id.desc()).limit(5)).fetchall()

        g.news = []
        for news in news_list:
            g.news.append({
                'title': getattr(news, f'title_{language}'),
                'body': markdown.markdown(getattr(news, f'body_{language}'), tab_length=2),
                'date': news.created.strftime("%d/%m/%Y")
            })

        return render_template(
            'noticias.html', 
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
            lang=language
        )

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html") 

    from .db import init_db_command
    app.cli.add_command(init_db_command)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import member
    app.register_blueprint(member.bp)

    from . import IX_IPC
    IX_IPC.register(app)

    from .admission import register_admission
    register_admission(app)

    return app