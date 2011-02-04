import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = MANAGERS = (
    # ('Your Name', 'your_email@domain.com'),
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'public', 'media')
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public', 'static')

ADMIN_MEDIA_PREFIX = '/static/admin/'
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'database.sqlite'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'discursion.auth.DiscursionPermissions',
)

DISCURSION_RENDER_BACKEND = 'discursion.render_backends.BBCode'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
ROOT_URLCONF = 'demosite.urls'
SECRET_KEY = '$qnl-kb=cauln&@6%nnwqwotq2+-5_e8)e$rya_2)m-y(*0xx@'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

TEMPLATE_DIRS = (os.path.join(PROJECT_ROOT, 'templates'),)
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.csrf',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'demosite.context_processors.common'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'discursion.middleware.DiscursionMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'discursion',
    'gravatar',
    'pagination',
    'treebeard',
)

DJANGO_DEBUG_TOOLBAR = True
if DJANGO_DEBUG_TOOLBAR:
    INSTALLED_APPS = list(INSTALLED_APPS)
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
    MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware',)

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
        'HIDE_DJANGO_SQL': False,
    }

    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
        'debug_toolbar.panels.cache.CacheDebugPanel',
    )
