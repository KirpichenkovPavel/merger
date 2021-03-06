# coding=utf-8
"""
Django settings for polyana_web project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/

!!! DO NOT EDIT THIS FILE UNLESS YOU REALLY KNOW WHAT YOU ARE DOING !!!
All user settings should be overridden in local_settings.py file
(Use local_settings.py.template as a template)
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import time
from types import ModuleType, FunctionType

from django.core.urlresolvers import reverse_lazy
from django_auth_ldap.config import LDAPSearch
import ldap


########################################################################################################################
# Some dark python magic to detect overridable settings
########################################################################################################################

class OverrideProxy:
    __slots__ = ["_obj", "__weakref__"]

    def __init__(self, obj):
        object.__setattr__(self, "_obj", obj)

    #
    # proxying (special cases)
    #
    def __getattribute__(self, name):
        if name == "underlying_object":
            return object.__getattribute__(self, "_obj")
        else:
            return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self):
        return bool(object.__getattribute__(self, "_obj"))

    def __str__(self):
        return str(object.__getattribute__(self, "_obj"))

    def __repr__(self):
        return repr(object.__getattribute__(self, "_obj"))

    #
    # factories
    #
    _special_names = [
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__',
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__',
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__',
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__',
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__',
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__',
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__',
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__',
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__',
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__',
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__',
        '__truediv__', '__xor__', 'next',
    ]

    @classmethod
    def _create_class_proxy(cls, theclass):
        """creates a proxy for the given class"""

        def make_method(name):
            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, "_obj"), name)(*args, **kw)

            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """
        creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
        passed to this class' __init__, so deriving classes can define an
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)
        return ins


class DoNotOverrideMe(OverrideProxy):
    pass


class OverrideMe(OverrideProxy):
    pass


class DoNotCare(OverrideProxy):
    pass

########################################################################################################################

#BASE_DIR = DoNotOverrideMe(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
BASE_DIR = DoNotOverrideMe(os.path.dirname(os.path.dirname(__file__)))

ADMINS = OverrideMe((
    ('Поляна', 'polyana.web@yandex.ru'),
))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DoNotCare(False)

TEMPLATE_DEBUG = DoNotCare(False)

INSTALLED_APPS = DoNotOverrideMe((
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'crequest',
    'django_remote_model',
    'main_remote',
    'polyauth_remote',
    'polyauthentication',
    'main',
))

ALLOWED_HOSTS = OverrideMe([])

# Application definition


MIDDLEWARE_CLASSES = DoNotOverrideMe((
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crequest.middleware.CrequestMiddleware',
))


TEMPLATE_CONTEXT_PROCESSORS = DoNotOverrideMe((
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    # 'main.context_processors.menu_generator',
    # 'polyauth.context_processors.available_role_templates',
    # 'tickets.context_processors.user_tickets_count',
    # 'main.context_processors.external_services'
))

STATICFILES_FINDERS = DoNotOverrideMe((
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
))

ROOT_URLCONF = DoNotOverrideMe('merger.urls')

#WSGI_APPLICATION = DoNotOverrideMe('polyana_web.wsgi.application')

SESSION_ENGINE = DoNotOverrideMe("django.contrib.sessions.backends.cached_db")

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
# To be overriden by local settings
DATABASES = OverrideMe({
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'polyana_web',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
})

DATABASE_ROUTERS = DoNotOverrideMe(['django_remote_model.routers.RemoteRouter'])

# Cache

CACHES = DoNotCare({
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400
    }
})
QUERY_CACHE_PREFIX = DoNotOverrideMe(int(time.time()))

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = OverrideMe('ru-ru')

TIME_ZONE = OverrideMe('Europe/Moscow')

USE_I18N = DoNotOverrideMe(True)

USE_L10N = DoNotOverrideMe(True)

USE_TZ = DoNotOverrideMe(True)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = DoNotOverrideMe('/static/')
TEMPLATE_DIRS = DoNotOverrideMe((BASE_DIR + '/templates/',))
STATICFILES_DIRS = DoNotOverrideMe((BASE_DIR + '/static/',))

# Authentication configuration

AUTH_USER_MODEL = DoNotOverrideMe('polyauthentication.PolyUser')

LOGIN_URL = DoNotOverrideMe(reverse_lazy('polyauth:login'))
LOGIN_REDIRECT_URL = DoNotOverrideMe(reverse_lazy('polyauth:login_role'))
INDEX_URL = DoNotOverrideMe(reverse_lazy('index'))

LOGOUT_URL = DoNotOverrideMe(reverse_lazy('polyauth:logout'))

LOGIN_NOT_REQUIRED_URLS = DoNotOverrideMe([
    "/tickets-api/.*"
])

AUTHENTICATION_BACKENDS = DoNotOverrideMe((
    'django.contrib.auth.backends.ModelBackend',
    'polyauthentication.backends.PolyauthenticationBackend',
))

ANONYMOUS_USER_ID = DoNotOverrideMe(-1)

AUTH_LDAP_SERVER_URI = OverrideMe('ldap://127.0.0.1')
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = DoNotOverrideMe(True)
AUTH_LDAP_USER_DN_TEMPLATE = OverrideMe('SPBSTU\%(user)s')

AUTH_LDAP_USER_SEARCH = OverrideMe(LDAPSearch('OU=СПбГПУ,DC=test,DC=dc',
                                   ldap.SCOPE_SUBTREE, "sAMAccountName=%(user)s"))

AUTH_LDAP_USER_ATTR_MAP = DoNotCare({
    'employee_id': 'employeeID',
})

PAGINATION_DEFAULT_PAGINATION = DoNotCare(20)

POLYANA_SERVER_URI = OverrideMe('http://127.0.0.1:31780')

POLYANA_API_PATH = DoNotOverrideMe('/polyana-core-ws/core/api')

NSI_SERVER_URI = OverrideMe('http://127.0.0.1:31780')

NSI_API_PATH = DoNotOverrideMe('/polyana-nsi-ws/nsi/api')

LDAP_PROXY_SERVER_URI = OverrideMe('http://127.0.0.1:31780')

LDAP_PROXY_API_PATH = DoNotOverrideMe('/polyana-ldap-proxy-ws/ldapproxy/api')

REPORTS_SERVER_URI = OverrideMe('http://polyana.deploy:31780')

REPORTS_API_PATH = DoNotOverrideMe('/polyana-reports-ws/reports/api')

SETTINGS_PATH = DoNotOverrideMe('/private/settings')

REST_FRAMEWORK = DoNotOverrideMe({
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'tickets.authentication.BusinessProcessAuthentication',
    ),
    'PAGINATE_BY': 20
})
# Rules to choose css classes for ticket item in tickets list
# maps (state, type) to class
# recommended classes: success, warning, danger, info, default
# "*" instead of state and type is used as wildcard.
# priority of rule (state, "*") > priority of rule  ("*", type) > priority of rule ("*", "*")
TICKET_MOODS = DoNotOverrideMe({
    ("new", "notification"): "success",
    ("new", "task"): "warning",
    ("new", "bad_notification"): "danger",
    ("new", "*"): "info",
    ("*", "*"): "default"
})

# Rules to choose phrase on button that changes ticket state locally
# Maps (type, from_state, to_state) to phrase.
# {to_state} in phrase will be replaced to new state name, {from_state} - to old state name
# Priorities (note that order differs from TICKET_MOODS):
# (type, from_state, to_state) >
# > ("*", from_state, to_state) >
# > (type, "*", to_state) >
# > ("*", "*", to_state) >
# > (type, from_state, "*") >
# > ("*", from_state, "*") >
# > (type, "*", "*") >
# > ("*", "*", "*")
STATE_CHANGE_PHRASES = DoNotOverrideMe({
    ("notification", "new", "closed"): "Отметить прочитанным",
    ("notification", "closed", "new"): "Отметить непрочитанным",
    ("bad_notification", "new", "closed"): "Отметить прочитанным",
    ("bad_notification", "closed", "new"): "Отметить непрочитанным",
    ("*", "*", "*"): """В состояние \"{to_state}\"""",
})

# Rules to determine if ticket is active (affects calculation
# the number of active tickets in navbar).
# Rule is looks like (state, type) and "*" is used as a wildcard.
# All rules are joined by logic OR.
ACTIVE_TICKETS = DoNotOverrideMe([
    ("new", "*")
])

# Rules to select css classes for comment
# maps commentator_role to class
COMMENT_MOODS = DoNotOverrideMe({
    "verifier": "warning",
    "author": "success",
    "*": "default"
})

BASE_URL = OverrideMe("http://localhost:8000")

EMAIL_HOST = OverrideMe('smtp.yandex.ru')

EMAIL_PORT = OverrideMe(465)

EMAIL_USE_SSL = OverrideMe(True)

EMAIL_HOST_USER = OverrideMe('polyana.web')

EMAIL_HOST_PASSWORD = OverrideMe('rjhgjhfwbz')

EMAIL_FROM = OverrideMe('Рабочий офис СПбПУ <polyana.web@yandex.ru>')

SERVER_EMAIL = OverrideMe('polyana.web@yandex.ru')

EMAIL_TAG = OverrideMe('Рабочий офис')

TICKETS_CLIENT_API_ROOT = OverrideMe('http://localhost:8000/tickets-api')

STATIC_ROOT = DoNotOverrideMe(os.path.join(BASE_DIR, 'collected_static'))

COMPRESS_ENABLED = DoNotCare(True)

COMPRESS_OFFLINE = DoNotCare(True)

LOG_ROOT = DoNotCare(os.path.join(BASE_DIR, "log"))

LOG_HANDLERS = DoNotCare(['console', 'logfile', ])

DEBUG_TRUE_LOG_LEVEL = DoNotCare('INFO')

DEBUG_FALSE_LOG_LEVEL = DoNotCare('INFO')


__base_url = BASE_URL.underlying_object

BUSINESS_PROCESSES = OverrideMe({
    # This one will be taken by backend directly from settings (AUTHENTICATION_BP, not from DB)!
    "polyauthentication": [{
        "username": "polyauthentication",
        "password": "12345",
        "verbose_name": "Аутентификация",
        "url": __base_url,
        "remote_id": 1
    }],
    "conference": [{
        "username": "conference",
        "password": "12345",
        "verbose_name": "Конференции",
        "url": __base_url,
        "remote_id": 2
    }],
    "studcontingent": [{
        "username": "studcontingent",
        "password": "12345",
        "verbose_name": "Контингент студентов",
        "url": __base_url,
        "remote_id": 3
    }],
    "rights_interface": [{
        "username": "rights_interface",
        "password": "12345",
        "verbose_name": "Редактирование прав",
        "url": __base_url,
        "remote_id": 4
    }],
    "grant": [{
        "username": "grant",
        "password": "12345",
        "verbose_name": "Конкурсы и гранты",
        "url": __base_url,
        "remote_id": 5
    }],
    "patent": [{
        "username": "patent",
        "password": "12345",
        "verbose_name": "Патенты",
        "url": __base_url,
        "remote_id": 6
    }],
    "funding": [{
        "username": "funding",
        "password": "12345",
        "verbose_name": "Источники финансирования",
        "url": __base_url,
        "remote_id": 7
    }],
    "trips": [{
        "username": "trips",
        "password": "12345",
        "verbose_name": "Командировки",
        "url": __base_url,
        "remote_id": 8
    }],
    "publication": [{
        "username": "publication",
        "password": "12345",
        "verbose_name": "Публикации",
        "url": __base_url,
        "remote_id": 9
    }],
    "editboard": [{
        "username": "editboard",
        "password": "12345",
        "verbose_name": "Редколлегии журналов",
        "url": __base_url,
        "remote_id": 10
    }],
    "reports": [{
        "username": "reports",
        "password": "12345",
        "verbose_name": "Отчеты",
        "url": __base_url,
        "remote_id": 11
    }],
    "disscouncil": [{
        "username": "disscouncil",
        "password": "12345",
        "verbose_name": "Диссертационные советы",
        "url": __base_url,
        "remote_id": 12
    }],
    "contract": [{
        "username": "contract",
        "password": "12345",
        "verbose_name": "Контракты",
        "url": __base_url,
        "remote_id": 13
    }],
    "employee": [
        {
            "username": "employee",
            "password": "12345",
            "verbose_name": "Сотрудники",
            "url": __base_url,
            "remote_id": 14,
        },
        {
            "username": "self",
            "password": "12345",
            "verbose_name": "self",
            "url": __base_url,
            "remote_id": 21
        }
    ],
    "postgraduate": [{
        "username": "postgraduate",
        "password": "12345",
        "verbose_name": "Аспиранты",
        "url": __base_url,
        "remote_id": 15,
    }],
    "location": [{
        "username": "location",
        "password": "12345",
        "verbose_name": "Помещения",
        "url": __base_url,
        "remote_id": 16,
    }],
    "uiu": [{
        "username": "uiu",
        "password": "12345",
        "verbose_name": "UIU",
        "url": __base_url,
        "remote_id": 17
    }],
    "staff_unit": [{
        "username": "staff_unit",
        "password": "12345",
        "verbose_name": "Штатное расписание",
        "url": __base_url,
        "remote_id": 18
    }],
    "tag": [{
        "username": "tag",
        "password": "12345",
        "verbose_name": "Теги",
        "url": __base_url,
        "remote_id": 19
    }],
    "division": [
        {
            "username": "division",
            "password": "12345",
            "verbose_name": "Подразделения",
            "url": __base_url,
            "remote_id": 20
        },
        {
            "username": "division_passport",
            "password": "12345",
            "verbose_name": "Паспорт подразделения",
            "url": __base_url,
            "remote_id": 22
        },
    ],
    "student": [{
        "username": "student",
        "password": "12345",
        "verbose_name": "Студенты",
        "url": __base_url,
        "remote_id": 23
    }],
    "equipment": [{
        "username": "equipment",
        "password": "12345",
        "verbose_name": "Оборудование",
        "url": __base_url,
        "remote_id": 24,
    }],
    "people": [{
        "username": "people",
        "password": "12345",
        "verbose_name": "Люди",
        "url": __base_url,
        "remote_id": 25,
    }],
    "info": [{
        "username": "static_pages",
        "password": "12345",
        "verbose_name": "Статические страницы",
        "url": __base_url,
        "remote_id": 26,
    }],
    "mooc": [{
        "username": "mooc",
        "password": "12345",
        "verbose_name": "МООК",
        "url": __base_url,
        "remote_id": 27,
    }],
    "discharge": [{
        "username": "discharge",
        "password": "12345",
        "verbose_name": "Таблички имени Головина",
        "url": __base_url,
        "remote_id": 28,
    }],
})

AUTHENTICATION_BP = DoNotCare(BUSINESS_PROCESSES["polyauthentication"][0])

BULK_SIZE = DoNotCare(300)

MAIN_MENU = DoNotOverrideMe([
    {
        "name": "Наука",
        "subgroups": [
            {
                "name": "Публикации",
                "items": [
                    ("Каталог публикаций", "publication:available_publications"),
                ],
                "bp": "publication"
            },
            {
                "name": "НИОКР",
                "items": [
                    ("Каталог НИОКР", "contract:available_contracts")
                ],
                "bp": "contract"
            },
            {
                "name": "Объекты интеллектуальной собственности",
                "items": [
                    ("Каталог заявок на ОИС", "patent:available_pendpats"),
                    ("Каталог ОИС", "patent:available_patents")
                ],
                "bp": "patent"
            },
            {
                "name": "Аспиранты / докторанты / соискатели",
                "items": [("Мои аспиранты и др.", "postgraduate:list_postgraduates_my")],
                "bp": "self"
            },
            {
                "name": "Конференции",
                "items": [
                    ("Каталог конференций", "conference:available_conferences"),
                    ("Участия в конференциях", "conference:available_confparts"),
                ],
                "bp": "conference"
            },
            {
                "name": "Конференции",
                "items": [("Участия в конференциях", "conference:my_confparts")],
                "bp": "self"
            },
            {
                "name": "Конкурсы и гранты",
                "items": [
                    ("Каталог конкурсов и грантов", "grant:grant_list"),
                    ("Участия в конкурсах и грантах", "grant:grantpart_available")
                ],
                "bp": "grant"
            },
            {
                "name": "Редколлегии журналов",
                "items": [
                    ("Список редколлегий", "editboard:available_editboards")
                ],
                "bp": "editboard"
            },
            {
                "name": "Диссертационные советы",
                "items": [
                    ("Список членов советов", "disscouncil:available_disscouncil_members"),
                    ("Список советов", "disscouncil:available_disscouncils")
                ],
                "bp": "disscouncil"
            },
        ]
    },
    {
        "name": "Образование",
        "subgroups": [
            {
                "name": "Аспиранты / докторанты / соискатели",
                "items": [("Список аспирантов и др.", "postgraduate:list_postgraduates")],
                "bp": "postgraduate",
            },
            {
                "items": [("Студенты", "student:student_list")],
                "bp": "student"
            },
            {
                "items": [("МООК", "mooc:mooc_list")],
                "bp": "mooc"
            },

        ]
    },
    {
        "name": "Кадры",
        "subgroups": [
            {
                "items": [("Сотрудники", "employee:list_employees")],
                "bp": "employee"
            },
            {
                "items": [("Штатное расписание", "staff_unit:staff_unit_list")],
                "bp": "staff_unit"
            },
            {
                "items": [("Командировки", "trips:main")],
                "bp": "trips"
            },
            {
                "items": [("Подразделения", "division:division_tree")],
                "bp": "division"
            },
            {
                "items": [("Поиск людей", "people:search")],
                "bp": "people"
            },
        ]
    },
    {
        "name": "МИК",
        "subgroups": [
            {
                "items": [("Помещения", "location:available_locations")],
                "bp": "location"
            },
            {
                "items": [("Имущество", "equipment:list")],
                "bp": "equipment"
            },
        ]
    },
    {
        "name": "Отчеты",
        "url": "reports:main",
        "bp": "reports"
    },
    {
        "name": "Сервис",
        "subgroups": [
            {
                "items": [("Войти как...", "polyauth:login_as")],
                "login_as_permission": True
            },
            {
                "items": [("Назначение прав", "rights:main-interface")],
                "bp": "rights_interface"
            },
            {
                "items": [("Источники финансирования", "funding:funding_list")],
            },
            {
                "name": " ",
                "items": [
                    ("Создать новость", "news:create"),
                    ("Журнал событий", "polylog:log_list")
                ],
            },
            {
                "name": "Журналы",
                "items": [
                    ("Список журналов", "publication:journals"),
                ],
            },
            {
                "name": "Отчёты",
                "items": [
                        ("Просмотреть", "reports:listreports"),
                        ("Добавить", "reports:addreport"),
                ],
            },
            {
                "name": "Теги",
                "items": [
                    ("Управление тегами", "tag:list_tags"),
                ],
            },
            {
                "name": "Страницы помощи",
                "items": [
                    ("Просмотреть", "help:index"),
                    ("Добавить", "help:create"),
                ],
            },
            {
                "name": "Выгрузки",
                "items": [
                    ("Базовые параметры", "discharge:parameters"),
                    ("Шаблоны отчётов", "discharge:report_list"),
                    ("Отчёты по выгрузкам", "discharge:report_instance_list_all"),
                ],
                "bp": "discharge",
            },
        ]
    },
    {
        "name": "Рейтинги",
        "url": "info:ratings",
        "bp": "static_pages"
    }
])

DISABLED_BPS = DoNotCare(set())

# ------------------ CKEditor settings ------------------

CKEDITOR_CONFIGS = DoNotOverrideMe({
    'default': {
        'skin': 'moono',
        'toolbar_polyana': [
            {'name': 'document', 'items': ['Source', '-', 'Save', 'NewPage', 'Preview', 'Print', '-', 'Templates']},
            {'name': 'clipboard', 'items': ['Cut', 'Copy', 'Paste', 'PasteText', '-', 'Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace']},
            '/',
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            '/',
            {'name': 'basicstyles',
             'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar']},
            {'name': 'tools', 'items': ['Preview', 'Maximize', 'ShowBlocks']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'BidiLtr', 'BidiRtl',
                       'Language']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
        ],
        'toolbar': 'polyana',
        'toolbarGroups': [{ 'name': 'document', 'groups': [ 'mode', 'document', 'doctools' ] }],
        'width': '100%',
        'filebrowserWindowHeight': 725,
        'filebrowserWindowWidth': 940,
        'toolbarCanCollapse': True,
        'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'allowedContent': True,
        'extraPlugins': ','.join(
            [
                'div',
                'autolink',
                'autoembed',
                'embedsemantic',
                'autogrow',
                'widget',
                'lineutils',
                'clipboard',
                'dialog',
                'dialogui',
                'elementspath'
            ]),
    }
})

# ------------------ Scopus import settings ------------------

INTERNAL_AFF_ID = DoNotCare(60017103)
SCOPUS_API_KEY = OverrideMe("4c77d808458bbf1a7ae2217f536d4f2d")
SCOPUS_DOWNLOAD_PATH = DoNotOverrideMe(os.path.join(BASE_DIR, "scopus_data"))
WOS_DOWNLOAD_PATH = DoNotOverrideMe(os.path.join(BASE_DIR, "wos_data"))
MANAGEMENT_USER_NAME = OverrideMe("mpetrov")
MANAGEMENT_USER_PASS = OverrideMe("Qwerty123")
MANAGEMENT_BP_NAME = OverrideMe("conference")
MANAGEMENT_BP_PASS = OverrideMe("12345")

UIU_IGNORED_MODELS = DoNotOverrideMe({
    "Employee": {
        "00000"
    },
    "StaffUnit": {
        0
    }
})

CAS_URL = OverrideMe("https://localhost/cas")
PENTAHO_URL = OverrideMe("https://localhost/pentaho")
CAS_PENTAHO_SEC_CHECK = DoNotOverrideMe("j_spring_cas_security_check")

XLSX_ROOT = DoNotOverrideMe(os.path.join(BASE_DIR, "xlsx_dumps/"))

########################################################################################################################
# Overriding variables by local_settings.py
########################################################################################################################
__not_to_override = []

__vars_copy = vars().copy()

# Variables to ignore during override checking
__ignore_policy = ["__package__",
                   "__file__",
                   "__name__",
                   "__loader__",
                   "__spec__",
                   "__doc__",
                   "__builtins__",
                   "__cached__",
                   "__not_to_override",
                   "__base_url"
                   ]


for setting in __vars_copy:
    val = __vars_copy[setting]
    # Ignoring everything that is not a settings value
    if setting in __ignore_policy or isinstance(val, (type, ModuleType, FunctionType)):
        continue

    # Saving settings that should not be overriden
    if isinstance(val, DoNotOverrideMe):
        __not_to_override.append(setting)

    # Checking for raw values in settings.py
    if not isinstance(val, OverrideProxy):
        print("Settings warning: please specify override policy for setting {} ".format(setting))
        print("Settings warning: Override policy should be one of OverrideMe, DoNotOverrideMe or DoNotCare")

try:
    from merger.local_settings import *
except ImportError:
    print("No local settings found!")
    pass
########################################################################################################################

########################################################################################################################
# Variables set below depends on variables that are set by local settings
########################################################################################################################
__debug_log_level = DoNotCare(DEBUG_TRUE_LOG_LEVEL if DEBUG else DEBUG_FALSE_LOG_LEVEL)

LOGGING = DoNotCare({
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_ROOT + '/logfile.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 1000,
            'encoding': 'utf8',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'commands_logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_ROOT + '/commands.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 100,
            'encoding': 'utf8',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'polyana_web': {
            'handlers': LOG_HANDLERS,
            'level': 'INFO',
            'formatter': 'verbose'
        },
    }
})

print("Performing settings checks...")


__new_vars_copy = vars().copy()
for setting in __new_vars_copy:
    val = vars()[setting]
    if setting in __not_to_override and not isinstance(val, DoNotOverrideMe):
        print("Settings warning: you are overriding setting {} "
              "in your local settings which you probably should not do".format(setting))
    elif isinstance(val, OverrideMe):
        print("Settings warning: you are not overriding setting {} "
              "in your local settings which you probably should do. Using fallback value.".format(setting))

    if isinstance(val, OverrideProxy):
        vars()[setting] = val.underlying_object

print("Settings checks done.")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%f)r^nv8qcnegaacc$5-tuvy7--l!3pm0ej%bs+cibil9+c**#'

