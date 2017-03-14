# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models
import django.core.validators
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0001_initial'),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolyUser',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(verbose_name='username', help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')], unique=True)),
                ('first_name', models.CharField(blank=True, verbose_name='first name', max_length=30)),
                ('last_name', models.CharField(blank=True, verbose_name='last name', max_length=30)),
                ('email', models.EmailField(blank=True, verbose_name='email address', max_length=75)),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status', help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, verbose_name='active', help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('middle_name', models.CharField(blank=True, verbose_name='отчество', max_length=30)),
                ('employee', django_remote_model.models.RemoteOneToOneField(related_name='user', verbose_name='сотрудник', to='main_remote.Employee', null=True, db_constraint=False)),
                ('groups', models.ManyToManyField(to='auth.Group', blank=True, verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', related_query_name='user', related_name='user_set')),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', blank=True, verbose_name='user permissions', help_text='Specific permissions for this user.', related_query_name='user', related_name='user_set')),
            ],
            options={
                'verbose_name': 'user',
                'abstract': False,
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
    ]
