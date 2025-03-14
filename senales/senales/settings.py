"""
Django settings for senales project.

Generated by 'djangocms' command using django CMS 4.1.4 and Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of Django settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/

For the list of django CMS settings and their values, see
https://docs.django-cms.org/en/release-4.1.x/reference/configuration.html
"""

import os
from pathlib import Path

from django.utils.translation import gettext_lazy as _

from decouple import config
import logging
logging.basicConfig(level=logging.DEBUG)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-994&bno6z+$(xv-np@8sjoutupe_ehu6gbqb$n9y@o^h8v3$3^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#ALLOWED_HOSTS = []
ALLOWED_HOSTS = ['192.168.11.10', 'house.red.lan', 'localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'djangocms_admin_style',

    'django.contrib.admin',

    # Django apps predeterminadas
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',             # Requerido por django-allauth
     # CMS base apps
    'cms',
    'menus',

    'djangocms_text',
    'djangocms_alias',
    'djangocms_versioning',

    'sekizai',
    'treebeard',
    'parler',

    'filer',
    'easy_thumbnails',
    'djangocms_frontend',
    'djangocms_frontend.contrib.accordion',
    'djangocms_frontend.contrib.alert',
    'djangocms_frontend.contrib.badge',
    'djangocms_frontend.contrib.card',
    'djangocms_frontend.contrib.carousel',
    'djangocms_frontend.contrib.collapse',
    'djangocms_frontend.contrib.content',
    'djangocms_frontend.contrib.grid',
    'djangocms_frontend.contrib.icon',
    'djangocms_frontend.contrib.image',
    'djangocms_frontend.contrib.jumbotron',
    'djangocms_frontend.contrib.link',
    'djangocms_frontend.contrib.listgroup',
    'djangocms_frontend.contrib.media',
    'djangocms_frontend.contrib.navigation',
    'djangocms_frontend.contrib.tabs',
    'djangocms_frontend.contrib.utilities',
     # django-allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',  # Opcional, si usas login con redes sociales
    # blog
    'blog',
    'core',
    'django_countries',
    'widget_tweaks',
    # extenciones
    'django_extensions',
    # signals para senales trading
    'signals',
]

# Renueva la configuración TEMPLATES['APP_DIRS'] de la aplicación para deshabilitar el uso de sus plantillas
# INSTALLED_APPS.remove('allauth.account')
# INSTALLED_APPS.insert(0, 'custom_allauth_account')

APPHOOK_RELOAD = True

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Agregado aquí
]

ROOT_URLCONF = 'senales.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "templates"),  # Prioriza esta carpeta
            os.path.join(BASE_DIR, "senales", "templates"),  # Añade esta carpeta como fallback
            os.path.join(BASE_DIR, "core", "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
            ],
        },
    },
]

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

WSGI_APPLICATION = 'senales.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/


# Configuracion de Lenguaje
LANGUAGE_CODE = 'es'

LANGUAGES = [
    ("es", _("Español")),
    ("en", _("English")),
    ('fr', _('French')),
    ('de', _('German')),
    # Agregar más idiomas aquí
]

CMS_LANGUAGES = {
    1: [  # El `1` representa el ID del sitio
        {
            "code": "en",
            "name": "English",
            "fallbacks": ["es"],  # Si no hay traducción, usa español
            "public": True,
        },
        {
            "code": "es",
            "name": "Español",
            "fallbacks": ["en"],  # Si no hay traducción, usa inglés
            "public": True,
        },
    ],
    "default": {
        "fallbacks": ["en", "es"],
        "redirect_on_fallback": True,
        "public": True,
        "hide_untranslated": False,
    },
}

LOCALE_PATHS = [
    BASE_DIR / 'locale',  # Ruta donde estarán los archivos .po y .mo
#    os.path.join(BASE_DIR, 'locale'),  # Asegúrate de tener esta configuración si usas traducciones personalizadas
]

# Personaliza el formulario de inicio de sesión
ACCOUNT_FORMS = {
    'login': 'core.forms.CustomLoginForm',
}

TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Este es el directorio donde se almacenarán los archivos recolectados

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# This is a django CMS 4 template

CMS_CONFIRM_VERSION4 = True

# django CMS requires the site framework
# https://docs.django-cms.org/en/release-4.1.x/how_to/multi-site.html

SITE_ID = 1

# A base template is part of this setup
# https://docs.django-cms.org/en/release-4.1.x/reference/configuration.html#cms-templates

CMS_TEMPLATES = (
    ("base.html", _("Plantilla Base")),
    ("inicio.html", _("Pagina de Incio")),
    ("quienesomos.html", _("Quiénes Somos")),
)

# Enable permissions
# https://docs.django-cms.org/en/release-4.1.x/topics/permissions.html

CMS_PERMISSION = True

# Allow admin sidebar to open admin URLs

X_FRAME_OPTIONS = 'SAMEORIGIN'

# Enable inline editing with djangocms-text
# https://github.com/django-cms/djangocms-text#inline-editing-feature

TEXT_INLINE_EDITING = True

# Allow deletion of version objects
# https://djangocms-versioning.readthedocs.io/en/latest/settings.html#DJANGOCMS_VERSIONING_ALLOW_DELETING_VERSIONS

DJANGOCMS_VERSIONING_ALLOW_DELETING_VERSIONS = True

# Add project-wide static files directory
# https://docs.djangoproject.com/en/5.0/ref/settings/#staticfiles-dirs

STATICFILES_DIRS = [
    BASE_DIR / "senales" / "static",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

# Add project-wide static files directory
# https://docs.djangoproject.com/en/5.0/ref/settings/#media-root

MEDIA_URL = "media/"
MEDIA_ROOT = str(BASE_DIR.parent / "media")

############################################################################
#                             Realizado por PFCO                           #
############################################################################

# Configuracion Postgresql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trading_signals_db',
        'USER': 'pftrading',
        'PASSWORD': '.N0jodas.',
        'HOST': 'localhost',  # O la dirección de tu servidor PostgreSQL
        'PORT': '5432',  # El puerto por defecto de PostgreSQL
    }
}

# Configuracion Sistema de Autenticacion
AUTHENTICATION_BACKENDS = [
    # Soporte para autenticación predeterminada de Django
    'django.contrib.auth.backends.ModelBackend',

    # Soporte para autenticación de django-allauth
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Configuración de django-allauth (puedes personalizar según tus necesidades)
ACCOUNT_AUTHENTICATION_METHOD = 'username'  # o 'email' para autenticación por correo
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Opcional: 'none', 'optional', 'mandatory'

# Configuracion Gmail para correos para produccion, aqui hay que tener un dominio propio, este luego se descomenta
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_PORT = 587
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = 'fmcarrion2022@gmail.com'
#EMAIL_HOST_PASSWORD = 'Pablo1113$'


# Configurar SendGrid como proveedor SMTP en Django para pruebas desa
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'pfcarrion@gmail.com'

# Cambia esto por la URL de tu lógica de creación de usuario y contraseña
#LOGIN_REDIRECT_URL = '/crear-usuario/'
LOGIN_REDIRECT_URL = '/subscribe/'  # Redirige al menú de suscripción después de iniciar sesión
LOGOUT_REDIRECT_URL = '/'  # Redirige a la página principal después de cerrar sesión

# Configuracion Telegram
TELEGRAM_API_ID = '27993507'
TELEGRAM_API_HASH = 'cebd8da77a1b90732917b58da312a333'
TELEGRAM_PHONE_NUMBER = '+5930969934117'

# Configuración de PayPal
#PAYPAL_CLIENT_ID = "AdCUyp80yRSy7XYsBXAGMx2WqANjIf6Ksnaux6ORAGEd7S_3de1c_rlqH1E3N_2GZSer9U_kH4fC6px7"
#PAYPAL_CLIENT_SECRET = "EOCxaj4ys5quvRF5B3p0-I3kTcrDPs_s_oGEto0ZSjzlQL3zrAYDxmAVQXRsPTz0LXBAAicKvVQBdGgV"
# Sandbox para pruebas o producción: https://api.paypal.com
#PAYPAL_MODE = "https://api.sandbox.paypal.com"
#PAYPAL_ENV = "sandbox"  # Cambia a "production" cuando sea necesario

PAYPAL_CLIENT_ID = "AdCUyp80yRSy7XYsBXAGMx2WqANjIf6Ksnaux6ORAGEd7S_3de1c_rlqH1E3N_2GZSer9U_kH4fC6px7"
PAYPAL_CLIENT_SECRET = "EOCxaj4ys5quvRF5B3p0-I3kTcrDPs_s_oGEto0ZSjzlQL3zrAYDxmAVQXRsPTz0LXBAAicKvVQBdGgV"
PAYPAL_ENV = "sandbox"  # Cambia a "production" en producción
PAYPAL_API_URL = "https://api.sandbox.paypal.com" if PAYPAL_ENV == "sandbox" else "https://api.paypal.com"


# Configuración de Binance
BINANCE_API_KEY = "LC2JEIXpq9KFIKhG8Q6exBBLaNQ1ZNEGYbaYq6ptobipe6Zll5g8zbYJIEOFEOLS"
BINANCE_SECRET_KEY = "i9wOMKvG3vXOOP6MmE5p0Rq5mFMUB4H8hPHKPtW67CkaBlDIMxa4Y13EWXVD1PoW"
BINANCE_WALLET_ADDRESS = "TMomjt6WzCzqie2PQ8r7Y4FtPYbtbNUAHR"

# Configuracion para los LOGS de correos
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django_email.log',  # Archivo de log donde se guardarán los correos#        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
            },
        },
    }
}
# Solucion Temporal SEKIZAI para las paginas
SEKIZAI_IGNORE_VALIDATION = True

# Esta parte de la configuracion sirve para rastrear problemas relacionados con el CMS
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'django_cms': {
        'handlers': ['console'],
        'level': 'DEBUG',
        'propagate': True,
    },
}

