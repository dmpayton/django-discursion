from discursion.forms import ThreadForm, PostForm
from discursion.models import Forum, Thread, Post
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

def new_thread(request, forum_id, slug, template_name=None, thread_form_class=None, post_form_class=None):
    template_name = template_name or 'discursion/new_thread.html'
    thread_form_class = thread_form_class or ThreadForm
    post_form_class = post_form_class or PostForm
    forum = get_object_or_404(Forum, pk=forum_id)
    form = thread_form_class(request.POST or None, request=request, forum=forum)
    if form.is_valid():
        thread = form.save()
        return redirect(thread)
    return render_to_response(template_name, {
        'forum': forum,
        'form': form,
        }, context_instance=RequestContext(request))

def thread_detail(request, thread_id, slug, template_name=None):
    template_name = template_name or 'discursion/thread_detail.html'
    thread = get_object_or_404(Thread, pk=thread_id)
    thread.view_count = F('view_count') + 1
    thread.save()
    reply_form = PostForm(request=request, thread=thread)
    return render_to_response(template_name, {
        'thread': thread,
        'reply_form': reply_form
        }, context_instance=RequestContext(request))

def add_reply(request, thread_id, slug, template_name=None):
    template_name = template_name or 'discursion/add_reply.html'
    thread = get_object_or_404(Thread, pk=thread_id)
    form = PostForm(request.POST or None, request=request, thread=thread)
    if form.is_valid():
        form.save()
        return redirect(thread)
    return render_to_response(template_name, {
        'thread': thread,
        'form': form,
        }, context_instance=RequestContext(request))

def post_detail(request, thread_id, slug, post_id, template_name=None):
    template_name = template_name or 'discursion/post_detail.html'
    thread = get_object_or_404(Thread, pk=thread_id)
    post = get_object_or_404(thread.posts, pk=post_id)
    return render_to_response(template_name, {
        'thread': thread,
        'post': post,
        }, context_instance=RequestContext(request))
