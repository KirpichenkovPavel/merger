# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20170202_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hypostasis',
            name='employee_id',
            field=models.CharField(unique=True, null=True, max_length=255),
            preserve_default=True,
        ),
    ]
