from flask import flash, render_template, redirect, url_for, Blueprint, g, request, session
from flask import current_app as app
from flask_wtf import FlaskForm
from sqlalchemy import select, delete

from email_validator import validate_email, EmailNotValidError

from .db_IXIPC import get_session
from .models import User, Abstract, AbstractType, Author, AbstractAuthor, Institution, Affiliation

import json, functools

bp = Blueprint('IX_IPC', __name__, template_folder='templates')


def login_IXIPC_required(view):
    """Guarantees the user is logged in
     
    Decorator that guarantees the user is logged in, redirecting to the main 
    page if they are not.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.IXIPC_user is None:
            return redirect(
                url_for('IX_IPC.IXIPC', language=kwargs['language'])
            )

        return view(**kwargs)

    return wrapped_view


@bp.route('/IX_IPC/<language:language>')
@bp.route('/IX_IPC')
@bp.route('/IX_Iberian_Primatological_Conference/<language:language>')
@bp.route('/IX_Iberian_Primatological_Conference')
def IXIPC(language='pt'):
    """IXIPC main page"""

    g.links[2]['active'] = True

    with get_session() as db_session:
        abstracts = []
        if g.IXIPC_user:
            abstracts = db_session.execute(
                select(Abstract).filter_by(owner=g.IXIPC_user.id)
            ).scalars()

        return render_template(
            'IX_IPC.html',
            lang=language,
            form=FlaskForm(),
            text_column=True,
            abstracts=abstracts,
            site_map=True
        )


def sanitize_email(email: str) -> str|None:
    """Helper function to sanitize input emails"""

    try:
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
    except EmailNotValidError as e:
        return None
    return email


@bp.route('/IX_IPC/register/<language:language>', methods=['POST'])
def register_user(language):
    """Registers a new user
    
    This route registers a new user and logs them in, redirecting to the main
    page with a welcoming message. In the registration process, an email is sent 
    to the user informing their credentials. If anything goes wrong (invalid 
    email, the email is already registered, etc) a warning is displayed.
    """

    g.links[2]['active'] = True

    name = request.form['first-name'].strip()
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
                    url = url_for(
                        'IX_IPC.recover_credentials', 
                        language=language, 
                        email=email
                    )
                    flash(
                        app.translate(
                          'IXIPC-email-already-registered', 
                          language, {
                              'email': email, 
                              'recover_credentials': url
                          }
                        ), 'warning'
                    )
                else:
                    try:
                        app.send_email(
                            app.translate('IXIPC-welcome-email-subject', language),
                            app.translate(
                                'IXIPC-welcome-email-body', 
                                language, {
                                'email': email,
                                'name': name,
                                'password': user.password
                            }),
                            [email]
                        )
                    except:
                        flash(
                            app.translate(
                              'IXIPC-email-failed', language, {'email': email}
                            ), 'warning'
                        )
                    else:
                        flash(
                            app.translate(
                                'IXIPC-account-creation-successful', language
                            ), 'success'
                        )
                        return redirect(url_for("IX_IPC.IXIPC", language=language))
        else:
            flash(app.translate('IXIPC-invalid-email', language), 'warning')

    return redirect(url_for("IX_IPC.IXIPC", language=language))


@bp.route('/IX_IPC/recover_credentials/<language:language>/<string:email>')
def recover_credentials(language, email):
    """Resends the email with the credentials"""

    email = sanitize_email(email)
    if email:
        with get_session() as db_session:
            user = db_session.execute(select(User).filter_by(email=email)).scalar_one()
            app.send_email(
                app.translate('IXIPC-recover-credentials-email-subject', language),
                app.translate(
                    'IXIPC-recover-credentials-email-body', 
                    language, {
                    'email': email,
                    'name': user.name,
                    'password': user.password
                }),
                [email]
            )
            flash(
                app.translate(
                    'IXIPC-recover-credentials-notification', 
                    language
                ), 'success'
            )
    else:
        flash(app.translate('IXIPC-invalid-email', language), 'warning')
    return redirect(url_for("IX_IPC.IXIPC", language=language))


@bp.route('/IX_IPC/login/<language:language>', methods=['POST'])
def login(language):
    """Logs a user in
    
    Logs a user in and redirects to the main page. Displays a warning in case
    the login is unsuccessful. 
    """

    email = sanitize_email(request.form['email'])
    password = request.form['password']

    with get_session() as db_session:
        user = db_session.execute(
            select(User).filter_by(email=email)
        ).scalar_one()

    if user and user.password == password:
        session.clear()
        session['IXIPC_user_id'] = user.id
    else:
        flash(
            app.translate('IXIPC-login-wrong-email-or-password', language), 
            'warning'
        )
    
    return redirect(url_for('IX_IPC.IXIPC', language=language))


@login_IXIPC_required
@bp.route('/IX_IPC/logout/<language:language>', methods=['POST'])
def logout(language):
    """Logs a user out
    
    Logs a user out and redirects to the main page.
    """

    session.clear()
    return redirect(url_for('IX_IPC.IXIPC', language=language))


@bp.before_app_request
def load_logged_in_IXIPC_user() -> None:
    """Loads the current user
    
    Function that runs before every request and adds the current user to g.
    """

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
@bp.route('/IX_IPC/save_personal_data', methods=['POST'])
def save_personal_data():
    """Saves current user's data to the database"""

    with get_session() as db_session:
        user = db_session.get(User, g.IXIPC_user.id)
        user.first_name = request.form['first-name'].strip()
        user.last_name = request.form['last-name'].strip()
        user.institution = request.form['institution'].strip()
        user.student = request.form['student'] == 'true'

        db_session.commit()

        return json.dumps({}), 200


@login_IXIPC_required
@bp.route('/IX_IPC/create_abstract/<language:language>', methods=['POST'])
def create_new_abstract(language='pt'):
    """Creates and returns a new abstract"""

    id = int(json.loads(save_abstract_local(None, g))['id'])
    return load_closed_abstract(id, language), 200


@login_IXIPC_required
@bp.route('/IX_IPC/closed_abstract/<language:language>', methods=['POST'])
def closed_abstract(language='pt'):
    """Returns the closed form of an existing abstract"""

    id = int(request.form['abstract-id'])
    with get_session() as db_session:
        abstract = db_session.get(Abstract, id)

        if abstract.owner == g.IXIPC_user.id:
            return load_closed_abstract(id, language), 200
        else:
            return json.dumps({'error': 'access unauthorized'}), 401


def load_closed_abstract(abstract: int|Abstract, language) -> str:
    """Returns a closed abstract HTML element
    
    Receives an Abstract object or an index to an abstract and return a json 
    string containing the abstract id and the HTML element for the closed 
    abstract.
    """

    if isinstance(abstract, int):
        with get_session() as db_session:
            abstract = db_session.get(Abstract, abstract)
    
    return json.dumps({
        'id': abstract.id,
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
    """Deletes an existing abstract
    
    Deletes the abstract data as well as the corresponding abstract authors.
    """

    with get_session() as db_session:
        id = request.form['abstract-id']

        abstract = db_session.get(Abstract, id)
        delete_abstract_authors = delete(AbstractAuthor)\
                                    .where(AbstractAuthor.abstract_id == id)
        
        if g.IXIPC_user.id == abstract.owner:
            try:
                db_session.delete(abstract)
                db_session.execute(delete_abstract_authors)
                db_session.commit()
            except:
                return json.dumps({'error': 'error deleting abstract'}), 500
            return json.dumps({}), 204
        return json.dumps({'error': 'access unauthorized'}), 401


def save_abstract_local(form, g) -> str:
    """Saves an abstract to the database
    
    Helper function that saves an abstract to the database, creating a new
    abstract if an abstract id is not provided in the request.
    """

    with get_session() as db_session:
        abstract = None
        if form and 'abstract-id' in form and len(form['abstract-id']) > 0:
            id = int(form['abstract-id'])
            abstract = db_session.get(Abstract, id)

            if abstract.owner != g.IXIPC_user.id:
                return json.dumps({'error': 'access unauthorized'})
        else:
            abstract = Abstract(owner=g.IXIPC_user.id)
            db_session.add(abstract)

        if form:
            if 'title' in form:
                abstract.title = form['title'].strip()
                # TODO: update this rejection criteria
                # if len(abstract.title) > 150:
                #     return json.dumps({'error': 'title too long'})

            if 'abstract-body' in form:
                abstract.abstract = form['abstract-body'].strip()
                # TODO: update this rejection criteria
                # if len(abstract.abstract) > 500:
                #     return json.dumps({'error': 'abstract too long'})

            if 'abstract_type' in form:
                abstract_type = form['abstract_type']
                if abstract_type == 'poster':
                    abstract.abstract_type = AbstractType.POSTER
                elif abstract_type == 'presentation':
                    abstract.abstract_type = AbstractType.PRESENTATION
                else:
                    return json.dumps({'error': 'unrecognized abstract type'})
            
            if 'keywords' in form:
                # TODO: process keywords to guarantee they are shown in a uniform fashion
                abstract.keywords = form['keywords'].strip()
        else:
            abstract.title = ''
            abstract.abstract = ''
            abstract.abstract_type = AbstractType.POSTER

        db_session.commit()

        return json.dumps({'id': abstract.id})


@login_IXIPC_required
@bp.route('/IX_IPC/load_abstract/<language:language>/', methods=['POST'])
def load_abstract(language, id=None, csrf_token = None):
    """Loads an abstract in the open form
    
    Returns a json string containing the abstract id and an HTML element 
    representing the open abstract in the submitted or unsubmitted form 
    depending on submission status.
    """

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
                      'abstract-form-open-submitted.html', 
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
                      'abstract-form-open-unsubmitted.html', 
                      lang=language, 
                      form=request.form, 
                      reload=True,
                      abstract=abstract,
                      csrf_token=csrf_token
                  )
              }), 200
        else:
            return json.dumps({'error': 'access unauthorized'}), 401


@login_IXIPC_required
@bp.route('/IX_IPC/save_abstract', methods=['POST'])
def save_abstract():
    """Saves an abstract"""

    return save_abstract_local(request.form, g), 200


@login_IXIPC_required
@bp.route('/IXIPC/new_author', methods=['POST'])
def new_author():
    """Creates a new author"""

    with get_session() as db_session:
        author = Author(created_by=g.IXIPC_user.id)
        db_session.add(author)
        db_session.commit()

        return json.dumps({'id': author.id}), 200


@login_IXIPC_required
@bp.route('/IX_IPC/load_authors', methods=['POST'])
def load_authors():
    """Loads authors available to current user"""

    with get_session() as db_session:
        authors = db_session.execute(
            select(Author).where(Author.created_by == g.IXIPC_user.id)
        ).scalars()

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
    """Saves a list of authors
    
    Saves a list of authors provided in the request.
    """

    authors = json.loads(request.form['authors'])
    with get_session() as db_session:
        authors_list = []
        for (id, author_new) in authors.items():
            author = db_session.get(Author, int(id))
            if g.IXIPC_user.id == author.created_by:
                author.first_name = author_new['firstName'].strip()
                author.last_name = author_new['lastName'].strip()
                authors_list.append(author)
        
        db_session.add_all(authors_list)
        db_session.commit()
    
    return json.dumps({}), 200


@login_IXIPC_required
@bp.route('/IX_IPC/save_affiliations', methods=['POST'])
def save_affiliations():
    """Saves authors' affiliations
    
    Saves the affiliations for a list of authors provided in the request.
    """

    affiliations = json.loads(request.form['affiliations'])
    print(affiliations)
    with get_session() as db_session:
        new_affiliations = []
        for (author_id, institution) in affiliations.items():
            db_session.execute(delete(Affiliation).where(
                Affiliation.author_id == author_id
            ))
            for (institution_id, order) in institution:
                affiliation = Affiliation(
                    author_id=author_id, 
                    institution_id=institution_id, 
                    order=order
                )
                new_affiliations.append(affiliation)

        db_session.add_all(new_affiliations)
        db_session.commit()

    return json.dumps({}), 200


def get_affiliations(author_id: int) -> list[object]|None:
    """Returns a list of authors' affiliations

    Returns a list of authors' affiliations for a given author if or None if
    the author owner is not the current user.
    """

    with get_session() as db_session:
        if db_session.get(Author, author_id).created_by == g.IXIPC_user.id:
            query = select(Affiliation)\
              .where(Affiliation.author_id == author_id)\
              .order_by(Affiliation.order)
            
            affiliations_list = db_session.execute(query).scalars()

            affiliations = []
            for affiliation in affiliations_list:
                affiliations.append({
                    'authorId': author_id,
                    'institutionId': affiliation.institution_id,
                    'order': affiliation.order,
                })
            
            return affiliations
        else:
            return None


@login_IXIPC_required
@bp.route('/IX_IPC/load_affiliations', methods=['POST'])
def load_affiliations():
    """Loads authors' affiliations
    
    Loads the authors' affiliations in request.
    """
    
    author_id = json.loads(request.form['authorId'])
    return json.dumps({'affiliations': get_affiliations(author_id)}), 200


@login_IXIPC_required
@bp.route('/IX_IPC/save_abstract_authors', methods=['POST'])
def save_abstract_authors():
    """Saves the abstract authors
    
    Saves the abstract authors for a list of abstracts provided in the request.
    """

    abstracts = json.loads(request.form['abstractAuthors'])
    with get_session() as db_session:
        abstract_authors = []
        for (abstract_id, abstract) in abstracts.items():
            if db_session.get(Abstract, abstract_id).owner == g.IXIPC_user.id:
                db_session.execute(delete(AbstractAuthor).where(
                    AbstractAuthor.abstract_id == abstract_id
                ))
                for (author_id, order, presenter) in abstract:
                    abstract_author = AbstractAuthor(
                        author_id=author_id, 
                        abstract_id=abstract_id, 
                        order=order, 
                        presenter=presenter
                    )
                    abstract_authors.append(abstract_author)
                
        db_session.add_all(abstract_authors)
        db_session.commit()
    
    return json.dumps({}), 200


def get_abstract_authors_list(abstract_id: int) -> list[object]|None:
    """Returns a list of abstract authors

    Returns a list of the abstract authors for a given abstract id or None if
    the abstract owner is not the current user.
    """

    with get_session() as db_session:
        if db_session.get(Abstract, abstract_id).owner == g.IXIPC_user.id:
            query = select(
                  AbstractAuthor.abstract_id, AbstractAuthor.author_id, 
                  AbstractAuthor.presenter, AbstractAuthor.order, 
                  Author.first_name, Author.last_name
              ).select_from(AbstractAuthor)\
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
        else:
            return None


@login_IXIPC_required
@bp.route('/IX_IPC/load_abstract_authors', methods=['POST'])
def load_abstract_authors():
    """Loads abstract authors
    
    Loads the abstract authors for the abstract in request.
    """
    
    abstract_id = json.loads(request.form['abstractId'])
    return json.dumps({'authors': get_abstract_authors_list(abstract_id)}), 200


@login_IXIPC_required
@bp.route('/IX_IPC/submit_abstract/<language:language>', methods=['POST'])
def submit_abstract(language):
    """Submits an abstract
    
    Submits the abstract and returns the corresponding submitted abstract HTML 
    element or an error message.
    """
    
    id = request.form['abstract-id']
    output = json.loads(save_abstract_local(request.form, g))

    if 'error' not in output:
        with get_session() as db_session:
            abstract = db_session.get(Abstract, id)
            abstract.submit()
            db_session.commit()

            return load_abstract(language=language, id=id)
    else:
        return output, 500


@login_IXIPC_required
@bp.route('/IXIPC/new_institution', methods=['POST'])
def new_institution():
    """Creates a new institution"""

    with get_session() as db_session:
        institution = Institution(created_by=g.IXIPC_user.id)
        db_session.add(institution)
        db_session.commit()

        return json.dumps({'id': institution.id}), 200


@login_IXIPC_required
@bp.route('/IX_IPC/load_institution', methods=['POST'])
def load_institution():
    """Loads an institution"""

    id = json.loads(request.form['id'])
    with get_session() as db_session:
        institution = db_session.get(Institution, id)

        if institution.created_by == g.IXIPC_user.id:
            data = {}
            data['id'] = id
            data['name'] = institution.name if institution.name else ''
            data['address'] = institution.address if institution.address else ''
            data['country'] = institution.country if institution.country else ''
            return json.dumps({'institution': data}), 200
        else:
            return json.dumps({'error': 'access unauthorized'}), 401


@login_IXIPC_required
@bp.route('/IX_IPC/load_institutions', methods=['POST'])
def load_institutions():
    """Loads institutions available to current user"""

    with get_session() as db_session:
        institutions = db_session.execute(
            select(Institution).where(Institution.created_by == g.IXIPC_user.id)
        ).scalars()

        institutions_list = []
        for institution in institutions:
            name = institution.name if institution.name else '' 
            address = institution.address if institution.address else '' 
            country = institution.country if institution.country else '' 
            institutions_list.append({
                'name': name,
                'address': address,
                'country': country,
                'id': institution.id
            })

        return json.dumps({'institutions': institutions_list}), 200

@login_IXIPC_required
@bp.route('/IX_IPC/load_all_affiliations', methods=['POST'])
def load_all_affiliations():
    """Loads all affiliations of the current user's authors"""

    with get_session() as db_session:
        # db_session.add(Affiliation(2, 1, 0))
        # db_session.commit()

        affiliations = db_session.execute(
            select(Affiliation)
            .select_from(Affiliation)
            .join(Author, Affiliation.author_id == Author.id)
            .where(Author.created_by == g.IXIPC_user.id)
            .order_by(Affiliation.order)
        ).scalars()

        affiliations_list = []
        for affiliation in affiliations:
            affiliations_list.append({
                'author_id': affiliation.author_id,
                'institution_id': affiliation.institution_id,
                'order': affiliation.order
            })

        return json.dumps({'affiliations': affiliations_list}), 200


@login_IXIPC_required
@bp.route('/IX_IPC/save_institutions', methods=['POST'])
def save_institutions():
    """Saves a list of institutions
    
    Saves the list of institutions provided in the request.
    """

    institutions = json.loads(request.form['institutions'])
    with get_session() as db_session:
        institutions_list = []
        for (id, institution_new) in institutions.items():
            institution = db_session.get(Institution, int(id))
            if g.IXIPC_user.id == institution.created_by:
                institution.name = institution_new['name'].strip()
                institution.address = institution_new['address'].strip()
                institution.country = institution_new['country'].strip()
                institutions_list.append(institution)
        
        db_session.add_all(institutions_list)
        db_session.commit()
    
    return json.dumps({}), 200


def register(app) -> None:
    """Registers the IXIPC blueprint with the Flask app"""

    app.register_blueprint(bp)

    def abstract_type_filter(abstract_type, language) -> str:
        abstract = ''
        if abstract_type == 1:
            abstract = app.i18n.l10n[language].format_value('IXIPC-abstract-poster')
        else:
            abstract = app.i18n.l10n[language].format_value('IXIPC-abstract-presentation')
        
        return abstract

    app.jinja_env.filters['abstract_type'] = abstract_type_filter

    from .db_IXIPC import init_IXIPC_db_command
    app.cli.add_command(init_IXIPC_db_command)
