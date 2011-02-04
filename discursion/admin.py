from discursion.models import Forum, ForumPermissions, Thread, Post
from discursion.settings import DEFAULT_ANON_READ, DEFAULT_ANON_CREATE, DEFAULT_ANON_REPLY
from django import forms
from django.contrib import admin
from django.template.defaultfilters import yesno
from treebeard.admin import TreeAdmin
from treebeard.forms import MoveNodeForm

class ForumPermissionsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ForumPermissionsForm, self).__init__(*args, **kwargs)
        def update_anon_choices(field, default):
            self.fields[field].widget.choices = [[k, v] for k, v in self.fields[field].widget.choices]
            self.fields[field].widget.choices[0][1] = 'Use default (%s)' % yesno(default)
        update_anon_choices('anon_can_read', DEFAULT_ANON_READ)
        update_anon_choices('anon_can_create', DEFAULT_ANON_CREATE)
        update_anon_choices('anon_can_reply', DEFAULT_ANON_REPLY)

    class Meta:
        model = ForumPermissions

class ForumPermissionsInline(admin.StackedInline):
    filter_horizontal = ('read_groups', 'create_groups', 'reply_groups', 'moderate_groups')
    form = ForumPermissionsForm
    model = ForumPermissions

class ForumAdminForm(MoveNodeForm):
    def __init__(self, *args, **kwargs):
        super(ForumAdminForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Forum

class ForumAdmin(TreeAdmin):
    #fields = ('name', 'slug', 'description', 'order', 'is_closed', 'is_hidden',
    #        'anon_can_read', 'anon_can_post', 'groups_can_read', 'groups_can_post',
    #        'groups_can_moderate')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description',)
        }),
        ('Categorization', {
            'fields': ('_position', '_ref_node_id', 'order')
        }),
        ('Moderation', {
            'fields': ('is_hidden', 'is_closed')
        }),
    )
    form = ForumAdminForm
    inlines = (ForumPermissionsInline,)
    list_display = ('name', 'thread_count', 'post_count')
    list_filter = ('created_on', 'updated_on')
    prepopulated_fields = {'slug': ('name',)}
    #readonly_fields = ('num_threads', 'num_posts', 'last_post')

admin.site.register(Forum, ForumAdmin)
admin.site.register(Thread)
admin.site.register(Post)
