# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20170504_1832'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='number',
        ),
        migrations.AddField(
            model_name='group',
            name='inconsistent',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
