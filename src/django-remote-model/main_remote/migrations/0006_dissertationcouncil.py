# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0005_staffunit'),
    ]

    operations = [
        migrations.CreateModel(
            name='DissertationCouncil',
            fields=[
                ('id', models.IntegerField(serialize=False, blank=True, primary_key=True)),
                ('code', models.CharField(verbose_name='шифр совета', max_length=255)),
                ('date_from', models.DateField(verbose_name='дата открытия')),
                ('date_to', models.DateField(verbose_name='дата закрытия', null=True)),
            ],
            options={
                'verbose_name': 'диссертационный совет',
                'managed': False,
                'verbose_name_plural': 'диссертационные советы',
                'abstract': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
