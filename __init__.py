import os, json, re
from copy import deepcopy
from dotenv import dotenv_values

from flask import Flask, render_template, g, request
from flask_wtf.csrf import CSRFProtect

from .i18n import I18N
from .db import init_db_command
from . import auth

from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(test_config=None):
    """Creates and configures the app"""

    app = Flask(
        __name__, 
        instance_relative_config=True, 
    )

    config = dotenv_values(os.path.join(app.root_path, '.env'))

    app.config.from_mapping(
        SECRET_KEY=config['SECRET_KEY'],
        CSRF_SECRET_KEY=config['CSRF_SECRET_KEY'],
        DATABASE=os.path.join(app.instance_path, 'apprimatologia.db'),
        DATABASE_IXIPC=os.path.join(app.instance_path, 'IXIPC.db'),
        RECAPTCHA_PUBLIC_KEY = config['RECAPTCHA_PUBLIC_KEY'],
        RECAPTCHA_PRIVATE_KEY = config['RECAPTCHA_PRIVATE_KEY'],
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587, # SSL: 465
        MAIL_USE_TLS = True,
        # SERVER_NAME = config['SERVER_NAME'],
        # MAIL_USE_SSL = True,
        # MAIL_DEBUG = default app.debug,
        MAIL_USERNAME = config['MAIL_USERNAME'],
        MAIL_PASSWORD = config['MAIL_PASSWORD'],
        MAIL_DEFAULT_SENDER = config['MAIL_USERNAME'],
        IMAP_URL = 'imap.gmail.com',
        # MAIL_MAX_EMAILS = default None,
        # MAIL_SUPPRESS_SEND = default app.testing,
        # MAIL_ASCII_ATTACHMENTS = default False
        UPLOAD_FOLDER = os.path.join(app.root_path, 'uploaded_files'),
        MBWAY_KEY = config['MBWAY_KEY'],
        CCARD_KEY = config['CCARD_KEY'],
        ANTI_PHISHING_KEY = config['ANTI_PHISHING_KEY'],
        MAINTENANCE_EMAIL = config['MAINTENANCE_EMAIL'],
        IXIPC_MANAGER_PASSWORD = config['IXIPC_MANAGER_PASSWORD']
    )

    # register the internationalization module
    I18N(app)

    # register the csrf protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    from . import email
    email.register(app)

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db_session.remove()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile(
            os.path.join(app.root_path, 'config.py'), 
            silent=True
        )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with open(os.path.join(app.root_path, 'links.json'), encoding='utf8') as f:
        links = json.load(f)

    pattern_en = re.compile(r"/en/|/en$")
    pattern_pt = re.compile(r"/pt/|/pt$")
    @app.before_request
    def add_links():
        """Adds the links the request context"""

        g.links = deepcopy(links)

        url = request.url

        match_pt = pattern_pt.search(url)
        match_en = pattern_en.search(url)

        g.current_lang = 'en' if match_en else 'pt'
        if g.current_lang == 'pt':
            g.url_pt = url
            if not match_pt:
                g.url_en = url + '/en'
            else:
                g.url_en = pattern_pt.sub(r'/en/', url, count=1)

            if g.url_en[-1] == '/':
                g.url_en = g.url_en[:-1]
        else:
            g.url_en = url
            g.url_pt = pattern_en.sub(r'/pt/', url, count=1)

            if g.url_pt[-1] == '/':
                g.url_pt = g.url_pt[:-1]

    @app.errorhandler(404)
    def not_found(e):
        """Returns page not found"""

        return render_template("404.html")


    app.cli.add_command(init_db_command)

    auth.register(app)
    
    from . import member
    member.register(app)

    from . import main_site
    main_site.register(app)

    from . import IX_IPC
    IX_IPC.register(app)

    from . import admission
    admission.register(app)

    from . import files
    files.register(app)

    # word counter filter
    def word_counter_generator(separator=None):
      def word_counter(s: str|None):
          if s:
              s = s.strip().split(separator)
              s = list(filter(lambda x: len(x.strip()) > 0, s))
              return len(s)
          else:
              return 0
      return word_counter

    app.jinja_env.filters['word_counter'] = word_counter_generator()
    app.jinja_env.filters['keyword_counter'] = word_counter_generator(';')

    # app.wsgi_app = ProxyFix(
    #     app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    # )
    return app

# if __name__ == '__main__':
#     import waitress
#     waitress.serve(
#         create_app, 
#         port=5000, 
#         url_scheme='https'
#     )