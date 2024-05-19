from flask import session, g, request, render_template

from wtforms import DecimalField, EmailField, FileField, IntegerField, \
                    RadioField, StringField, TelField, TextAreaField, validators

from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField

from .db import get_session
from .models import Member


def register(app):
    """Register the admission form with the app"""

    class RegistrationForm(FlaskForm):
        given_name  = StringField('registration-form-given-name', [validators.Length(min=1, max=50)])
        family_name = StringField('registration-form-family-name', [validators.Length(min=1, max=50)])
        cc_passaporte = StringField('registration-form-cc-passport', [validators.Length(min=5, max=20)])
        nationality = StringField('registration-form-nationality', [validators.Length(min=5, max=20)])
        private_address = StringField('registration-form-private-address', [validators.Length(min=1, max=100)])
        city = StringField('registration-form-city', [validators.Length(min=1, max=20)])
        postal_code = StringField('registration-form-postal-code', [validators.Length(min=1, max=20)])
        country = StringField('registration-form-country', [validators.Length(min=1, max=50)])
        phone_number = TelField('registration-form-phone-number', [validators.Length(min=1, max=20)])
        email = EmailField('registration-form-email', [validators.DataRequired(), validators.Email()])

        work_place = StringField('registration-form-work-place', [validators.Length(min=1, max=50)])
        work_address = StringField('registration-form-work-address', [validators.Length(min=1, max=100)])
        work_city = StringField('registration-form-work-city', [validators.Length(min=1, max=20)])
        work_postal_code = StringField('registration-form-work-postal-code', [validators.Length(min=1, max=20)])
        work_country = StringField('registration-form-work-country', [validators.Length(min=1, max=20)])
        work_phone_number = TelField('registration-form-work-phone-number', [validators.Length(min=1, max=20)])
        work_email = EmailField('registration-form-work-email', [validators.DataRequired(), validators.Email()])
        research_line = TextAreaField('registration-form-research-line')
        species = StringField('registration-form-species')
        academic_title = StringField('registration-form-academic-title')
        current_studies = StringField('registration-form-current-studies')

        address_correspondence = RadioField('registration-form-address-correspondence', choices=[(1, 'private'), (2, 'work')], default=1)
        data_authorization = RadioField('registration-form-data-authorization', choices=[(1, 'yes'), (0, 'no')], default=1)

        supporting_member_name_1 = StringField('registration-form-name', [validators.Length(min=1, max=100)])
        supporting_member_number_1 = IntegerField('number')
        # supporting_member_name_2 = StringField('registration-form-name', [validators.Length(min=1, max=100)])
        # supporting_member_number_2 = IntegerField('number')

        quota_type = RadioField('registration-form-quota-type', choices=[(1, 'regular-quota'), (2, 'reduced-quota')], default=1)
        voluntary_donation = DecimalField('registration-form-voluntary-donation', places=2)
        payment_method = RadioField('registration-form-payment-method', choices=[(1, 'transfer'), (2, 'check')], default=1)
        check_number = StringField('registration-form-check', [validators.Length(min=1, max=50)])
        payment_confirmation = FileField()

        recaptcha = RecaptchaField()


    def label_generator():
        """Generates the labels for the fields"""

        return lambda field, language: f'<label for="{field.id}" class="form-label">{app.i18n.l10n[language].format_value(field.label.text)}</label>'

    app.jinja_env.filters['label'] = label_generator()


    @app.route('/APP/junta-te/<language:language>')
    @app.route('/APP/junta-te')
    def juntate(language='pt', methods=['GET', 'POST']):
        """Members admission page"""

        g.links[0]['active'] = True

        if request.method == 'POST':
            pass

        return render_template(
            'admission.html',
            lang=language,
            form=RegistrationForm()
        )
    
    # @app.route('/api/save_juntate', methods=['POST'])
    # def save_juntate():
    #     """Save new member"""
    #
    #     with get_session as db_session:
    #         member = None
    #         if request.form['id']:
    #             id = request.form['id']
    #             member = db_session.get(Member, id)
    #         else:
    #             member = Member()

    #         if request.form['registration-form-given-name']:
    #             member.given_name = request.form['registration-form-given-name']
