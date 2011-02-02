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
        #try:
        #    perm = perm.split('.')[-1]
        #except IndexError:
        #    return False

        ## Forum permissions
        if isinstance(obj, Forum):
            if self._user_can_moderate(user_obj, obj):
                return True



        ## Thread permissions
        if isinstance(obj, Thread):
            if self._user_can_moderate(user_obj, obj.forum):
                return True

            if user_obj.is_authenticated():
                return False

        if isinstance(obj, Post):
            if self._user_can_moderate(user_obj, obj.thread.forum):
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

    def _can_moderate_forum(self, user, forum):
        if user.has_perm('discursion.moderate_forum'):
            ## User is essentially a global moderator
            return True
        ## If the user is in a group that has moderator permissions on any
        ## ancestor, the user is a moderator od that forums.
        return forum.get_ancestors().filter(_permissions__groups_can_moderate=u.groups.all()).exists()
