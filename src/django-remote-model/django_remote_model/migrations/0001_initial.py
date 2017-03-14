# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RemoteCoreResultModel',
            fields=[
                ('primary_key', models.AutoField(primary_key=True, serialize=False)),
                ('remote_id', models.IntegerField(blank=True, null=True)),
                ('version', models.IntegerField(blank=True, null=True)),
                ('validity_from', models.DateTimeField(blank=True, null=True)),
                ('validity_to', models.DateTimeField(blank=True, null=True)),
                ('activity_from', models.DateTimeField(blank=True, null=True)),
                ('activity_to', models.DateTimeField(blank=True, null=True)),
                ('internal_id', models.CharField(blank=True, max_length=64, null=True)),
                ('external_id', models.CharField(blank=True, max_length=64, null=True)),
                ('type_kind', models.CharField(max_length=64, choices=[('DATA', 'DATA'), ('DICTIONARY', 'DICTIONARY'), ('FINANCE', 'FINANCE')])),
                ('verification_status', models.CharField(default='NEVER', max_length=64, choices=[('NEVER', 'NEVER'), ('APPROVED', 'APPROVED'), ('DECLINED', 'DECLINED'), ('CHANGED', 'CHANGED')])),
                ('verification_comment', models.CharField(blank=True, max_length=1024, null=True)),
                ('parents', models.ManyToManyField(to='django_remote_model.RemoteCoreResultModel', related_name='children')),
            ],
            options={
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
