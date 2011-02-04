from django.conf.urls.defaults import *

urlpatterns = patterns('discursion.views',
    # url(r'', '', name=''),
    url(r'^$', 'index', name='index'),
    url(r'^forum/(?P<forum_id>\d+)/(?P<slug>[\w-]+)/$', 'forum_detail', name='forum_detail'),
    url(r'^forum/(?P<forum_id>\d+)/(?P<slug>[\w-]+)/new-thread/$', 'new_thread', name='new_thread'),
    url(r'^thread/(?P<thread_id>\d+)/(?P<slug>[\w-]+)/$', 'thread_detail', name='thread_detail'),
    url(r'^thread/(?P<thread_id>\d+)/(?P<slug>[\w-]+)/add-reply/$', 'add_reply', name='add_reply'),
    url(r'^thread/(?P<thread_id>\d+)/(?P<slug>[\w-]+)/post/(?P<post_id>\d+)/$', 'post_detail', name='post_detail'),
    url(r'^thread/(?P<thread_id>\d+)/(?P<slug>[\w-]+)/post/(?P<post_id>\d+)/delete/$', 'delete_post', name='delete_post'),
)
