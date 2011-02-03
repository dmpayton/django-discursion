from discursion.models import Forum, Thread, Post
from discursion.settings import ALLOW_ANON_READ, ALLOW_ANON_POST
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

class DiscursionPermissionBackend(ModelBackend):
    supports_anonymous_user = True
    supports_object_permissions = True

    def authenticate(self, username, password):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        ## Forum permissions
        if isinstance(obj, Forum):
            pass

        ## Thread permissions
        if isinstance(obj, Thread):
            if obj.forum.permissions.user_is_moderator(user_obj):
                return True

            if user_obj.is_authenticated():
                return False

        if isinstance(obj, Post):
            if obj.forum.permissions.user_is_moderator(user):
                return True

        return False

    def _can_read_forum(self, user, forum):
        if user.is_authenticated():
            if forum.is_hidden or forum.is_closed:
                return False
        else:
            if forum.permissions.anon_can_read is None:
                return ALLOW_ANON_READ
            return forum.permissions.anon_can_read
