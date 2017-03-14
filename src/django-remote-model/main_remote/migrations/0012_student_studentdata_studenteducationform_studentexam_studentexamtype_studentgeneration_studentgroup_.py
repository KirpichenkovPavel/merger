# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models
import main_remote.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0011_building_locationkind_locationkindgroup_locationnormkind_parcel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('last_name', models.CharField(max_length=255, verbose_name='фамилия')),
                ('first_name', models.CharField(max_length=255, verbose_name='имя')),
                ('middle_name', models.CharField(max_length=255, verbose_name='отчество', null=True)),
                ('gender', models.CharField(max_length=1, verbose_name='пол')),
                ('date_birth', models.DateField(verbose_name='дата рождения', null=True)),
                ('region', models.CharField(max_length=255, verbose_name='регион')),
                ('email', models.CharField(max_length=255, verbose_name='email', null=True)),
                ('phone', models.CharField(max_length=255, verbose_name='телефон', null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'студент',
                'verbose_name_plural': 'студенты',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel, main_remote.mixins.NamedPersonMixin),
        ),
        migrations.CreateModel(
            name='StudentData',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('contract', models.BooleanField(default=False, verbose_name='контрактный студент')),
                ('valid_from', models.DateField(verbose_name='дата поступления')),
                ('valid_to', models.DateField(verbose_name='дата отчисления')),
                ('purpose', models.BooleanField(default=False, verbose_name='целевое назначение')),
                ('purpose_org', models.CharField(max_length=255, verbose_name='заказчик целевого назначения')),
                ('diploma_date', models.DateField(verbose_name='дата защиты')),
                ('diploma_result', models.CharField(max_length=255, verbose_name='результат защиты')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'данные о студенте',
                'verbose_name_plural': 'данные о студентах',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentEducationForm',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='название')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'форма обучения',
                'verbose_name_plural': 'формы обучения',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentExam',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('value', models.IntegerField(verbose_name='баллы')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'экзамен',
                'verbose_name_plural': 'экзамены',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentExamType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='название')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'тип экзамена',
                'verbose_name_plural': 'типы экзаменов',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentGeneration',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='название')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'поколение стандарта',
                'verbose_name_plural': 'поколение стандартов',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentGroup',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('number', models.CharField(max_length=255, verbose_name='название')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'учебная группа',
                'verbose_name_plural': 'учебные группы',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentPrivilege',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='название')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'тип льготников',
                'verbose_name_plural': 'типы льготников',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentState',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='название')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'статус студента',
                'verbose_name_plural': 'статусы студента',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
