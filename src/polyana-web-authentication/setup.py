from distutils.core import setup

setup(
    name='polyana_web_authentication',
    version='0.0.13',
    author='Kirill Gagarski',
    author_email='gagarski@kspt.icc.spbstu.ru',
    packages=['polyauthentication', 'django_auth_ldap', 'polyauthentication.migrations'],
    install_requires=[
        "django >=1.7,<1.8",
        "prettyprint",
#        "django_remote_model",  # TODO: think about correct handling of that dependencies
#        "main_remote",
#        "python-ldap >= 2.0", # Install it manually from git!
    ],
    setup_requires=[
        "setuptools >= 0.6c11",
    ],
    tests_require=[
        "mockldap >= 0.2",
    ]
)
