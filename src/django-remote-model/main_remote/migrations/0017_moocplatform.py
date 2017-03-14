# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0016_materialpoint'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoocPlatform',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, blank=True)),
                ('name', models.CharField(verbose_name='имя', max_length=255)),
                ('platform_url', models.URLField(verbose_name='URL', max_length=255)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'МООК-платформа',
                'managed': False,
                'verbose_name_plural': 'МООК-платформы',
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
