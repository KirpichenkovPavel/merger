# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20170510_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouprecord',
            name='forbidden_group_records',
            field=models.ManyToManyField(related_name='forbidden_group_records_rel_+', to='main.GroupRecord'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='grouprecord',
            name='forbidden_groups',
            field=models.ManyToManyField(to='main.Group'),
            preserve_default=True,
        ),
    ]
