# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('building', models.CharField(verbose_name='Корпус', max_length=500)),
                ('floor', models.CharField(verbose_name='Этаж', max_length=500)),
                ('number', models.CharField(verbose_name='Номер', max_length=500)),
                ('usage', models.CharField(verbose_name='Использование', max_length=500)),
                ('category', models.CharField(verbose_name='Категория', choices=[('административное', 'административное'), ('арендуемое', 'арендуемое'), ('вспомогательное в жилом фонде', 'вспомогательное в жилом фонде'), ('жилое', 'жилое'), ('научно-исследовательское', 'научно-исследовательское'), ('неотапливаемое', 'неотапливаемое'), ('подсобное', 'подсобное'), ('подсобное в жилом фонде (моп)', 'подсобное в жилом фонде (моп)'), ('производственное', 'производственное'), ('специализированные помещения', 'специализированные помещения'), ('трансформаторные подстанции', 'трансформаторные подстанции'), ('учебное', 'учебное'), ('учебно-вспомогательное', 'учебно-вспомогательное'), ('учебно-лабораторное', 'учебно-лабораторное'), ('учебно-научное', 'учебно-научное')], max_length=500)),
                ('space', models.FloatField(verbose_name='Площадь')),
            ],
            options={
                'verbose_name': 'помещение',
                'managed': False,
                'verbose_name_plural': 'помещения',
                'abstract': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.IntegerField(primary_key=True, blank=True, serialize=False)),
                ('tag', models.CharField(verbose_name='Тег', max_length=255, primary_key=True, serialize=False)),
                ('description', models.CharField(verbose_name='Описание', max_length=255)),
            ],
            options={
                'managed': False,
                'abstract': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
