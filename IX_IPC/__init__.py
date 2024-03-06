from flask import flash, render_template, redirect, url_for, Blueprint, g, request, session
from flask import current_app as app
from email_validator import validate_email, EmailNotValidError

from .db_IXIPC import db_session
from .models import User

from flask_wtf import FlaskForm

from sqlalchemy import select

bp = Blueprint('IX_IPC', __name__, template_folder='templates')


@bp.route('/<language:language>/eventos/')
@bp.route('/eventos/')
@bp.route('/<language:language>/IX_IPC')
@bp.route('/IX_IPC')
@bp.route('/<language:language>/IPC')
@bp.route('/IPC')
@bp.route('/<language:language>/IX_Iberian_Primatological_Conference')
@bp.route('/IX_Iberian_Primatological_Conference')
def IXIPC(language='pt'):
    g.links[2]['active'] = True

    return render_template(
        'IX_IPC.html',
        lang=language,
        form=FlaskForm()
    )


@bp.route('/<language:language>/IX_IPC/register', methods=['POST'])
def register_user(language):
    g.links[2]['active'] = True

    name = request.form['first-name']
    email = request.form['email']
    error = None

    if not email:
        error = 'Email is required.'
    elif not name:
        error = 'Name is required.'

    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
    except EmailNotValidError as e:
        error = str(e)

    if error is None:
        try:
            user = User(name, email)
            db_session.add(user)
            db_session.commit()
            session['IXIPC_user_id'] = user.id
        except:
            error = f"{email} is already registered."
        else:
            try:
                app.send_email(
                    'Bem-vindo/a ao Congresso Ibérico de Primatologia!', 
                    f'Olá {name},\n\nBem-vindo/a ao Congresso Ibérico de Primatologia!\nO teu username é este email ({email}) tua password é {user.password}. Usa estes dados no site para alterar a tua inscrição e submeter candidaturas a posters e apresentações orais.\n\nEsperamos ver-te em breve!',
                    [email]
                )
            except:
                error = f"Could not send email {email}."
            else:
                return redirect(url_for("IX_IPC.IXIPC", language=language))

    flash(error)
    return redirect(url_for("IX_IPC.IXIPC", language=language))


@bp.route('/<language:language>/IX_IPC/login', methods=['POST'])
def login(language):
    email = request.form['email']
    password = request.form['password']
    error = None

    user = db_session.execute(select(User).filter_by(email=email)).scalar_one()

    if user is None:
        error = 'Incorrect email.'
    elif user.password != password:
        error = 'Incorrect password.'

    if error is None:
        session.clear()
        session['IXIPC_user_id'] = user.id
        return redirect(url_for('IX_IPC.IXIPC', language=language))

    flash(error)
    return redirect(url_for('IX_IPC.IXIPC', language=language))


@bp.route('/<language:language>/IX_IPC/logout', methods=['POST'])
def logout(language):
    session.clear()
    return redirect(url_for('IX_IPC.IXIPC', language=language))


@bp.before_app_request
def load_logged_in_IXIPC_user():
    user_IXIPC_id = session.get('IXIPC_user_id')
    if user_IXIPC_id is None:
        g.IXIPC_user = None
    else:
        g.IXIPC_user = db_session.get(User, user_IXIPC_id)


def register(app):
    app.register_blueprint(bp)

    from .db_IXIPC import init_IX_IPC_db_command
    app.cli.add_command(init_IX_IPC_db_command)
