# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0013_studentdatahistory_studentdatahistorycomment'),
    ]

    operations = [
        migrations.CreateModel(
            name='FiasAddress',
            fields=[
                ('id', models.IntegerField(blank=True, serialize=False, primary_key=True)),
                ('region_code', models.CharField(max_length=2, verbose_name='код региона')),
                ('formal_name', models.CharField(max_length=100, verbose_name='название')),
                ('short_name', models.CharField(max_length=50)),
                ('guid', models.CharField(max_length=100)),
                ('act_status', models.IntegerField(verbose_name='статус')),
                ('level', models.IntegerField(verbose_name='уровень')),
            ],
            options={
                'verbose_name_plural': 'адресные объекты',
                'abstract': False,
                'verbose_name': 'адресный объект',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='PostgraduateProgram',
            fields=[
                ('id', models.IntegerField(blank=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=500, verbose_name='наименование')),
                ('code', models.CharField(max_length=20, verbose_name='код')),
                ('type', models.CharField(max_length=20, choices=[('GRADUATE_AREA', 'направление аспирантуры'), ('GRADUATE_SPECIALITY', 'специальность аспирантуры')], verbose_name='направление')),
            ],
            options={
                'verbose_name_plural': 'специальности',
                'abstract': False,
                'verbose_name': 'специальность',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentProgram',
            fields=[
                ('id', models.IntegerField(blank=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=500, verbose_name='наименование')),
                ('code', models.CharField(max_length=20, verbose_name='код')),
                ('type', models.CharField(max_length=20, choices=[('BACHELOR', 'бакалавриат'), ('MASTER', 'магистратура'), ('SPECIALIST', 'специалитет')], verbose_name='направление')),
            ],
            options={
                'verbose_name_plural': 'специальности',
                'abstract': False,
                'verbose_name': 'специальность',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
