# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_group_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grouprecord',
            name='group',
            field=models.ForeignKey(to='main.Group', null=True),
            preserve_default=True,
        ),
    ]
