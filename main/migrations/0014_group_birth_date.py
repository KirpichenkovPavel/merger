# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20170518_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='birth_date',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
