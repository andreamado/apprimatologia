import os
import threading
from copy import deepcopy
import json

from uuid import UUID

from flask import Flask, render_template, g, request, url_for, send_from_directory
from flask_mail import Mail, Message

from sqlalchemy import select

from dotenv import dotenv_values

from flask_wtf.csrf import CSRFProtect

# check these options
import markdown

from .i18n import I18N
from .models import UploadedFile, Image
from .db import get_session

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    config = dotenv_values(os.path.join(app.root_path, '.env'))

    app.config.from_mapping(
        SECRET_KEY='dev',
        CSRF_SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'apprimatologia.sqlite'),
        DATABASE_IXIPC=os.path.join(app.instance_path, 'IX_IPC.sqlite'),
        RECAPTCHA_PUBLIC_KEY = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J",
        RECAPTCHA_PRIVATE_KEY = "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu",
        MAIL_SERVER = 'smtp.gmail.com',
        MAIL_PORT = 587, # SSL: 465
        MAIL_USE_TLS = True,
        # MAIL_USE_SSL = True,
        # MAIL_DEBUG = default app.debug,
        MAIL_USERNAME = config['MAIL_USERNAME'],
        MAIL_PASSWORD = config['MAIL_PASSWORD'],
        MAIL_DEFAULT_SENDER = config['MAIL_USERNAME'],
        # MAIL_MAX_EMAILS = default None,
        # MAIL_SUPPRESS_SEND = default app.testing,
        # MAIL_ASCII_ATTACHMENTS = default False
        UPLOAD_FOLDER = 'uploaded_files'
    )

    # register the internationalization module
    I18N(app)

    csrf = CSRFProtect()
    csrf.init_app(app)

    app.mail = Mail(app)

    def send_email(subject, body, recipients):
        def _send_email():
            with app.app_context():
                msg = Message(subject, recipients=recipients, body=body)
                app.mail.send(msg)
                print(f'Email sent to {recipients}.')
        t1 = threading.Thread(target=_send_email, name="email")
        t1.start()
    
    app.send_email = send_email

    # @app.teardown_appcontext
    # def shutdown_session(exception=None):
    #     db_session.remove()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile(os.path.join(app.root_path, 'config.py'), silent=True)
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

    @app.route('/noticias/<language:language>')
    @app.route('/noticias/')
    def noticias(language='pt'):
        g.links[1]['active'] = True

        from .models import News
        from sqlalchemy import select
        with get_session() as db_session:
            news_list = db_session.scalars(select(News).order_by(News.id.desc()).limit(5)).fetchall()

            g.news = []
            for news in news_list:
                aaa = None
                if news.image:
                    aaa = db_session.get(Image, news.image).to_object(language)
                    print(aaa['id'])

                g.news.append({
                    'title': getattr(news, f'title_{language}'),
                    'body': markdown.markdown(getattr(news, f'body_{language}'), tab_length=2),
                    'date': news.created.strftime("%d/%m/%Y"),
                    'modified': news.modified.strftime("%d/%m/%Y") if news.modified else None,
                    'image': aaa
                })

            return render_template(
                'noticias.html', 
                lang=language,
                text_column=True
            )

    @app.route('/contacto/<language:language>')
    @app.route('/contacto/')
    def contacto(language='pt'):
        g.links[3]['active'] = True
        return render_template(
            'contacto.html', 
            background_monkey=True, 
            lang=language
        )

    @app.route('/membros/<language:language>')
    @app.route('/membros/')
    def membros(language='pt'):
        g.links[4]['active'] = True
        return render_template(
            'membros.html', 
            lang=language
        )


    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @app.route('/upload_file/', methods=['POST'])
    def upload_file():
        if 'file' in request.files:
            f = request.files['file']
        elif 'file' in request.form:
            f = request.form['file']
        else:
            return json.dumps({'error': 'no file uploaded'}), 400 

        if f.filename == '':
            return json.dumps({'error': 'no selected file'}), 400

        if not allowed_file(f.filename):
            return json.dumps({'error': 'file type not allowed'}), 415

        #TODO: sanitize the description
        description = request.form['description'] if 'description' in request.form else None
        
        with get_session() as db_session:
            file = UploadedFile(f.filename, description, g.user)
            try:
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], str(file.id)))
            except:
                return json.dumps({'error': 'upload failed'}), 500
            else:
                db_session.add(file)
                db_session.commit()

            return json.dumps({
                'id': f'{file.id}',
                'name': f'{file.original_name}'
            }), 200

    @app.route("/get_file/<uuid:id>")
    # TODO: find a more performant method
    # https://tedboy.github.io/flask/generated/flask.send_from_directory.html
    def get_file(id):
        return send_from_directory('uploaded_files', str(id))

    @app.route("/remove_file", methods=['POST'])
    def remove_file():
        if 'id' in request.form:
            id = request.form['id']
        else:
            # Correct this error
            return json.dumps({'error': 'no file uploaded'}), 400

        with get_session() as db_session:
            file = db_session.execute(select(UploadedFile).filter_by(id=UUID(id))).scalar_one()
            if not file.deleted:
                try:
                    file.delete()
                except:
                    db_session.rollback()
                    return 'unable to remove file', 500
                else:
                    db_session.commit()

        return '', 204


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

if __name__ == '__main__':
    import waitress
    waitress.serve(create_app, port=5000, url_scheme='https')