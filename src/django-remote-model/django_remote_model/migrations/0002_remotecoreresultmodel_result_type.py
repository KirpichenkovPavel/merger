# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0001_initial'),
        ('django_remote_model', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='remotecoreresultmodel',
            name='result_type',
            field=django_remote_model.models.RemoteForeignKey(db_constraint=False, to='main_remote.CoreResultType'),
            preserve_default=True,
        ),
    ]
