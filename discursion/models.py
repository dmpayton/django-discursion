from discursion.managers import ForumManager, PostManager
from discursion.render_backends import get_render_backend
from discursion.signals import new_post
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import F, Q
from treebeard.mp_tree import MP_Node

RENDER_BACKEND = getattr(settings, 'DISCURSION_RENDER_BACKEND', 'discursion.renderers.Simple')

class Forum(MP_Node):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    order = models.SmallIntegerField(default=1)
    is_closed = models.BooleanField(default=False, help_text='Only moderators may post in closed forums.')
    is_hidden = models.BooleanField(default=False, help_text='Only moderators will be able to see hidden forums.')

    thread_count = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)
    last_thread = models.ForeignKey('Thread', related_name='last_posted_forum', blank=True, null=True)

    objects = ForumManager()
    node_order_by = ('order',)

    class Meta:
        ordering = ('order',)
        permissions = (('global_moderator', 'Can moderate all forums'),) ## Global mods

    def __unicode__(self):
        return unicode(self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('discursion:forum_detail', (self.pk, self.slug,))

    @models.permalink
    def get_new_thread_url(self):
        return ('discursion:new_thread', (self.pk, self.slug,))

    @property
    def permissions(self):
        ## We always want permissions available, even if they're empty/default
        try:
            return self._permissions
        except ForumPermissions.DoesNotExist:
            return ForumPermissions.objects.create(forum=self)

    @property
    def threads(self):
        return Thread.objects.filter(Q(forum=self)|Q(is_announcement=True)).order_by('-is_announcement', '-is_sticky', '-created_on')

class ForumPermissions(models.Model):
    forum = models.OneToOneField(Forum, related_name='_permissions')

    anon_can_read = models.NullBooleanField(default=None)
    anon_can_post = models.NullBooleanField(default=None)

    user_groups = models.ManyToManyField(Group, related_name='user_forums', blank=True, null=True)
    moderate_groups = models.ManyToManyField(Group, related_name='moderate_forums', blank=True, null=True)

    def __unicode__(self):
        return unicode(self.forum)


class Thread(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    author = models.ForeignKey(User, related_name='threads', blank=True, null=True)

    forum = models.ForeignKey(Forum, related_name='_threads')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    is_closed = models.BooleanField(default=False)
    is_announcement = models.BooleanField(default=False)
    is_sticky = models.BooleanField(default=False)

    view_count = models.IntegerField(default=0)
    post_count = models.IntegerField(default=0)

    first_post = models.ForeignKey('Post', related_name='first_posted_thread', blank=True, null=True)
    last_post = models.ForeignKey('Post', related_name='last_posted_thread', blank=True, null=True)

    class Meta:
        ordering = ('-last_post__created_on',)
        get_latest_by = ('created_on',)

    def __unicode__(self):
        return unicode(self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('discursion:thread_detail', (self.pk, self.slug,))

    @models.permalink
    def get_add_reply_url(self):
        return ('discursion:add_reply', (self.pk, self.slug,))

    @property
    def posts(self):
        return Post.objects.filter(thread=self).order_by('created_on')

class Post(models.Model):
    thread = models.ForeignKey(Thread, related_name='_posts')
    author = models.ForeignKey(User, related_name='posts', blank=True, null=True)

    message = models.TextField()
    message_rendered = models.TextField()

    ip_address = models.IPAddressField()
    created_on = models.DateTimeField(auto_now_add=True)

    is_first_post = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    objects = PostManager()

    def __unicode__(self):
        return unicode(self.pk)

    @models.permalink
    def get_absolute_url(self):
        return ('discursion:post_detail', (self.pk,))

    def render_message(self):
        render = get_render_backend(RENDER_BACKEND)
        self.message_rendered = render(seld.message)


def increment_stats(sender, post, new_thread=False, **kwargs):
    ''' Increment thread/post counts and last_post FK's on Post save '''
    print 'caught signal'
    Thread.objects.filter(pk=post.thread.pk).update(last_post=post, post_count=F('post_count')+1)
    forum_kwargs = {
        'last_thread': post.thread,
        'post_count': F('post_count') + 1,
        }
    if new_thread:
        forum_kwargs['thread_count'] = F('thread_count')+1
    Forum.objects.filter(pk=post.thread.forum.pk).update(**forum_kwargs)
    post.thread.forum.get_ancestors().update(**forum_kwargs)
    print 'success'
new_post.connect(increment_stats, sender=Post)