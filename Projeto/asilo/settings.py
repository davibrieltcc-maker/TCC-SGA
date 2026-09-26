"""
Configurações do projeto - Sistema de Gerenciamento de Asilo
TCC - Django + SQLite
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-asilo-tcc-2024-substitua-em-producao'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps do projeto
    'core',
    'idosos',
    'medicamentos',
    'fisioterapia',
    'consultas',
    'funcionarios',
    'atividades',
    'relatorios',
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

ROOT_URLCONF = 'asilo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.notificacoes',
            ],
        },
    },
]

WSGI_APPLICATION = 'asilo.wsgi.application'

# Banco de dados SQLite (integrado ao Django)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Formatos de data/hora personalizados (asilo/formats/pt_BR/formats.py).
# Garante que os campos <input type="date"> exibam a data ja salva ao editar.
FORMAT_MODULE_PATH = ['asilo.formats']

# Alinha as tags de mensagem do Django com as classes do Bootstrap
# (messages.error -> "danger", senao o alerta fica sem estilo).
from django.contrib.messages import constants as _messages  # noqa: E402

MESSAGE_TAGS = {_messages.ERROR: 'danger'}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirecionamento após login/logout
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# Sessão: guarda a sessão no cache em memória (LocMemCache), que é zerado toda
# vez que o servidor reinicia. Assim, ao iniciar o sistema, ninguém continua
# logado — sempre cai na tela de autenticação. Também expira ao fechar o
# navegador.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Modelo de usuário customizado
AUTH_USER_MODEL = 'core.Usuario'
