# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_group_birth_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='person',
            field=models.ForeignKey(to='main.Person', null=True),
            preserve_default=True,
        ),
    ]
