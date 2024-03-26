from fluent.runtime import FluentLocalization, FluentResourceLoader
from werkzeug.routing import BaseConverter, ValidationError

class I18N():
    """Class to manage the internationalization of the app"""

    class LanguageConverter(BaseConverter):
        """Class to validate and convert language selection"""

        def to_python(self, value) -> str:
            """"Decodes and validates language from url to python"""

            if value not in {'pt', 'en'}:
                raise ValidationError
            return value

        def to_url(self, value):
            """"Encodes language to url"""

            return super(I18N.LanguageConverter, self).to_url(value)
    

    def __init__(self, app) -> None:
        """Registers the class with the app"""

        self.loader = FluentResourceLoader(app.root_path + '/l10n/{locale}')

        self.l10n = {}
        self.l10n['pt'] = FluentLocalization(
            ['pt', 'en'], ['base.ftl'], self.loader
        )
        self.l10n['en'] = FluentLocalization(
            ['en', 'pt'], ['base.ftl'], self.loader
        )

        app.url_map.converters['language'] = I18N.LanguageConverter
        app.jinja_env.filters['l10n'] = \
            lambda string_name, language: \
                self.l10n[language].format_value(string_name)
        
        app.jinja_env.filters['date'] = lambda date: date.strftime("%d/%m/%y")

        app.i18n = self
        
        app.translate = \
            lambda fluent_str, language, params=None: \
                self.l10n[language].format_value(fluent_str, params)


    def lazy_translator(self, string):
        """Returns a translator"""

        return lambda language: self.l10n[language].format_value(string)