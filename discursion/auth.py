from discursion.decorators import user_perms_cache
from discursion.models import Forum, Thread, Post
from discursion.settings import DEFAULT_ANON_CREATE, DEFAULT_ANON_REPLY
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

class DiscursionPermissions(ModelBackend):
    supports_anonymous_user = True
    supports_object_permissions = True

    def authenticate(self, username, password):
        return None

    @user_perms_cache
    def has_perm(self, user_obj, perm, obj=None):
        # read_forum (forum)
        # create_thread (forum)
        # delete_thread (thread)
        # create_post (thread)
        # edit_post (post)

        ## discursion.perm_check -> perm_check
        try:
            perm = perm.split('.')[-1]
        except IndexError:
            return False

        ## Forum permissions
        if isinstance(obj, Forum):
            if perm == 'read_forum':
                if obj.permissions.user_can_moderate(user_obj):
                    return True
                if obj.permissions.user_can_read(user_obj):
                    return True
                return False

            if perm == 'create_thread':
                if obj.is_root():
                    return False # No threads in root forums
                if obj.permissions.user_can_moderate(user_obj):
                    return True
                if obj.permissions.user_can_create_thread(user_obj):
                    return True
                return False
            return False

        ## Thread permissions
        if isinstance(obj, Thread):
            if perm == 'delete_thread':
                if obj.forum.permissions.user_can_moderate(user_obj):
                    return True
                if obj.forum.permissions.user_can_create_thread():
                    return True
                return False

            if perm == 'create_post':
                if obj.forum.permissions.user_can_moderate(user_obj):
                    return True
                if all((
                    obj.forum.permissions.user_can_add_reply(user_obj),
                    obj.author == user_obj,
                    not obj.is_closed)):
                    return True
                return False
            return False

        ## Post permissions
        if isinstance(obj, Post):
            if perm == 'edit_post':
                if obj.thread.forum.permissions.user_can_moderate(user_obj):
                    return True
                if all((
                    obj.thread.forum.permissions.user_can_add_reply(user_obj),
                    obj.author == user_obj,
                    not obj.thread.is_closed,
                    not obj.thread.is_deleted)):
                    return True
                return False
            return False
        return False
