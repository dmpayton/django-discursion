from discursion.forms import ThreadForm, PostForm
from discursion.models import Forum, Thread, Post
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template.context import RequestContext

def index(request, template_name=None):
    template_name = template_name or 'discursion/index.html'
    forum_list = Forum.objects.toplevel()
    return render_to_response(template_name, {
        'forum_list': forum_list
        }, context_instance=RequestContext(request))


def forum_detail(request, forum_id, slug, template_name=None):
    template_name = template_name or 'discursion/forum_detail.html'
    forum = get_object_or_404(Forum.objects.select_related(), pk=forum_id)
    return render_to_response(template_name, {
        'forum': forum
        }, context_instance=RequestContext(request))


def new_thread(request, forum_id, slug, template_name=None, thread_form_class=None):
    template_name = template_name or 'discursion/thread_form.html'
    thread_form_class = thread_form_class or ThreadForm
    forum = get_object_or_404(Forum, pk=forum_id)
    form = thread_form_class(request.POST or None, request=request, forum=forum)
    if form.is_valid():
        thread = form.save()
        return redirect(thread)
    return render_to_response(template_name, {
        'forum': forum,
        'form': form,
        }, context_instance=RequestContext(request))

def edit_thread(request, thread_id, slug, template_name=None, thread_form_clas=None):
    template_name = template_name or 'discursion/thread_form.html'
    thread_form_class = thread_form_class or ThreadForm
    thread = get_object_or_404(Thread.objects.select_related('forum', 'author'), pk=thread_id)
    form = thread_form_class(request.POST or None, instance=thread)
    if form.is_valid():
        thread = form.save()
        return redirect(thread)
    return render_to_response(template_name, {
        'form': form,
        'thread': thread,
        'forum': thread.forum,
        }, context_instance=RequestContext(request))

def thread_detail(request, thread_id, slug, template_name=None):
    template_name = template_name or 'discursion/thread_detail.html'
    thread = get_object_or_404(Thread.objects.select_related('forum'), pk=thread_id)
    thread.view_count = F('view_count') + 1
    thread.save()
    reply_form = PostForm(request=request, thread=thread)
    return render_to_response(template_name, {
        'thread': thread,
        'forum': thread.forum,
        'reply_form': reply_form
        }, context_instance=RequestContext(request))


def new_post(request, thread_id, slug, template_name=None):
    template_name = template_name or 'discursion/post_form.html'
    thread = get_object_or_404(Thread.objects.select_related('forum'), pk=thread_id)
    form = PostForm(request.POST or None, request=request, thread=thread)
    if form.is_valid():
        form.save()
        return redirect(thread)
    return render_to_response(template_name, {
        'form': form,
        'thread': thread,
        'forum': thread.forum,
        }, context_instance=RequestContext(request))


def edit_post(request, thread_id, slug, post_id, template_name=None, post_form_class=None):
    template_name = template_name or 'discursion/post_form.html'
    post_form_class = post_form_class or PostForm
    post = get_object_or_404(Post.objects.select_related('author', 'thread', 'thread__forum'), pk=post_id, thread=thread_id)
    form = post_form_class(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(post.thread)
    return render_to_response(template_name, {
        'form': form,
        'post': post,
        'thread': post.thread,
        'forum': post.thread.forum,
        }, context_instance=RequestContext(request))



def delete_post(request, thread_id, slug, post_id):
    thread = get_object_or_404(Thread.objects.select_related('forum'), pk=thread_id)
    post = get_object_or_404(thread.posts, pk=post_id)
    if request.user.has_perm('discursion.edit_post', post):
        post.is_deleted = True
        post.save()
        messages.success(request, 'Your post has been deleted')
        return redirect(thread)
    raise PermissionDenied

def post_detail(request, thread_id, slug, post_id, template_name=None):
    template_name = template_name or 'discursion/post_detail.html'
    post = get_object_or_404(Post.objects.select_related('author', 'thread', 'thread__forum'), pk=post_id, thread=thread_id)
    return render_to_response(template_name, {
        'post': post,
        'thread': post.thread,
        'forum': post.thread.forum
        }, context_instance=RequestContext(request))
