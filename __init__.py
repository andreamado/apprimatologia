import os, threading, json
from copy import deepcopy
from uuid import UUID
from dotenv import dotenv_values

from flask import Flask, render_template, g, request, send_from_directory
from flask_mail import Mail, Message
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import select

from .i18n import I18N
from .models import UploadedFile
from .db import get_session, init_db_command
from .auth import login_required, bp as auth_bp

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def create_app(test_config=None):
    """Creates and configures the app"""

    app = Flask(__name__, instance_relative_config=True)

    config = dotenv_values(os.path.join(app.root_path, '.env'))

    app.config.from_mapping(
        SECRET_KEY='dev',
        CSRF_SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'apprimatologia.db'),
        DATABASE_IXIPC=os.path.join(app.instance_path, 'IXIPC.db'),
        RECAPTCHA_PUBLIC_KEY = config['RECAPTCHA_PUBLIC_KEY'],
        RECAPTCHA_PRIVATE_KEY = config['RECAPTCHA_PRIVATE_KEY'],
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
        UPLOAD_FOLDER = 'uploaded_files',
        MBWAY_KEY = config['MBWAY_KEY'],
        ANTI_PHISHING_KEY = config['ANTI_PHISHING_KEY'],
        MAINTENANCE_EMAIL = config['MAINTENANCE_EMAIL']
    )

    # register the internationalization module
    I18N(app)

    # register the csrf protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # register the email methods
    app.mail = Mail(app)

    def send_email(subject: str, body: str, recipients: list[str]) -> None:
        def _send_email():
            with app.app_context():
                msg = Message(subject, recipients=recipients, body=body)
                app.mail.send(msg)
                # TODO: log the emails
                print(f'Email sent to {recipients}.')
        t1 = threading.Thread(target=_send_email, name="email")
        t1.start()
    
    app.send_email = send_email

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

    @app.before_request
    def add_links():
        """Adds the links the request context"""

        g.links = deepcopy(links)


    def allowed_file(filename: str) -> bool:
        """Helper function to validate file extension"""

        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @login_required
    @app.route('/upload_file/', methods=['POST'])
    def upload_file():
        """Uploads a file
        
        Saves a file locally and adds it to the database, returning file name 
        and id or an error message.
        """

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
        description = \
          request.form['description'].strip() \
            if 'description' in request.form \
            else None
        
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
        """Sends a file from the upload directory"""

        # TODO: add verification that the file can be openly accessed
        return send_from_directory('uploaded_files', str(id))


    @app.route("/remove_file", methods=['POST'])
    def remove_file():
        """Removes a file from the uploaded files
        
        Mark a file as removed in the database and move it to the deleted files
        folder.
        """

        if 'id' in request.form:
            id = request.form['id']
        else:
            # TODO: Correct this error
            return json.dumps({'error': 'no file uploaded'}), 400

        with get_session() as db_session:
            file = db_session.execute(
                select(UploadedFile).filter_by(id=UUID(id))
            ).scalar_one()

            if not file.deleted:
                try:
                    file.delete()
                except:
                    db_session.rollback()
                    return 'unable to remove file', 500
                else:
                    db_session.commit()

        return json.dumps({}), 204


    @app.errorhandler(404)
    def not_found(e):
        """Returns page not found"""

        return render_template("404.html")


    app.cli.add_command(init_db_command)

    app.register_blueprint(auth_bp)
    
    from . import member
    app.register_blueprint(member.bp)

    from . import main_site
    main_site.register(app)

    from . import IX_IPC
    IX_IPC.register(app)

    from .admission import register_admission
    register_admission(app)

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

    return app

if __name__ == '__main__':
    import waitress
    waitress.serve(create_app, port=5000, url_scheme='https')