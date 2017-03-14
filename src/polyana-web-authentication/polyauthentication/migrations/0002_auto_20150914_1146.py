# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('polyauthentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='polyuser',
            name='expiration_date',
            field=models.DateTimeField(blank=True, null=True, default=None, verbose_name='срок действия'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='polyuser',
            name='is_fake',
            field=models.BooleanField(verbose_name='является служебным', default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='polyuser',
            name='employee',
            field=django_remote_model.models.RemoteForeignKey(null=True, verbose_name='сотрудник', related_name='users', to='main_remote.Employee', db_constraint=False),
            preserve_default=True,
        ),
    ]
