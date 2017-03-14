# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0015_auto_20160220_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialPoint',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('number', models.CharField(verbose_name='номер мат.точки', max_length=32)),
            ],
            options={
                'verbose_name': 'материальная точка',
                'verbose_name_plural': 'материальные точки',
                'managed': False,
                'abstract': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
