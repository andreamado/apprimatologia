from flask import flash, render_template, redirect, url_for, Blueprint, g, request, session
from flask import current_app as app
from email_validator import validate_email, EmailNotValidError

from .db_IXIPC import get_session
from .models import User, Abstract, AbstractType, Author, AbstractAuthor

from flask_wtf import FlaskForm

from sqlalchemy import select, delete, update

import json

bp = Blueprint('IX_IPC', __name__, template_folder='templates')

import functools
def login_IXIPC_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.IXIPC_user is None:
            return redirect(url_for('IX_IPC.IXIPC', language=kwargs['language']))

        return view(**kwargs)

    return wrapped_view



@bp.route('/IX_IPC/<language:language>')
@bp.route('/IX_IPC')
@bp.route('/IPC/<language:language>')
@bp.route('/IPC')
@bp.route('/IX_Iberian_Primatological_Conference/<language:language>')
@bp.route('/IX_Iberian_Primatological_Conference')
def IXIPC(language='pt'):
    g.links[2]['active'] = True

    with get_session() as db_session:
        abstracts = []
        if g.IXIPC_user:
            abstracts = db_session.execute(select(Abstract).filter_by(owner=g.IXIPC_user.id)).scalars()

        return render_template(
            'IX_IPC.html',
            lang=language,
            form=FlaskForm(),
            text_column=True,
            abstracts=abstracts,
            site_map=True
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


@login_IXIPC_required
@bp.route('/IX_IPC/create_abstract/<language:language>', methods=['POST'])
def create_new_abstract(language='pt'):
    id = json.loads(save_abstract_local(None, g))['id']
    return load_closed_abstract(id, language), 200


@login_IXIPC_required
@bp.route('/IX_IPC/closed_abstract/<language:language>', methods=['POST'])
def closed_abstract(language='pt'):
    id = request.form['abstract-id']
    return load_closed_abstract(id, language), 200


def load_closed_abstract(id, language):
    with get_session() as db_session:
        abstract = db_session.get(Abstract, id)
        
        return json.dumps({
            'id': id,
            'html': render_template(
                'abstract-form-closed.html',
                abstract = abstract,
                csrf_token = request.form['csrf_token'],
                reload=True,
                lang=language
            )})


@login_IXIPC_required
@bp.route('/IX_IPC/delete_abstract', methods=['POST'])
def delete_abstract():
    with get_session() as db_session:
        id = request.form['abstract-id']

        abstract = db_session.get(Abstract, id)
        delete_abstract_authors = delete(AbstractAuthor).where(AbstractAuthor.abstract_id == id)
        if g.IXIPC_user.id == abstract.owner:
            try:
                db_session.delete(abstract)
                db_session.execute(delete_abstract_authors)
                db_session.commit()
            except:
                return '', 500
            return '', 204
        return '', 400


def save_abstract_local(form, g):
    with get_session() as db_session:
        abstract = None
        if form and 'abstract-id' in form and len(form['abstract-id']) > 0:
            id = int(form['abstract-id'])
            abstract = db_session.get(Abstract, id)
        else:
            abstract = Abstract(owner=g.IXIPC_user.id)
            db_session.add(abstract)

        # TODO: Sanitize input!
        if form:
            if 'title' in form:
                abstract.title = form['title']

            if 'abstract-body' in form:
                abstract.abstract = form['abstract-body']

            if 'abstract_type' in form:
                abstract_type = form['abstract_type']
                if abstract_type == 'poster':
                    abstract.abstract_type = AbstractType.POSTER
                elif abstract_type == 'presentation':
                    abstract.abstract_type = AbstractType.PRESENTATION
        else:
            abstract.title = ''
            abstract.abstract = ''
            abstract.abstract_type = AbstractType.POSTER

        db_session.commit()

        return json.dumps({'id': abstract.id})


@login_IXIPC_required
@bp.route('/IX_IPC/load_abstract/<language:language>/', methods=['POST'])
def load_abstract(language, id=None, csrf_token = None):
    if not id:
        id = request.form['abstract-id']
    
    if not csrf_token:
        csrf_token = request.form['csrf_token']

    with get_session() as db_session:
        abstract = db_session.get(Abstract, id)
        if g.IXIPC_user.id == abstract.owner:
            if abstract.submitted:
                return json.dumps({
                  'id': abstract.id,
                  'html': render_template(
                      'abstract-form-open.html', 
                      lang=language, 
                      form=request.form, 
                      reload=True,
                      abstract=abstract,
                      csrf_token=csrf_token,
                      authors=get_abstract_authors_list(id)
                  )
              }), 200
            else:
              return json.dumps({
                  'id': abstract.id,
                  'html': render_template(
                      'abstract-form-open.html', 
                      lang=language, 
                      form=request.form, 
                      reload=True,
                      abstract=abstract,
                      csrf_token=csrf_token
                  )
              }), 200
        else:
            return json.dumps({'error': 'Access not authorized'}), 401


@login_IXIPC_required
@bp.route('/IX_IPC/save_abstract', methods=['POST'])
def save_abstract():
    return save_abstract_local(request.form, g), 200

@login_IXIPC_required
@bp.route('/IXIPC/new_author', methods=['POST'])
def new_author():
    with get_session() as db_session:
        author = Author(created_by=g.IXIPC_user.id)
        db_session.add(author)
        db_session.commit()

        return json.dumps({'id': author.id}), 200

@login_IXIPC_required
@bp.route('/IX_IPC/load_authors', methods=['POST'])
def load_authors():
    with get_session() as db_session:
        authors = db_session.execute(select(Author).where(Author.created_by == g.IXIPC_user.id)).scalars()
        authors_list = []
        for author in authors:
            first_name = author.first_name if author.first_name else '' 
            last_name = author.last_name if author.last_name else '' 
            authors_list.append({
                'firstName': first_name,
                'lastName': last_name,
                'id': author.id
            })

        return json.dumps({'authors': authors_list}), 200


@login_IXIPC_required
@bp.route('/IX_IPC/save_authors', methods=['POST'])
def save_authors():
    authors = json.loads(request.form['authors'])
    with get_session() as db_session:
        authors_list = []
        for id in authors:
            author = db_session.get(Author, int(id))
            author_new = authors[id]
            if g.IXIPC_user.id == author.created_by:
                author.first_name = author_new['firstName']
                author.last_name = author_new['lastName']
                authors_list.append(author)
        db_session.add_all(authors_list)
        db_session.commit()
    return '', 200


@login_IXIPC_required
@bp.route('/IX_IPC/save_abstract_authors', methods=['POST'])
def save_abstract_authors():
    abstracts = json.loads(request.form['abstractAuthors'])
    with get_session() as db_session:
        for abstract_id in abstracts:
            db_session.execute(delete(AbstractAuthor).where(
                AbstractAuthor.abstract_id == abstract_id
            ))

            # TODO: verify if the abstracts and authors being modified belong to user
            # TODO: add the presenter tag
            for (author_id, order, presenter) in abstracts[abstract_id]:
                db_session.add(AbstractAuthor(author_id=author_id, abstract_id=abstract_id, order=order, presenter=presenter))

        db_session.commit()
    return '', 200


def get_abstract_authors_list(abstract_id):
    with get_session() as db_session:
        query = select(AbstractAuthor.abstract_id, AbstractAuthor.author_id, AbstractAuthor.presenter, AbstractAuthor.order, Author.first_name, Author.last_name)\
          .select_from(AbstractAuthor)\
          .join(Author, AbstractAuthor.author_id == Author.id)\
          .where(AbstractAuthor.abstract_id == abstract_id)\
          .order_by(AbstractAuthor.order)
        
        abstract_authors_list = db_session.execute(query)

        abstract_authors = []
        for abstract_author in abstract_authors_list:
            abstract_authors.append({
                'authorId': abstract_author.author_id,
                'firstName': abstract_author.first_name,
                'lastName': abstract_author.last_name,
                'order': abstract_author.order,
                'presenter': abstract_author.presenter
            })
        
        return abstract_authors

@login_IXIPC_required
@bp.route('/IX_IPC/load_abstract_authors', methods=['POST'])
def load_abstract_authors():
    abstract_id = json.loads(request.form['abstractId'])
    return json.dumps({'authors': get_abstract_authors_list(abstract_id)}), 200

# TODO: limit the submission to the right user!!!
@login_IXIPC_required
@bp.route('/IX_IPC/submit_abstract/<language:language>', methods=['POST'])
def submit_abstract(language):
    id = request.form['abstract-id']
    save_abstract_local(request.form, g)

    with get_session() as db_session:
        abstract = db_session.get(Abstract, id)
        abstract.submit()
        db_session.commit()

        return load_abstract(language=language, id=id)

def register(app):
    app.register_blueprint(bp)

    def filter(abstract_type, language) -> str:
        abstract = ''
        if abstract_type == 1:
            abstract = app.i18n.l10n[language].format_value('IXIPC-abstract-poster')
        else:
            abstract = app.i18n.l10n[language].format_value('IXIPC-abstract-presentation')
        
        return abstract

    app.jinja_env.filters['abstract_type'] = filter


    from .db_IXIPC import init_IX_IPC_db_command
    app.cli.add_command(init_IX_IPC_db_command)
