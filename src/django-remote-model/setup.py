from distutils.core import setup

setup(
    name='django_remote_model',
    version='0.12.86',
    author='Digitek Labs',
    author_email='maxim.petrov@kspt.icc.spbstu.ru',
    packages=['django_remote_model',
              'django_remote_model.util',
              'django_remote_model.migrations',
              'core_client',
              'nsi_client',
              'ldap_proxy_client',
              'remote_impl',
              'main_remote',
              'main_remote.migrations',
              'polyauth_remote',
              'polyauth_remote.migrations'],
    install_requires=[
        'Django>=1.7,<1.8',
        'aiohttp==0.21.6',
        'requests==2.6.0',
        'jsonfield',
        'django-crequest',
        'asyncio==3.4.3'
    ]
)
