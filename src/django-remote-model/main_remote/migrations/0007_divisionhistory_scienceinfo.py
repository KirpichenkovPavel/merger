# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0006_dissertationcouncil'),
    ]

    operations = [
        migrations.CreateModel(
            name='DivisionHistory',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('activity_from', models.DateField(blank=True, null=True)),
                ('activity_to', models.DateField(blank=True, null=True)),
                ('name', models.CharField(verbose_name='название', max_length=300)),
                ('full_name', models.CharField(verbose_name='полное название', max_length=300)),
                ('abbrv', models.CharField(verbose_name='аббревиатура', max_length=300)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField(null=True)),
                ('code1', models.CharField(verbose_name='код 1', max_length=2, null=True)),
                ('code2', models.CharField(verbose_name='код 2', max_length=2, null=True)),
            ],
            options={
                'verbose_name': 'история подразделения',
                'abstract': False,
                'verbose_name_plural': 'история подразделений',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='ScienceInfo',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'внешняя информация о сотруднике',
                'abstract': False,
                'verbose_name_plural': 'внешняя информация о сотрудниках',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
