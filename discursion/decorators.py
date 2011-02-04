from discursion.middleware import _thread_locals
from django.db.models import Model

def forum_perms_cache(func):
    def wrapper(self, user):
        if not hasattr(_thread_locals, 'discursion_perms'):
            _thread_locals.discursion_perms = {}
        user_id = getattr(user, 'pk', 'anon')
        key = '%s:%s:%s' % (func.func_name, user_id, self.forum.pk)
        if key not in _thread_locals.discursion_perms:
            print 'caching %s' % key
            _thread_locals.discursion_perms[key] = func(self, user)
        return _thread_locals.discursion_perms[key]
    return wrapper

def user_perms_cache(func):
    def wrapper(self, user_obj, perm, obj=None):
        if not hasattr(_thread_locals, 'discursion_perms'):
            _thread_locals.discursion_perms = {}
        user_id = getattr(user_obj, 'pk', 'anon')
        if isinstance(obj, Model):
            key = '%s:%s:%s:%s' % (perm, user_id, obj._meta.module_name, obj.pk)
        else:
            key = '%s:%s' % (perm, user_id)
        if key not in _thread_locals.discursion_perms:
            print 'caching %s' % key
            _thread_locals.discursion_perms[key] = func(self, user_obj, perm, obj)
        return _thread_locals.discursion_perms[key]
    return wrapper
