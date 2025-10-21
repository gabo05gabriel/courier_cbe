import os
from pathlib import Path
from dotenv import load_dotenv

# ------------------------------------------------------------------------------
# 🔹 Cargar variables de entorno (.env)
# ------------------------------------------------------------------------------
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# 🔹 Seguridad y configuración general
# ------------------------------------------------------------------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

# ------------------------------------------------------------------------------
# 🔹 Aplicaciones instaladas
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',


    # Apps internas
    'envios',
    'usuarios',
    'pagos',
    'rutas',
    'zonas',
    'ubicaciones_mensajeros',

    # Dependencias API / Auth / CORS
    'rest_framework',
    'corsheaders',
]

# ------------------------------------------------------------------------------
# 🔹 Middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # ✅ primero
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # 👈 debe ir antes de CommonMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'usuarios.middleware.AutenticacionMiddleware',  # si la usas, déjala activa
]

# ------------------------------------------------------------------------------
# 🔹 Configuración de plantillas
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'myproject.wsgi.application'

# ------------------------------------------------------------------------------
# 🔹 Base de datos (usa tu .env)
# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ------------------------------------------------------------------------------
# 🔹 Autenticación y contraseñas
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------------------------
# 🔹 Internacionalización
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# 🔹 Archivos estáticos y media
# ------------------------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ------------------------------------------------------------------------------
# 🔹 Django REST Framework + JWT
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

# ------------------------------------------------------------------------------
# 🔹 CORS y CSRF (para Flutter web y Android)
# ------------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True        # ✅ permite todas las peticiones (solo desarrollo)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']

# Evita el error 403 CSRF desde Flutter Web
CSRF_TRUSTED_ORIGINS = [
    'http://localhost',
    'http://127.0.0.1',
    'http://0.0.0.0',
    'http://localhost:62214',  # Flutter Web local
    'http://127.0.0.1:8000',   # Django
    "http://localhost:53847",
    "http://127.0.0.1:53847",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:51262",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

# ------------------------------------------------------------------------------
# 🔹 Seguridad básica (solo producción)
# ------------------------------------------------------------------------------
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# ------------------------------------------------------------------------------
# 🔹 Archivos estáticos locales
# ------------------------------------------------------------------------------
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# ------------------------------------------------------------------------------
# 🔹 Clave API (opcional)
# ------------------------------------------------------------------------------
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

# ------------------------------------------------------------------------------
# 🔹 Configuración final
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
