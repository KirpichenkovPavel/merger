# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0010_scienceinfoelement'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.CharField(blank=True, max_length=255, serialize=False, primary_key=True)),
                ('name', models.CharField(null=True, max_length=255, verbose_name='Название')),
                ('address', models.CharField(null=True, max_length=255, verbose_name='Адрес')),
                ('cadastr_num', models.CharField(null=True, max_length=255, verbose_name='Кадастровый номер')),
                ('build_year', models.CharField(null=True, max_length=255, verbose_name='Год постройки')),
                ('floors', models.CharField(null=True, max_length=255, verbose_name='Этажность')),
                ('space', models.FloatField(null=True, verbose_name='Суммарная площадь')),
            ],
            options={
                'verbose_name_plural': 'здания',
                'verbose_name': 'здание',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='LocationKind',
            fields=[
                ('id', models.IntegerField(blank=True, serialize=False, primary_key=True)),
                ('name', models.CharField(null=True, max_length=255, verbose_name='название')),
            ],
            options={
                'verbose_name_plural': 'категория исп. помещения',
                'verbose_name': 'категория исп. помещения',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='LocationKindGroup',
            fields=[
                ('id', models.IntegerField(blank=True, serialize=False, primary_key=True)),
                ('name', models.CharField(null=True, max_length=255, verbose_name='название')),
                ('description', models.CharField(null=True, max_length=255, verbose_name='описание')),
            ],
            options={
                'verbose_name_plural': 'группы категорий исп. помещения',
                'verbose_name': 'группа категорий исп. помещения',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='LocationNormKind',
            fields=[
                ('id', models.IntegerField(blank=True, serialize=False, primary_key=True)),
                ('name', models.CharField(null=True, max_length=255, verbose_name='название')),
            ],
            options={
                'verbose_name_plural': 'категории норм. использования помещения',
                'verbose_name': 'категория норм. использования помещения',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.CharField(blank=True, max_length=255, serialize=False, primary_key=True)),
                ('cadastr_num', models.CharField(null=True, max_length=255, verbose_name='Кадастровый номер')),
                ('address', models.CharField(verbose_name='Адрес', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'земельные участки',
                'verbose_name': 'земельный участок',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
