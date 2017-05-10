# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20170508_2145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouprecord',
            name='person',
            field=models.ForeignKey(to='main.Person', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
