from flask import flash, render_template, redirect, url_for, Blueprint, g, request, session
from flask import current_app as app
from email_validator import validate_email, EmailNotValidError

from .db_IXIPC import get_session
from .models import User, Abstract, AbstractType

from flask_wtf import FlaskForm

from sqlalchemy import select

import json

bp = Blueprint('IX_IPC', __name__, template_folder='templates')


@bp.route('/IX_IPC/<language:language>')
@bp.route('/IX_IPC')
@bp.route('/IPC/<language:language>')
@bp.route('/IPC')
@bp.route('/IX_Iberian_Primatological_Conference/<language:language>')
@bp.route('/IX_Iberian_Primatological_Conference')
def IXIPC(language='pt'):
    g.links[2]['active'] = True

    if g.IXIPC_user:
        with get_session() as db_session:
            g.abstract = db_session.execute(select(Abstract).filter_by(owner=g.IXIPC_user.id)).scalar_one_or_none()
    
    return render_template(
        'IX_IPC.html',
        lang=language,
        form=FlaskForm(),
        text_column=True
    )

def sanitize_email(email: str) -> str|None:
    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
    except EmailNotValidError as e:
        return None
    return email

@bp.route('/IX_IPC/register/<language:language>', methods=['POST'])
def register_user(language):
    g.links[2]['active'] = True

    name = request.form['first-name']
    email = request.form['email']

    if not email:
        flash('Email is required.', 'warning')
    elif not name:
        flash('Name is required.', 'warning')
    else:
        email = sanitize_email(email)
        if email:
            with get_session() as db_session:
                try:
                    user = User(name, email)
                    db_session.add(user)
                    db_session.commit()
                    session['IXIPC_user_id'] = user.id
                except:
                    flash(
                        app.i18n.l10n[language].format_value(
                            'IXIPC-email-already-registered', {
                                'email': email, 
                                'recover_credentials': url_for('IX_IPC.recover_credentials', language=language, email=email)
                            }
                        ), 'warning'
                    )
                else:
                    try:
                        app.send_email(
                            'Bem-vindo/a ao Congresso Ibérico de Primatologia!', 
                            f'Olá {name},\n\nBem-vindo/a ao Congresso Ibérico de Primatologia!\nO teu username é este email ({email}) tua password é {user.password}. Usa estes dados no site para alterar a tua inscrição e submeter candidaturas a posters e apresentações orais.\n\nEsperamos ver-te em breve!',
                            [email]
                        )
                    except:
                        flash(f"Could not send email {email}. Please contact the organization.", 'warning')
                    else:
                        flash('Your account was successfully created! You can proceed with an abstract submission now or login again later with the credentials sent to your email.', 'success')
                        return redirect(url_for("IX_IPC.IXIPC", language=language))
        else:
            flash('Email not valid', 'warning')

    return redirect(url_for("IX_IPC.IXIPC", language=language))


@bp.route('/IX_IPC/recover_credentials/<language:language>/<string:email>')
def recover_credentials(language, email):
    email = sanitize_email(email)
    if email:
        with get_session() as db_session:
            user = db_session.execute(select(User).filter_by(email=email)).scalar_one()
            app.send_email(
                'Bem-vindo/a ao Congresso Ibérico de Primatologia!', 
                f'Olá {user.name},\n\nBem-vindo/a ao Congresso Ibérico de Primatologia!\nO teu username é este email ({email}) tua password é {user.password}. Usa estes dados no site para alterar a tua inscrição e submeter candidaturas a posters e apresentações orais.\n\nEsperamos ver-te em breve!',
                [email]
            )
            flash('We have sent you the login credentials again! If you don\'t seen them in you inbox within a few minutes, please check you spam box.', 'success')
    else:
        flash('Invalid email.', 'warning')
    return redirect(url_for("IX_IPC.IXIPC", language=language))


@bp.route('/IX_IPC/login/<language:language>', methods=['POST'])
def login(language):
    email = request.form['email']
    password = request.form['password']
    error = None

    with get_session() as db_session:
        user = db_session.execute(select(User).filter_by(email=email)).scalar_one()

    if user is None:
        error = 'Incorrect email.'
    elif user.password != password:
        error = 'Incorrect password.'

    if error is None:
        session.clear()
        session['IXIPC_user_id'] = user.id
        return redirect(url_for('IX_IPC.IXIPC', language=language))

    flash(error, 'warning')
    return redirect(url_for('IX_IPC.IXIPC', language=language))


@bp.route('/IX_IPC/logout/<language:language>', methods=['POST'])
def logout(language):
    session.clear()
    return redirect(url_for('IX_IPC.IXIPC', language=language))


@bp.before_app_request
def load_logged_in_IXIPC_user():
    user_IXIPC_id = session.get('IXIPC_user_id')
    if user_IXIPC_id is None:
        g.IXIPC_user = None
    else:
        try:
            with get_session() as db_session:
                g.IXIPC_user = db_session.get(User, user_IXIPC_id)
        except:
            g.IXIPC_user = None

@bp.route('/IX_IPC/save_abstract', methods=['POST'])
def save_abstract():
    print(request)
    with get_session() as db_session:
        abstract = None
        if 'abstract-id' in request.form and len(request.form['abstract-id']) > 0:
            id = int(request.form['abstract-id'])
            abstract = db_session.get(Abstract, id)
        else:
            abstract = Abstract(owner=g.IXIPC_user.id)
            db_session.add(abstract)


        # TODO: Sanitize input!
        if 'title' in request.form:
            abstract.title = request.form['title']

        if 'abstract-body' in request.form:
            abstract.abstract = request.form['abstract-body']

        if 'abstract_type' in request.form:
            abstract_type = request.form['abstract_type']
            if abstract_type == 'poster':
                abstract.abstract_type = AbstractType.POSTER
            elif abstract_type == 'presentation':
                abstract.abstract_type = AbstractType.PRESENTATION

        db_session.commit()

        return json.dumps({'id': abstract.id}), 200

def register(app):
    app.register_blueprint(bp)

    from .db_IXIPC import init_IX_IPC_db_command
    app.cli.add_command(init_IX_IPC_db_command)
