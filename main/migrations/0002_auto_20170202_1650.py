# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hypostasis',
            name='id',
            field=models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='id',
            field=models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False),
            preserve_default=True,
        ),
    ]
