from django.conf import settings
from django.utils.encoding import smart_str, force_unicode

# Python 2.7 has an importlib with import_module; for older Pythons,
# Django's bundled copy provides it.
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

def get_render_backend(path):
    ## from django-registration
    """
    Return an instance of a render backend, given the dotted
    Python import path (as a string) to the backend class.

    If the backend cannot be located (e.g., because no such module
    exists, or because the module does not contain a class of the
    appropriate name), ``django.core.exceptions.ImproperlyConfigured``
    is raised.

    """
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error loading registration backend %s: "%s"' % (module, e))
    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a registration backend named "%s"' % (module, attr))
    return backend_class()

class BaseRenderer(object):
    def __call__(self, message):
        raise NotImplimented

class Simple(BaseRenderer):
    def __call__(self, message):
        from django.template.defaultfilters import linebreaksbr, urlize
        return force_unicode(urlize(linebreaksbr(message))).strip()

class BBCode(BaseRenderer):
    def __call__(self, message):
        try:
            import postmarkup
        except ImportError:
            if not settings.DEBUG:
                return force_unicode(message).strip()
            raise
        return force_unicode(postmarkup.render_bbcode(message)).strip()

class Textile(BaseRenderer):
    def __call__(self, message):
        try:
            import textile
        except ImportError:
            if not settings.DEBUG:
                return force_unicode(message).strip()
            raise
        return force_unicode(textile.textile(smart_str(message), encoding='utf-8', output='utf-8')).strip()

class Markdown(BaseRenderer):
    def __call__(self, message):
        try:
            import markdown
        except ImportError:
            if not settings.DEBUG:
                return force_unicode(message).strip()
            raise
        return force_unicode(markdown.markdown(smart_str(message))).strip()

class ReStructuredText(BaseRenderer):
    def __call__(self, message):
        try:
            from docutils.core import publish_parts
        except ImportError:
            if not settings.DEBUG:
                return force_unicode(message).strip()
        docutils_settings = getattr(settings, 'RESTRUCTUREDTEXT_FILTER_SETTINGS', {})
        parts = publish_parts(source=smart_str(message), writer_name='html4css1', settings_overrides=docutils_settings)
        return force_unicode(parts['fragment']).strip()
