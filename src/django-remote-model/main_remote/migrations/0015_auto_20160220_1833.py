# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0014_fiasaddress_postgraduateprogram_studentprogram'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.IntegerField(serialize=False, blank=True, primary_key=True)),
                ('number', models.CharField(max_length=100, verbose_name='номер')),
                ('valid_from', models.DateField(verbose_name='дата начала')),
                ('valid_to', models.DateField(verbose_name='дата окончания')),
            ],
            options={
                'abstract': False,
                'verbose_name_plural': 'лицевые счета',
                'verbose_name': 'лицевой счет',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.RemoveField(
            model_name='resultfundingmodel',
            name='funding',
        ),
        migrations.AddField(
            model_name='resultfundingmodel',
            name='account',
            field=django_remote_model.models.RemoteForeignKey(null=True, db_constraint=False, to='main_remote.Account'),
            preserve_default=True,
        ),
    ]
