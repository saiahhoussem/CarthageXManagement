from pathlib import Path

from django.contrib.messages import constants as message_levels

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-s=j(^!do!uh(dbr#=ek4_9s&)c$@bmgkt2ht1vkiw9dxi1r&v7'

DEBUG = True

STATIC_ROOT = BASE_DIR / "staticfiles"
ALLOWED_HOSTS = ['Houssem.pythonanywhere.com', '127.0.0.1', 'localhost']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.forms',
    'compte',
    'enfants',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'carthage_x.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Permet aux widgets de formulaire personnalisés (ex. PhotoFileInput) d'utiliser
# des templates placés dans templates/widgets/, comme n'importe quel autre template
# du projet, plutôt que d'être limité aux dossiers templates/ internes à chaque app.
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

STATICFILES_DIRS = [BASE_DIR / "static"]

WSGI_APPLICATION = 'carthage_x.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_USER_MODEL = 'compte.User'

AUTHENTICATION_BACKENDS = [
    'compte.backends.CourrielOuNomUtilisateurBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = 'compte:connexion'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'compte.validators.ValidateurLongueurMinimale',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'compte.validators.ValidateurMotDePasseCourant',
    },
    {
        'NAME': 'compte.validators.ValidateurMotDePasseNumerique',
    },
]


LANGUAGE_CODE = 'fr-ca'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / "media"


MESSAGE_TAGS = {
    message_levels.ERROR: 'danger',
}
