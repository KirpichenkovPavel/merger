# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_group_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouprecord',
            name='instance_type',
            field=models.CharField(default='', max_length=255),
            preserve_default=True,
        ),
    ]
