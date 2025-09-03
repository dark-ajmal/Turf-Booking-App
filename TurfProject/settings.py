from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
SECRET_KEY = 'django-insecure-+oqza55jo)!@4v^$gk24pisvolhbw9h_5p%5$&z*e3+qokg4_g'
DEBUG = True
ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'TurfApp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # --- ADD THIS LINE ---
    "whitenoise.middleware.WhiteNoiseMiddleware", # For serving static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TurfProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # --- CORRECTED DIRS PATH ---
        'DIRS': [os.path.join(BASE_DIR, 'TurfApp/templates')],
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

WSGI_APPLICATION = 'TurfProject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ... (Password Validators) ...

# --- CORRECT STATIC AND MEDIA CONFIGURATION ---

# Static files (CSS, JavaScript, Images for your site's design)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (User-uploaded content like turf photos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'TurfApp.TurfUser'

# ... (Your JAZZMIN_SETTINGS) ...


JAZZMIN_SETTINGS = {
    # Title on the login screen (best kept short)
    "site_title": "OnlyTurf Admin",

    # Title on the brand logo
    "site_header": "OnlyTurf",

    # Welcome text on the admin index page
    "welcome_sign": "Welcome to the OnlyTurf Admin Dashboard",

    # Copyright notice
    "copyright": "OnlyTurf Ltd.",

    # The model admin to search from the search bar, search model admin looks like:
    # app_label.Model|Model|...
    "search_model": "TurfApp.TurfUser",

    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "View Site", "url": "/", "new_window": True},
        {"model": "TurfApp.TurfUser"},
    ],

    #############
    # UI Tweaks #
    #############
    # Relative paths to custom CSS/JS scripts (must be present in static files)
    "custom_css": None,
    "custom_js": None,
    # Whether to show the UI customizer on the sidebar
    "show_ui_builder": True,

    ###############
    # Change view #
    ###############
    # Render out the change view as a single form, or in tabs, current options are
    # - single
    # - horizontal_tabs (default)
    # - vertical_tabs
    # - collapsible
    # - carousel
    "changeform_format": "horizontal_tabs",
}
