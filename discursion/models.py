from discursion.decorators import forum_perms_cache
from discursion.managers import ForumManager, PostManager
from discursion.render_backends import get_render_backend
from discursion.settings import DEFAULT_ANON_READ, DEFAULT_ANON_CREATE, DEFAULT_ANON_REPLY, RENDER_BACKEND
from discursion.signals import new_post
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import F, Q
from treebeard.mp_tree import MP_Node

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
        permissions = (('global_moderator', 'Global Moderator'),) ## Global mods

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
        return Thread.objects.filter(Q(forum=self)|Q(is_announcement=True)).select_related('author', 'last_thread').order_by('-is_announcement', '-is_sticky', 'created_on')

class ForumPermissions(models.Model):
    forum = models.OneToOneField(Forum, related_name='_permissions')

    anon_can_read = models.NullBooleanField(default=None, help_text='Allow anonymous users to read this forum.')
    anon_can_create = models.NullBooleanField(default=None, help_text='Allow anonymous users to create new threads in this forum.')
    anon_can_reply = models.NullBooleanField(default=None, help_text='Allow anonymous users to reply to threads in this forum.')

    read_groups = models.ManyToManyField(Group, related_name='read_forum_perms', help_text='No groups selected gives read access to all groups.', blank=True, null=True)
    create_groups = models.ManyToManyField(Group, related_name='create_thread_perms', help_text='No groups selected gives create thread access to all groups.', blank=True, null=True)
    reply_groups = models.ManyToManyField(Group, related_name='reply_thread_perms', help_text='No groups selected gives reply access to all groups.', blank=True, null=True)
    moderate_groups = models.ManyToManyField(Group, related_name='moderate_forums', help_text='This is in addition to global moderators.', blank=True, null=True)

    def __unicode__(self):
        return unicode(self.forum)

    @forum_perms_cache
    def user_can_read(self, user):
        ''' Basic read permissions, does not take into account moderator or superuser status '''
        if self.forum.is_hidden:
            return False
        if not user.is_authenticated():
            if self.anon_can_read is None:
                return DEFAULT_ANON_READ
            return self.anon_can_read
        if self.read_groups.count():
            return ForumPermission.objects.filter(forum=self.forum, read_groups=u.groups.all()).exists()
        return True

    @forum_perms_cache
    def user_can_create_thread(self, user):
        ''' Basic create thread permissions, does not take into account moderator or superuser status '''
        if self.forum.is_hidden or forum.is_closed:
            return False
        if not user.is_authenticated():
            if self.anon_can_create is None:
                return DEFAULT_ANON_CREATE
            return self.anon_can_create
        if self.create_groups.count():
            return ForumPermission.objects.filter(forum=self.forum, create_groups=u.groups.all()).exists()
        return True

    @forum_perms_cache
    def user_can_add_reply(self, user):
        ''' Basic reply permissions, does not take into account moderator or superuser status '''
        if self.forum.is_hidden or self.forum.is_closed:
            return False
        if not user.is_authenticated():
            if self.anon_can_reply is None:
                return DEFAULT_ANON_REPLY
            return self.anon_can_reply
        if self.reply_groups.count():
            return ForumPermission.objects.filter(forum=self.forum, reply_groups=u.groups.all()).exists()
        return True

    @forum_perms_cache
    def user_can_moderate(self, user):
        ''' Check if the user can moderate this forum. '''
        ## Check if the user is a global moderator
        if user.has_perm('discursion.global_moderator'):
            return True
        ## Explicit moderator groups on this forum
        if self.moderate_groups.count():
            return ForumPermission.objects.filter(forum=self.forum, moderate_groups=u.groups.all()).exists()
        ## If the user is in a group that has moderator permissions on any
        ## ancestor, the user is a moderator of that forums.
        #return self.forum.get_ancestors().filter(_permissions__moderate_groups=u.groups.all()).exists()
        return False # CONSIDER: Do we want moderator perms to trickle down?


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
    is_deleted = models.BooleanField(default=False)

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
        return ('discursion:new_post', (self.pk, self.slug,))

    @property
    def posts(self):
        return Post.objects.filter(thread=self).select_related('author', 'thread', 'thread__forum').order_by('created_on')

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
        return ('discursion:post_detail', (self.thread.pk, self.thread.slug, self.pk,))

    @models.permalink
    def get_delete_post_url(self):
        return ('discursion:delete_post', (self.thread.pk, self.thread.slug, self.pk,))

    def render_message(self):
        render = get_render_backend(RENDER_BACKEND)
        self.message_rendered = render(self.message)


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
