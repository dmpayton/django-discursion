from django.conf import settings

DEFAULT_ANON_READ = getattr(settings, 'DISCURSION_DEFAULT_ANON_READ', True)
DEFAULT_ANON_WRITE = getattr(settings, 'DISCURSION_DEFAULT_ANON_WRITE', False)
RENDER_BACKEND = getattr(settings, 'DISCURSION_RENDER_BACKEND', 'discursion.renderers.Simple')
