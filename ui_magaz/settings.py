# ui_magaz/settings.py

from pathlib import Path
import os
from dotenv import load_dotenv # Добавляем для python-dotenv
import dj_database_url # Добавляем для настройки базы данных на основе URL
from whitenoise.storage import CompressedManifestStaticFilesStorage # Для Whitenoise

# Загружаем переменные из .env файла
# Это должно быть в самом начале, чтобы переменные были доступны для всего файла
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Получаем SECRET_KEY из переменных окружения.
# Локально - из .env, на Railway - из переменных, установленных на платформе.
# Если переменная не найдена (например, в Dev без .env), используется дефолтное значение.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-mwxhrv(08^g)!2e%j#s7%#*#gq4rxl*g9h2u1k1wqj%9gx#wrs') # Дефолтный ключ для локальной разработки

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG должен быть False в продакшене.
# Получаем DEBUG из переменных окружения и преобразуем строку в булево.
DEBUG = os.getenv('DEBUG', 'False') == 'True' # По умолчанию False, если не указано

# Разрешенные хосты для продакшена.
# Получаем список из переменной окружения, разделяя по запятым.
# Включаем домены Railway (.railway.app) и локальные для разработки.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')
if not DEBUG:
    ALLOWED_HOSTS.append('.railway.app') # Добавляем для продакшена на Railway

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store.apps.StoreConfig',
]

# Debug Toolbar должен быть только в режиме разработки
if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Добавляем Whitenoise здесь, ДО SessionMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Debug Toolbar middleware также только в режиме разработки
if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')


ROOT_URLCONF = 'ui_magaz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Используем Path объекты, более современно
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.header_banner',
            ],
        },
    },
]

WSGI_APPLICATION = 'ui_magaz.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Настройка базы данных с использованием dj-database-url
# DATABASE_URL будет предоставлен Railway (или установлен в .env для локальной PostgreSQL)
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Настройки для локальной разработки (SQLite по умолчанию, если DATABASE_URL не задан)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
# STATICFILES_DIRS - это места, где Django ищет статические файлы во время разработки
# STATIC_ROOT - это место, куда collectstatic собирает все статические файлы для продакшена
STATIC_ROOT = BASE_DIR / 'staticfiles' # Место, куда будут собираться статические файлы для продакшена
STATICFILES_DIRS = [BASE_DIR / 'static'] # Места, где Django ищет статические файлы при разработке

# Whitenoise для продакшена
# Этот класс хранилища автоматически сжимает и кэширует статические файлы
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media' # Это для локального хранения медиа, на продакшене лучше S3 или аналоги

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# INTERNAL_IPS для Debug Toolbar (только если DEBUG=True)
if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
    ]
    # Если вы хотите, чтобы debug_toolbar работал в докере или другом окружении,
    # где 127.0.0.1 не является адресом клиента, вы можете добавить IP-адрес хоста
    # из переменной окружения:
    # import socket
    # try:
    #     hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    #     INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]
    # except Exception:
    #     pass

# Добавляем настройку для Django, чтобы он доверял заголовкам X-Forwarded-Proto
# Это важно для работы HTTPS на Heroku/Railway, так как они используют прокси
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')