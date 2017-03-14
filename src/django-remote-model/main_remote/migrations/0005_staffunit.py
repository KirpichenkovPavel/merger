# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0004_postgraduatecategory_postgraduatefirereason_postgraduatesupervisor'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffUnit',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('part', models.FloatField(verbose_name='ставка')),
                ('date_start', models.DateTimeField(verbose_name='дата начала')),
                ('date_end', models.DateTimeField(verbose_name='дата конца', null=True)),
            ],
            options={
                'verbose_name': 'штатная единица',
                'abstract': False,
                'managed': False,
                'verbose_name_plural': 'штатные единицы',
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
