from django.conf import settings

def common(request):
    return {
        'STATIC_URL': settings.STATIC_URL,
    }
