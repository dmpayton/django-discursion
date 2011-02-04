from django.conf import settings

DEFAULT_ANON_READ = getattr(settings, 'DISCURSION_DEFAULT_ANON_READ', True)
DEFAULT_ANON_CREATE = getattr(settings, 'DISCURSION_DEFAULT_ANON_CREATE', False)
DEFAULT_ANON_REPLY = getattr(settings, 'DISCURSION_DEFAULT_ANON_REPLY', False)

RENDER_BACKEND = getattr(settings, 'DISCURSION_RENDER_BACKEND', 'discursion.renderers.Simple')
