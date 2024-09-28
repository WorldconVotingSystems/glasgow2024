# ruff: noqa: F401, E402
"""
Django settings for Glasgow 2024 project.

Generated by copier.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

import bleach.sanitizer
import djp

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# import the system configuration from the application
from nomnom.convention import system_configuration as cfg

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = cfg.secret_key

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = cfg.debug
TEMPLATE_DEBUG = cfg.debug


class InvalidStringShowWarning(str):
    def __mod__(self, other):
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"In template, undefined variable or unknown value for: '{other}'"
        )
        return ""

    def __bool__(self):  # if using Python 2, use __nonzero__ instead
        # make the template tag `default` use its fallback value
        return False


ALLOWED_HOSTS = cfg.allowed_hosts

CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS] if ALLOWED_HOSTS else []

# Application definition

INSTALLED_APPS = [
    "nomnom.apps.NomnomAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    # use whitenoise to serve static files, instead of django's builtin
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # deferred tasks
    "django_celery_results",
    "django_celery_beat",
    # debug helper
    "django_extensions",
    "django_browser_reload",
    # to render markdown to HTML in templates
    "markdownify.apps.MarkdownifyConfig",
    # OAuth login
    "social_django",
    # Admin filtering enhancements
    "admin_auto_filters",
    # Admin audit logging
    "logentry_admin",
    # Theming
    "django_bootstrap5",
    "fontawesomefree",
    # HTMX support
    "django_htmx",
    # A healthcheck
    "watchman",
    # Markdown field support
    "markdownfield",
    "nomnom.base",
    # the convention theme; this MUST come before the nominate app, so that its templates can
    # override the nominate ones.
    "glasgow_2024_app",
    # The nominating and voting app
    "nomnom.nominate",
    # Advisory Votes
    "nomnom.advise",
    # The hugo packet app
    "nomnom.hugopacket",
]

SITE_ID = 1

NOMNOM_ALLOW_USERNAME_LOGIN_FOR_MEMBERS = cfg.allow_username_login

AUTHENTICATION_BACKENDS = [
    # NOTE: the nomnom.nominate.apps.AppConfig.ready() hook will install handlers in this, as the first
    # set. Any handler in here will be superseded by those.
    #
    # Uncomment following if you want to access the admin
    "django.contrib.auth.backends.ModelBackend",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "nomnom.middleware.HtmxMessageMiddleware",
]

ROOT_URLCONF = "glasgow_2024.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "nomnom.nominate.context_processors.site",
                "nomnom.nominate.context_processors.inject_login_form",
            ],
            "string_if_invalid": InvalidStringShowWarning("%s"),
        },
    },
]

WSGI_APPLICATION = "glasgow_2024.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": cfg.db.name,
        "USER": cfg.db.user,
        "PASSWORD": cfg.db.password,
        "HOST": cfg.db.host,
        "PORT": str(cfg.db.port),
    }
}

# reuse some of those DB connections
if not DEBUG:
    CONN_HEALTH_CHECKS = True
    CONN_MAX_AGE = 600

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{cfg.redis.host}:{cfg.redis.port}",
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGOUT_REDIRECT_URL = "index"

# we are using postgres, so this is recommended in the docs.
SOCIAL_AUTH_JSONFIELD_ENABLED = True

# If using social authentication, configure it here. See the social_django documentation for
# details.

# Common social auth settings
# Can't use the backend-specific one because of https://github.com/python-social-auth/social-core/issues/875
# SOCIAL_AUTH_CLYDE_LOGIN_ERROR_URL = "nominate:login_error"
SOCIAL_AUTH_LOGIN_ERROR_URL = "election:login_error"

SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ["username", "first_name", "email"]

# This is a probably-okay social auth pipeline, but you may need to adjust it for your needs.
# See the social_django documentation for details.
SOCIAL_AUTH_PIPELINE = [
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
    "nomnom.nominate.social_auth.pipeline.get_wsfs_permissions",
    "nomnom.nominate.social_auth.pipeline.set_user_wsfs_membership",
    "nomnom.nominate.social_auth.pipeline.normalize_date_fields",
    "nomnom.nominate.social_auth.pipeline.restrict_wsfs_permissions_by_date",
    "nomnom.nominate.social_auth.pipeline.add_election_permissions",
]
# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = cfg.static_file_root

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Async tasks
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "default"
CELERY_BROKER_URL = f"redis://{cfg.redis.host}:{cfg.redis.port}"
CELERY_TIMEZONE = "America/Los_Angeles"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Presentation
ADMIN_MANAGED_ATTRIBUTES = bleach.sanitizer.ALLOWED_ATTRIBUTES.copy()
ADMIN_MANAGED_ATTRIBUTES.update(
    {
        "span": bleach.sanitizer.ALLOWED_ATTRIBUTES.get("span", []) + ["lang"],
        "p": bleach.sanitizer.ALLOWED_ATTRIBUTES.get("p", []) + ["lang"],
        "div": bleach.sanitizer.ALLOWED_ATTRIBUTES.get("div", []) + ["lang"],
    }
)
ADMIN_ALERT_ATTRIBUTES = ADMIN_MANAGED_ATTRIBUTES.copy()
ADMIN_ALERT_ATTRIBUTES["div"] += ["class", "role"]

MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": bleach.sanitizer.ALLOWED_TAGS | {"p", "h4", "h5"},
    },
    "admin-content": {
        "WHITELIST_TAGS": bleach.sanitizer.ALLOWED_TAGS | {"p", "h4", "h5", "span"},
        "WHITELIST_ATTRS": ADMIN_MANAGED_ATTRIBUTES,
    },
    "admin-alert": {
        "WHITELIST_TAGS": bleach.sanitizer.ALLOWED_TAGS
        | {"p", "h4", "h5", "span", "div"},
        "WHITELIST_ATTRS": ADMIN_ALERT_ATTRIBUTES,
    },
    "admin-label": {
        # no block-level elements
        "WHITELIST_TAGS": bleach.sanitizer.ALLOWED_TAGS
        | {"span"} - {"blockquote", "ol", "li", "ul"},
        "WHITELIST_ATTRS": ADMIN_MANAGED_ATTRIBUTES,
    },
}

BOOTSTRAP5 = {
    "field_renderers": {
        "default": "django_bootstrap5.renderers.FieldRenderer",
        "blank-safe": "nomnom.nominate.renderers.BlankSafeFieldRenderer",
    },
}

# Email
EMAIL_HOST = cfg.email.host
EMAIL_PORT = cfg.email.port
EMAIL_HOST_USER = cfg.email.host_user
EMAIL_HOST_PASSWORD = cfg.email.host_password
EMAIL_USE_TLS = cfg.email.use_tls

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "debug_console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django.db.backends": {
            "level": "DEBUG",
            "handlers": ["debug_console"],
        },
    },
}


# Sentry
if cfg.sentry_sdk.dsn is not None:
    # settings.py
    import sentry_sdk

    sentry_sdk.init(
        dsn=cfg.sentry_sdk.dsn,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
        # Our environment
        environment=cfg.sentry_sdk.environment,
        # include the user and client IP
        send_default_pii=True,
    )

try:
    from .settings_override import *  # noqa: F403
except ImportError:
    ...

djp.settings(globals())
