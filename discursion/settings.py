from django.conf import settings

ALLOW_ANON_READ = getattr(settings, 'ALLOW_ANON_READ', True)
ALLOW_ANON_POST = getattr(settings, 'ALLOW_ANON_POST', False)
