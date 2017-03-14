# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0003_academicrank'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostgraduateCategory',
            fields=[
                ('id', models.IntegerField(primary_key=True, blank=True, serialize=False)),
                ('name', models.CharField(max_length=500, null=True, verbose_name='название')),
            ],
            options={
                'managed': False,
                'verbose_name_plural': 'категории аспиранта',
                'abstract': False,
                'verbose_name': 'категория аспиранта',
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='PostgraduateFireReason',
            fields=[
                ('id', models.IntegerField(primary_key=True, blank=True, serialize=False)),
                ('name', models.CharField(max_length=500, null=True, verbose_name='название')),
            ],
            options={
                'managed': False,
                'verbose_name_plural': 'причины отчисления аспиранта',
                'abstract': False,
                'verbose_name': 'причина отчисления аспиранта',
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='PostgraduateSupervisor',
            fields=[
                ('id', models.IntegerField(primary_key=True, blank=True, serialize=False)),
                ('last_name', models.CharField(max_length=500, verbose_name='фамилия')),
                ('first_name', models.CharField(max_length=500, verbose_name='имя')),
                ('middle_name', models.CharField(max_length=500, null=True, verbose_name='отчество')),
                ('gender', models.CharField(max_length=1, null=True, verbose_name='пол')),
                ('date_birth', models.DateField(null=True, verbose_name='дата рождения')),
                ('dep_id', models.IntegerField(null=True)),
                ('is_staff', models.BooleanField(default=True, verbose_name='является сотрудником')),
            ],
            options={
                'managed': False,
                'verbose_name_plural': 'руководители аспирантов',
                'abstract': False,
                'verbose_name': 'руководитель аспиранта',
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
