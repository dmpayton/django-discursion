from django.dispatch import Signal

new_post = Signal(providing_args=('post', 'new_thread'))
