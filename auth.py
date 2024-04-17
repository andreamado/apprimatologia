import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from email_validator import validate_email, EmailNotValidError

from .db import get_session
from .models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
@bp.route('/<language:language>/register', methods=('GET', 'POST'))
def register(language='pt'):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        try:
            emailinfo = validate_email(email, check_deliverability=False)
            email = emailinfo.normalized
        except EmailNotValidError as e:
            error = str(e)

        if error is None:
            with get_session() as db_session:
                try:
                    user = User(email, generate_password_hash(password))
                    db_session.add(user)
                    db_session.commit()
                except:
                    error = f"User {email} is already registered."
                else:
                    return redirect(url_for("auth.login", language=language))


        flash(error)

    g.background_monkey = True
    return render_template('auth/register.html', lang=language)


@bp.route('/login', methods=('GET', 'POST'))
@bp.route('/<language:language>/login')
def login(language='pt'):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        error = None

        with get_session() as db_session:
            user = db_session.execute(db_session.select(User).filter_by(email=email)).scalar_one()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('main_site.index', language=language))

        flash(error)

    return render_template(
        'auth/login.html', 
        background_monkey=True, 
        lang=language
    )


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        with get_session() as db_session:
            try:
                g.user = db_session.get(User, user_id)
            except:
                g.user = None

@bp.route('/logout')
@bp.route('/<language:language>/logout')
def logout(language='pt'):
    session.clear()
    return redirect(url_for('main_site.index', lang=language))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', language=kwargs['language']))

        return view(**kwargs)

    return wrapped_view


def register(app):
    app.register_blueprint(bp)