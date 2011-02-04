from discursion.signals import new_post
from django.db import models

class ForumManager(models.Manager):
    def toplevel(self):
        return self.model.get_root_nodes()

class PostManager(models.Manager):
    def create_post(self, request, thread, message, first_post=False):
        post = self.model(
            thread=thread,
            author=request.user,
            ip_address=request.META['REMOTE_ADDR'],
            message=message
            )
        if not thread.first_post:
            first_post = True
            post.is_first_post = True
        post.render_message()
        post.save()
        new_post.send(sender=self.model, post=post, new_thread=first_post)
        return post
