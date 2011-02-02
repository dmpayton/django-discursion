from discursion.models import Forum, Thread, Post
from django.core.management.base import NoArgsCommand, CommandError

class Command(NoArgsCommand):
    help = 'Perform an audit of forum post/thread counts'

    def handle_noargs(self, **kwargs):
        def audit_forum(forum):
            thread_count = Thread.objects.filter(forum=forum).count()
            post_count = Post.objects.filter(thread__forum=forum).count()
            for subforum in forum.subforums.all():
                subforum_threads, subforum_posts = audit_forum(subforum)
                thread_count += subforum_threads
                post_count += subforum_posts
            forum.thread_count = thread_count
            forum.post_count = post_count
            forum.save()
            return thread_count, post_count

        print 'Auditing forums...'
        for forum in Forum.objects.toplevel():
            audit_forum(forum)

        print 'Auditing threads...'
        for thread in Thread.objects.all():
            thread.post_count = Post.objects.filter(thread=thread).count()
            thread.save()
