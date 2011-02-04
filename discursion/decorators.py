from discursion.middleware import _thread_locals
from django.db.models import Model

def forum_perms_cache(func):
    def wrapper(self, user):
        if not hasattr(_thread_locals, 'discursion_perms'):
            _thread_locals.discursion_perms = {}
        key = '%s:%s:%s' % (func.func_name, user.pk, self.forum.pk)
        if key not in _thread_locals.discursion_perms:
            print 'caching %s' % key
            _thread_locals.discursion_perms[key] = func(self, user)
        return _thread_locals.discursion_perms[key]
    return wrapper

def user_perms_cache(func):
    def wrapper(self, user_obj, perm, obj=None):
        if not hasattr(_thread_locals, 'discursion_perms'):
            _thread_locals.discursion_perms = {}
        if isinstance(obj, Model):
            key = '%s:%s:%s:%s' % (perm, user_obj.pk, obj._meta.module_name, obj.pk)
        else:
            key = '%s:%s' % (perm, user_obj.pk)
        if key not in _thread_locals.discursion_perms:
            print 'caching %s' % key
            _thread_locals.discursion_perms[key] = func(self, user_obj, perm, obj)
        return _thread_locals.discursion_perms[key]
    return wrapper
