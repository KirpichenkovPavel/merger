# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20170202_1941'),
    ]

    operations = [
        migrations.RenameField(
            model_name='hypostasis',
            old_name='person_id',
            new_name='person',
        ),
    ]
