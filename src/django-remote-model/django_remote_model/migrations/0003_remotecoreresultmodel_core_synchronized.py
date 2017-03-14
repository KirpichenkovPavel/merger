# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_remote_model', '0002_remotecoreresultmodel_result_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='remotecoreresultmodel',
            name='core_synchronized',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
