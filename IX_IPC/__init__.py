from flask import flash, render_template, redirect, url_for, Blueprint, g, request, session
from flask import current_app as app
from email_validator import validate_email, EmailNotValidError

from .db_IXIPC import db_session
from .models import User

from flask_wtf import FlaskForm

from sqlalchemy import select

bp = Blueprint('IX_IPC', __name__, template_folder='templates')


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

@bp.route('/<language:language>/IX_IPC/register', methods=['POST'])
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
            finally:
                db_session.close()
        else:
            flash('Email not valid', 'warning')

    return redirect(url_for("IX_IPC.IXIPC", language=language))


@bp.route('/<language:language>/IX_IPC/recover_credentials/<string:email>')
def recover_credentials(language, email):
    email = sanitize_email(email)
    if email:
        try:
            user = db_session.execute(select(User).filter_by(email=email)).scalar_one()
            app.send_email(
                'Bem-vindo/a ao Congresso Ibérico de Primatologia!', 
                f'Olá {user.name},\n\nBem-vindo/a ao Congresso Ibérico de Primatologia!\nO teu username é este email ({email}) tua password é {user.password}. Usa estes dados no site para alterar a tua inscrição e submeter candidaturas a posters e apresentações orais.\n\nEsperamos ver-te em breve!',
                [email]
            )
            flash('We have sent you the login credentials again! If you don\'t seen them in you inbox within a few minutes, please check you spam box.', 'success')
        finally:
            db_session.close()
    else:
        flash('Invalid email.', 'warning')
    return redirect(url_for("IX_IPC.IXIPC", language=language))


@bp.route('/<language:language>/IX_IPC/login', methods=['POST'])
def login(language):
    email = request.form['email']
    password = request.form['password']
    error = None

    try:
        user = db_session.execute(select(User).filter_by(email=email)).scalar_one()
    finally:
        db_session.close()

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
        try:
            g.IXIPC_user = db_session.get(User, user_IXIPC_id)
        except:
            g.IXIPC_user = None
        finally:
            db_session.close()



def register(app):
    app.register_blueprint(bp)

    from .db_IXIPC import init_IX_IPC_db_command
    app.cli.add_command(init_IX_IPC_db_command)
