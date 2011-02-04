from discursion.models import Forum, Thread, Post
from discursion.signals import new_post
from django import forms
from django.template.defaultfilters import slugify

class ThreadForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea)

    class Meta:
        fields = ['name',]
        model = Thread

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request', None)
        self._forum = kwargs.pop('forum', None)
        super(ThreadForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['message'].initial = self.instance.first_post.message
        ## if request.user.has_perm('discursion.forum_moderator', forum):
        ##     self.fields.is_sticky, is closed
        ## if request.user.has_perm('discursion.global_moderator'):
        ##     self.fields is_announcement

    def save(self, *args, **kwargs):
        kwargs['commit'] = False
        thread = super(ThreadForm, self).save(*args, **kwargs)
        if not self.instance.pk:
            ## No PK, it's a new thread
            thread.author = self._request.user
            thread.forum = self._forum
            thread.slug = slugify(thread.name)
            thread.save()
            Post.objects.create_post(
                request=self._request,
                thread=thread,
                message=self.cleaned_data['message'],
                first_post=True
                )
        else:
            thread.first_post.message = self.cleaned_data['message']
            thread.first_post.render_message()
            thread.first_post.save()
            thread.save()
        return thread

class PostForm(forms.ModelForm):
    class Meta:
        fields = ['message']
        model = Post

    def __init__(self, *args, **kwargs):
        self._request = kwargs.pop('request', None)
        self._thread = kwargs.pop('thread', None)
        super(PostForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.instance.pk:
            post = Post.objects.create_post(
                request=self._request,
                thread=self._thread,
                message=self.cleaned_data['message'],
                )
            return post
        else:
            self.instance.message = self.cleaned_data['message']
            self.instance.render_message()
            self.instance.save()
            return self.instance
