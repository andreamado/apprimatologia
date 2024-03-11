from fluent.runtime import FluentLocalization, FluentResourceLoader
from werkzeug.routing import BaseConverter, ValidationError

import os

class I18N():
    class LanguageConverter(BaseConverter):
        def to_python(self, value):
            if value not in {'pt', 'en'}:
                raise ValidationError
            return value

        def to_url(self, value):
            return super(I18N.LanguageConverter, self).to_url(value)


    def i18n_filter_generator(self) -> str:
        return lambda string_name, language: self.l10n[language].format_value(string_name)


    def __init__(self, app) -> None:
        self.loader = FluentResourceLoader(app.root_path + '/l10n/{locale}')

        self.l10n = {}
        self.l10n['pt'] = FluentLocalization(['pt', 'en'], ['base.ftl'], self.loader)
        self.l10n['en'] = FluentLocalization(['en', 'pt'], ['base.ftl'], self.loader)

        app.url_map.converters['language'] = I18N.LanguageConverter
        app.jinja_env.filters['l10n'] = self.i18n_filter_generator()

        app.i18n = self        

    def lazy_translator(self, string):
        return lambda language: self.l10n[language].format_value(string)