# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20170518_1952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouprecord',
            name='forbidden_groups',
            field=models.ManyToManyField(related_name='forbidden_group_record_set', to='main.Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='grouprecord',
            name='group',
            field=models.ForeignKey(to='main.Group', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
