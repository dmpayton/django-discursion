from django.conf import settings
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

class DiscursionMiddleware(object):
    def process_response(self, request, response):
        ''' At the end of the request cycle, clear the forum permissions cache '''
        _thread_locals.discursion_perms = {}
        return response
