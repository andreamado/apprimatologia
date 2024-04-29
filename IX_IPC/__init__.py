from flask import flash, render_template, redirect, url_for, Blueprint, g, request, session, send_file
from flask import current_app as app
from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import EmailField, StringField, validators

from sqlalchemy import select, delete

import requests, datetime

from email_validator import validate_email, EmailNotValidError
import phonenumbers

from .db_IXIPC import get_session
from .models import User, Abstract, AbstractType, Author, AbstractAuthor, Institution, Affiliation, Payment, PaymentMethod, PaymentStatus

import json, functools
from hashlib import sha256
import hmac
from secrets import token_hex

import csv
from io import BytesIO, StringIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

class RegistrationForm(FlaskForm):
    name = StringField('registration-form-name', [validators.DataRequired(), validators.Length(max=50)])
    email = StringField('registration-form-email', [validators.DataRequired(), validators.Email()])
    recaptcha = RecaptchaField()

class LoginForm(FlaskForm):
    email = StringField('login-form-email', [validators.DataRequired(), validators.Email()])
    password = StringField('login-form-password', [validators.DataRequired()])

@bp.route('/IX_IPC/<language:language>')
@bp.route('/IX_IPC')
@bp.route('/IX_Iberian_Primatological_Conference/<language:language>')
@bp.route('/IX_Iberian_Primatological_Conference')
def IXIPC(language='pt'):
    """IXIPC main page"""

    g.links[2]['active'] = True

    with get_session() as db_session:
        abstracts = []
        payment_status = 0
        if g.IXIPC_user:
            abstracts = db_session.execute(
                select(Abstract).filter_by(owner=g.IXIPC_user.id)
            ).scalars()

            if(g.IXIPC_user.paid_registration):
                payment_status = 1
            elif (g.IXIPC_user.payment_id):
                payment_status = 2
            
        return render_template(
            'IX_IPC.html',
            lang=language,
            registration_form=RegistrationForm(),
            login_form=LoginForm(),
            text_column=True,
            abstracts=abstracts,
            site_map=True,
            payment_status=payment_status
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

    form = RegistrationForm()
    
    name = form.name.data.strip()
    email = form.email.data

    if not email:
        flash('Email is required.', 'warning')
    elif not name:
        flash('Name is required.', 'warning')
    else:
        email = sanitize_email(email)
        if email:
            with get_session() as db_session:
                try:
                    password = token_hex(16)
                    user = User(name, email, password=password)
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
                                'password': password
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
            password = token_hex(16)
            user.update_password(password)
            db_session.commit()

            app.send_email(
                app.translate('IXIPC-recover-credentials-email-subject', language),
                app.translate(
                    'IXIPC-recover-credentials-email-body', 
                    language, {
                    'email': email,
                    'name': user.name,
                    'password': password
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

    form = LoginForm()
    if form.validate_on_submit():
        email = sanitize_email(form.email.data)

        with get_session() as db_session:
            user = db_session.execute(
                select(User).filter_by(email=email)
            ).scalar_one()

        if user and user.check_password(form.password.data):
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


# https://helpdesk.ifthenpay.com/en/support/solutions/articles/79000141345-api-mbway-v2-rest
# If then pay API request
# {
#     "mbWayKey": "MBWAY_KEY", //(string) mandatory (assigned by ifthenpay)
#     "orderId": "ORDER_ID", //(string) mandatory (15 chars max)
#     "amount": "AMOUNT", //(string) mandatory (decimal separator ".")
#     "mobileNumber": "MOBILE_NUMBER", //(string) mandatory
#     "email": "EMAIL", //(string) optional (100 chars max)
#     "description": "DESCRIPTION", //(string) optional (100 chars max)
# }
#
# and response:
# {
#     "Amount": "33.61",
#     "Message": "Pending",
#     "OrderId": "1887",
#     "RequestId": "i2szvoUfPYBMWdSxqO3n",
#     "Status": "000"
# }
#
# possible status:
# 000 - Request initialized successfully (pending acceptance).
# 100 - The initialization request could not be completed. You can try again.
# 122 - Transaction declined to the user.
# 999 - Error on initializing the request. You can try again.


def get_payment_value(user):
    """Returns the value of the payment for current user"""
    # TODO: update to the real values and take early bird into consideration
    return 35 if user.student else 80

HEADERS_JSON = {
    "accept": "application/json",
    "content-type": "application/json"
}


@login_IXIPC_required
@bp.route('/IX_IPC/payment_mbway/<language:language>', methods=['POST'])
def payment_mbway(language='pt'):
    """Starts an MBWay payment"""

    # parse and validate the phone number
    try:
        number = phonenumbers.parse(str(request.form['number']), 'PT')
        if phonenumbers.is_valid_number(number):
            # TODO: implement masking
            national_number = str(number.national_number)
            # national_number[2:-2] = re.sub('\d', '*', national_number[2:-2])
            masked = '+' + str(number.country_code) + ' ' + national_number
        else:
            raise phonenumbers.NumberParseException
    except:
        return json.dumps({'error': 'Invalid phone number'}), 400
    
    with get_session() as db_session:
        value = get_payment_value(g.IXIPC_user)

        payment = Payment(g.IXIPC_user.id, PaymentMethod.MBWay, masked, value)
        db_session.add(payment)
        db_session.commit()

        # Request to ifthenpay
        url = "https://ifthenpay.com/api/spg/payment/mbway"
            
        request_contents = {
            "mbWayKey": app.config['MBWAY_KEY'], #(string) mandatory (assigned by ifthenpay)
            "orderId": payment.transaction_id, #//(string) mandatory (15 chars max)
            "amount": str(payment.value), #(string) mandatory (decimal separator ".")
            "mobileNumber": str(number.country_code) + '#' + str(number.national_number), #(string) mandatory
            "email": "", #(string) optional (100 chars max)
            "description": app.i18n.l10n[language].format_value('IXIPC-payment-description'), #(string) optional (100 chars max)
        }

        return_content = None
        tries = 0
        while tries < 3:
            # TODO: activate again after the tests
            # response = requests.post(url, json=request_contents, headers=HEADERS_JSON)
            # response_data = response.json()

            # Fake response data for the test phase
            response_data = {
                "Amount": str(payment.value),
                "Message": "Pending",
                "OrderId": payment.transaction_id,
                "RequestId": "DxQI6XtpEPJS4BNfZVsY",
                "Status": "000"
            }
            payment.status_code = response_data['Status']
            payment.request_id = response_data['RequestId']

            if payment.status_code == '000':
                return_content = json.dumps({'id': payment.id}), 200

                user = db_session.get(User, payment.user_id)
                user.payment_id = payment.id
                break
            elif payment.status_code in {'100', '999'}:
                tries += 1 
            elif payment.status_code == '122':
                payment.failed(db_session)
                return_content = json.dumps({'error': 'Phone number declined by the payment processor'}), 400
                break
            else:
                payment.failed(db_session)
                return_content = json.dumps({'error': 'Payment failed for unknown reason'}), 400
                break
                
        if tries >= 3:
            return_content = json.dumps({'error': 'Maximum payment tries exceeded. Try again later'}), 400
            payment.failed(db_session)

        db_session.commit()

        return return_content

# https://ifthenpay.com/api/spg/payment/mbway/status?mbWayKey={mbWayKey}&requestId={requestId}
# {
#     "CreatedAt": "03-01-2024 15:15:06",
#     "Message": "Success",
#     "RequestId": "eR6mcnJzjFx7kOL1Ybdp",
#     "Status": "000",
#     "UpdateAt": "03-01-2024 15:15:16"
# }
# 000 - Transaction successfully completed (Payment confirmed).
# 020 - Transaction rejected by the user.
# 101 - Transaction expired (the user has 4 minutes to accept the payment in the MB WAY App before expiring)
# 122 - Transaction declined to the user. 

@login_IXIPC_required
@bp.route('/IX_IPC/check_mbway_status/<language:language>', methods=['POST'])
def check_mbway_status(language='pt'):
    """Checks the status of an MBWay payment"""

    with get_session() as db_session:
        payment = db_session.get(Payment, request.form['payment_id'])

        if g.IXIPC_user.id == payment.user_id:
            # return json.dumps({'status': payment.status}), 200

            # TODO: solve after dealing with the issue of not knowing what happens if the payment is waiting
            if payment.status != PaymentStatus.pending:
                return json.dumps({'status': payment.status}), 200

            url = f"https://ifthenpay.com/api/spg/payment/mbway/status?mbWayKey={app.config['MBWAY_KEY']}&requestId={payment.request_id}"

            response = requests.get(url)
            response_data = response.json()
            payment.status_code = response_data['Status']

            # TODO: answer: What if the payment is waiting??
            if payment.status_code == '000':
                payment.success(db_session)
            elif payment.status_code == '020':
                payment.canceled(db_session)
            elif payment.status_code == '101':
                payment.expired(db_session)
            elif payment.status_code == '122':
                payment.failed(db_session)
            else:
                db_session.commit()
                app.send_email(
                    'Payment failed',
                    f'Payment of user {g.IXIPC_user.id} failed for unknown reason. Error code {response_data["Status"]}, RequestId {response_data["RequestId"]}, Message {response_data["Message"]}.',
                    [app.config['MAINTENANCE_EMAIL']]
                )
                return json.dumps({'error': 'Request failed for unknown reason'}), 400
            
            db_session.commit()
            return json.dumps({
                'status': payment.status
            }), 200
        else:
            return json.dumps({'error': 'access unauthorized'}), 401


# http://www.yoursite.com/callback.php?key=[ANTI_PHISHING_KEY]&orderId=[ORDER_ID]&amount=[AMOUNT]&requestId=[REQUEST_ID]&payment_datetime=[PAYMENT_DATETIME]
@bp.route('/IX_IPC/payment_callback', methods=['GET'])
def payment_callback():
    """Callback that registers the result of an MBWay payment"""

    if request.args['key'] == app.config['ANTI_PHISHING_KEY']:
        try:
            with get_session() as db_session:
                payment = db_session.execute(
                    select(Payment).where(Payment.request_id == request.args['requestId'])
                ).scalar_one()

                if payment:
                    payment.success(db_session)
                    payment.value = request.args['amount']

                    db_session.commit()
        except:
            print(f'error: could not find payment {request.args["requestId"]} in the database')
            return '', 500

    return '', 200


@login_IXIPC_required
@bp.route('/IX_IPC/creditcard_payment/<language:language>/start', methods=['POST'])
def start_creditcard_payment(language):
    """Starts a new credit card payment and returns a user url for the payment"""

    if g.IXIPC_user.paid_registration:
        return json.dumps({'error': 'User has already paid'}), 403

    else:
        url = f'https://ifthenpay.com/api/creditcard/init/{app.config["CCARD_KEY"]}'
        value = get_payment_value(g.IXIPC_user)

        with get_session() as db_session:
            payment = Payment(g.IXIPC_user.id, PaymentMethod.Card, '', value)

            db_session.add(payment)
            db_session.commit()

            user = db_session.get(User, g.IXIPC_user.id)
            user.payment_id = payment.id

            request_data = {
                "orderId": payment.transaction_id,
                "amount": str(value),
                "successUrl": url_for('IX_IPC.creditcard_payment_success', language=language, _external=True),
                "errorUrl": url_for('IX_IPC.creditcard_payment_error', language=language, _external=True),
                "cancelUrl": url_for('IX_IPC.creditcard_payment_canceled', language=language, _external=True),
                "language" : language
            }

            return_content = None
            tries = 0
            while tries < 3:
                response = requests.post(url, json=request_data, headers=HEADERS_JSON)
                response_data = response.json()

                payment.status_code = response_data['Status']
                payment.request_id = response_data['RequestId']

                if payment.status_code == '0':
                    return_content = json.dumps({
                        'id': payment.id, 
                        'url': response_data['PaymentUrl']
                    }), 200
                    break
                elif payment.status_code == '-1':
                    tries += 1
                    print(f'error obtaining payment url for user id {g.IXIPC_user.id}: {response_data["Message"]}')
                else:
                    payment.failed(db_session)
                    return_content = json.dumps({'error': 'Unable to obtain payment link for unknown reason'}), 400
                    break
                    
            if tries >= 3:
                return_content = json.dumps({'error': 'Maximum payment tries exceeded. Try again later'}), 400
                payment.failed(db_session)

            db_session.commit()

            return return_content


def validate_payment(args):
    """Validates a payment confirmation"""

    message = str(args['id']) + str(args['amount']) + str(args['requestId'])
    hash = hmac.new(
        bytes(app.config['CCARD_KEY'], 'UTF-8'),
        message.encode(),
        sha256
    ).hexdigest()
    return hash == args['sk']


# Test cards:
# Pagamento com sucesso:
# 4012 0010 3714 1112
# CVC: 212
# Validade: 12/27

# Falha no pagamento:
# 4761 7390 0101 0135
# CVC: 608
# Validade: 12/22

@login_IXIPC_required
@bp.route('/IX_IPC/creditcard_payment/<language:language>/success', methods=['GET'])
def creditcard_payment_success(language):
    """Registers the success of a payment and redirects the user to the main page"""

    try:
        if validate_payment(request.args):
            with get_session() as db_session:
                payment = db_session.execute(
                    select(Payment).where(Payment.request_id == request.args['requestId'])
                ).scalar_one()

                payment.success(db_session)
                db_session.commit()
        else:
            print(f'Unable to validate payment {request.args}')
            flash('Could not validate credit card payment! Please contact the organizers')
    except:
        print(f'error: could not find payment {request.args["requestId"]} in the database')

    return redirect(url_for('IX_IPC.IXIPC', language=language))


@login_IXIPC_required
@bp.route('/IX_IPC/creditcard_payment/<language:language>/canceled', methods=['GET'])
def creditcard_payment_canceled(language):
    """Registers that a payment was canceled and redirects the user to the main page"""

    try:
        with get_session() as db_session:
            payment = db_session.execute(
                select(Payment).where(Payment.request_id == request.args['requestId'])
            ).scalar_one()

            print(type(payment))

            payment.canceled(db_session)
            db_session.commit()
    except:
        print(f'error: could not find payment {request.args["requestId"]} in the database')

    return redirect(url_for('IX_IPC.IXIPC', language=language))


@login_IXIPC_required
@bp.route('/IX_IPC/creditcard_payment/<language:language>/error', methods=['GET'])
def creditcard_payment_error(language):
    """Registers that a payment failed and redirects the user to the main page"""

    try:
        with get_session() as db_session:
            payment = db_session.execute(
                select(Payment).where(Payment.request_id == request.args['requestId'])
            ).scalar_one()

            payment.failed(db_session)
            db_session.commit()
    except:
        print(f'error: could not find payment {request.args["requestId"]} in the database')

    return redirect(url_for('IX_IPC.IXIPC', language=language))

@bp.route('/IX_IPC/management/participants_csv_summary')
def participants_csv_summary():    
    with StringIO() as buffer:
        writer = csv.writer(buffer, delimiter=';')

        fields = ['first_name', 'last_name', 'email', 'institution', 'student', 'paid', 'submitted_abstract']
        writer.writerow(fields)

        with get_session() as db_session:
            participants = db_session.execute(
                select(User)
                  .order_by(User.first_name, User.last_name)
            ).scalars()

            for participant in participants:
                abstracts = db_session.execute(
                    select(Abstract)
                      .where(Abstract.owner == participant.id)
                ).scalars().all()

                writer.writerow([
                    participant.first_name, 
                    participant.last_name,
                    participant.email,
                    participant.institution,
                    1 if participant.student else 0,
                    1 if participant.paid_registration else 0,
                    len(abstracts)
                ])

            buffer.seek(0)
            return send_file(
                BytesIO(buffer.getvalue().encode('utf-8-sig')),
                as_attachment=True,
                download_name='participants_summary.csv',
                mimetype='text/csv'
            )

@bp.route('/IX_IPC/management/participants_pdf_report')
def participants_pdf_report():    
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4, showBoundary=0, title='Participants list')

    w, h = A4
    mx = 3*cm
    mt = doc._topMargin
    styles = getSampleStyleSheet()
    name_style = ParagraphStyle('Name', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=16)
    bold_style = ParagraphStyle('Bold', parent=styles['Normal'], fontName='Helvetica-Bold')

    def first_page(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 24)
        canvas.drawString(mx, mt - 5*cm, "IXIPC participants list")
        canvas.setFont("Helvetica", 14)
        canvas.drawString(mx, mt - 6*cm, f'(generated {datetime.datetime.utcnow().strftime("%d/%m/%Y, %H:%M")})')    

        canvas.setFont('Helvetica', 10)
        canvas.drawRightString(doc._rightMargin, 1.8*cm, f"{doc.page}")

        canvas.restoreState()

    def later_pages(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        canvas.drawRightString(doc._rightMargin, 1.8*cm, f"{doc.page}")
        canvas.restoreState()
    
    with get_session() as db_session:
        participants = db_session.execute(
            select(User)
              .where(User.paid_registration == True)
              .order_by(User.first_name, User.last_name)
        ).scalars()

        story = [Spacer(1, 8*cm)]#[PageBreak()]
        style = styles["Normal"]

        for participant in participants:
            participant_description = [
                Paragraph(f'{participant.first_name} {participant.last_name} {"(student)" if participant.student == True else ""}', name_style),
                Spacer(1, 0.5*cm),
                Paragraph(f'email: {participant.email}', style),
                Spacer(1, 0.2*cm),
                Paragraph(f'Institution: {participant.institution}', style),
                Spacer(1, 0.2*cm),
            ]

            if participant.paid_registration and participant.payment_id:
                payment = db_session.get(Payment, participant.payment_id)
                method = PaymentMethod.to_str(payment.method)
                participant_description.append(Paragraph(
                    f'Paid: {payment.value}€ on {payment.concluded.strftime("%d/%m/%Y")} (via {method})',
                    style)
                )
            else:
                participant_description.append(Paragraph('No payment registered', style))
            participant_description.append(Spacer(1, 0.4*cm))

            submitted_abstracts = db_session.execute(
                select(Abstract)
                  .where(Abstract.owner == participant.id)
                  .where(Abstract.submitted == True)
            ).scalars().all()

            if submitted_abstracts:
                participant_description.append(
                    Paragraph('Submitted abstracts:', bold_style)
                )
                participant_description.append(Spacer(1, 0.2*cm))

                for i, abstract in enumerate(submitted_abstracts):
                    participant_description.append(
                        Paragraph(
                            f'{i+1}. ' 
                            + AbstractType.to_string(abstract.abstract_type) 
                            + ' — ' + abstract.title, 
                        style)
                    )

                    authors = db_session.execute(
                        select(AbstractAuthor)
                          .where(AbstractAuthor.abstract_id == abstract.id)
                          .order_by(AbstractAuthor.order)
                    ).scalars().all()

                    authors_list = ''
                    for author in authors:
                        author_details = db_session.get(Author, author.author_id)
                        if author.presenter:
                            authors_list += f'<u>{author_details.first_name} {author_details.last_name}</u>, '
                        else:
                            authors_list += f'{author_details.first_name} {author_details.last_name}, '

                    participant_description.append(Spacer(1, 0.2*cm))
                    participant_description.append(
                        Paragraph(f'Authors: ' + authors_list[:-2], style)
                    )

                    participant_description.append(Spacer(1, 0.2*cm))
                    participant_description.append(
                        Paragraph(f'Keywords: ' + abstract.keywords, style)
                    )
                    participant_description.append(Spacer(1, 0.4*cm))
            else:
                participant_description.append(
                    Paragraph('The participant did not submit any abstracts', 
                    style)
                )
            participant_description.append(Spacer(1, 0.2*cm))

            story.append(KeepTogether(participant_description))
            story.append(Spacer(1, 1*cm))

        doc.build(story, onFirstPage=first_page, onLaterPages=later_pages)

    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name='participants_list.pdf',
        mimetype='application/pdf'
    )

@bp.route('/IX_IPC/management/participants')
@bp.route('/IX_IPC/management/participants/<language:language>')
def participants_list(language='pt'):
    """Gets a list of participants"""

    # TODO: include option to limit to paid registrations
    with get_session() as db_session:
        participants = db_session.execute(
            select(User)
              .where(User.paid_registration == True)
              .order_by(User.first_name, User.last_name)
        ).scalars()

        parts = []
        for participant in participants:
            if participant.paid_registration and participant.payment_id:
                participant.payment = db_session.get(Payment, participant.payment_id)

            participant.submitted_abstracts = db_session.execute(
                select(Abstract)
                  .where(Abstract.owner == participant.id)
                  .where(Abstract.submitted == True)
            ).scalars().all()

            parts.append(participant)

        return render_template(
            'management/participant_list.html',
            lang=language,
            text_column=True,
            participants=parts
        )


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
