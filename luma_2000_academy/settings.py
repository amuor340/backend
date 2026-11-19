
"""
Django settings for luma_2000_academy project.
Pseudosphere Academy
"""

from pathlib import Path
from datetime import timedelta

from decouple import config


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

DEBUG = config("DEBUG", default=True, cast=bool)

SECRET_KEY = config("SECRET_KEY", default="")

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "unsafe-development-only-change-me"
    else:
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured(
            "SECRET_KEY is not set. Add a secure SECRET_KEY to your .env file."
        )

ALLOWED_HOSTS = [
    host.strip()
    for host in config(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1",
    ).split(",")
    if host.strip()
]

AUTH_USER_MODEL = "accounts.CustomUser"


# ============================================================
# CORS AND CSRF
# ============================================================

CORS_ALLOWED_ORIGINS = list(dict.fromkeys(
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    + [
        origin.strip()
        for origin in config(
            "CORS_ALLOWED_ORIGINS",
            default="",
        ).split(",")
        if origin.strip()
    ]
))

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(
    [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    + [
        origin.strip()
        for origin in config(
            "CSRF_TRUSTED_ORIGINS",
            default="",
        ).split(",")
        if origin.strip()
    ]
))


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    # Third-party filtering
    "django_filters",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party applications
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",

    # School Management System applications
    "notifiations",
    "assignments",
    "students",
    "subjects",
    "fees",
    "classes",
    "accounts",
    "schools",
    "parents",
    "attendance",
    "exams",
    "results",
    "timetable",
    "anouncements",
    "dashboard",
    "reports",
    "schooltools",
]


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)

EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 30

EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default=(
        "django.core.mail.backends.smtp.EmailBackend"
        if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
        else "django.core.mail.backends.console.EmailBackend"
    ),
)

DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=(
        f"Pseudosphere Academy <{EMAIL_HOST_USER}>"
        if EMAIL_HOST_USER
        else "Pseudosphere Academy <no-reply@example.com>"
    ),
)

SERVER_EMAIL = DEFAULT_FROM_EMAIL

FRONTEND_URL = config(
    "FRONTEND_URL",
    default="http://localhost:5173" if DEBUG else "",
)

PASSWORD_RESET_CODE_MINUTES = config(
    "PASSWORD_RESET_CODE_MINUTES",
    default=15,
    cast=int,
)

PASSWORD_RESET_MAX_ATTEMPTS = config(
    "PASSWORD_RESET_MAX_ATTEMPTS",
    default=5,
    cast=int,
)

PASSWORD_RESET_RESEND_SECONDS = config(
    "PASSWORD_RESET_RESEND_SECONDS",
    default=60,
    cast=int,
)


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "schooltools.middleware.ApiAuditMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = "luma_2000_academy.urls"


# ============================================================
# TEMPLATES
# ============================================================

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
            ],
        },
    },
]


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "luma_2000_academy.wsgi.application"


# ============================================================
# DATABASE: XAMPP MYSQL / SQLITE
# ============================================================

DB_ENGINE = config(
    "DB_ENGINE",
    default="django.db.backends.mysql",
)

if DB_ENGINE == "django.db.backends.sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": config(
                "DB_NAME",
                default=str(BASE_DIR / "db.sqlite3"),
            ),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,
            "NAME": config(
                "DB_NAME",
                default="psudosphere_db",
            ),
            "USER": config("DB_USER", default="root"),
            "PASSWORD": config("DB_PASSWORD", default=""),
            "HOST": config("DB_HOST", default="127.0.0.1"),
            "PORT": config("DB_PORT", default="3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
            },
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC AND MEDIA FILES
# ============================================================

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "accounts.platform_boundary_authentication.PlatformBoundaryJWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),

    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",

    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],

    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.ScopedRateThrottle",
    ],

    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
        "school_registration": "5/hour",
        "password_reset": "20/hour",
    },
}


# ============================================================
# JWT SETTINGS
# ============================================================

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=config("JWT_ACCESS_MINUTES", default=120, cast=int)
    ),

    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=config("JWT_REFRESH_DAYS", default=30, cast=int)
    ),

    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}


# ============================================================
# SAFARICOM DARAJA / M-PESA
# ============================================================

MPESA_ENVIRONMENT = config(
    "MPESA_ENVIRONMENT",
    default="sandbox",
)

MPESA_CONSUMER_KEY = config(
    "MPESA_CONSUMER_KEY",
    default="",
)

MPESA_CONSUMER_SECRET = config(
    "MPESA_CONSUMER_SECRET",
    default="",
)

MPESA_SHORTCODE = config(
    "MPESA_SHORTCODE",
    default="",
)

MPESA_PASSKEY = config(
    "MPESA_PASSKEY",
    default="",
)

MPESA_CALLBACK_URL = config(
    "MPESA_CALLBACK_URL",
    default="",
)
