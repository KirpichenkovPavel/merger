# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20170505_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouprecord',
            name='group',
            field=models.ForeignKey(null=True, to='main.Group', related_name='group_record_set'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='hypostasis',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, to='main.Person'),
            preserve_default=True,
        ),
    ]
