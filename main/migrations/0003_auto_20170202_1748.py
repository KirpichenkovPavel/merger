# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20170202_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hypostasis',
            name='employee_id',
            field=models.IntegerField(unique=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='hypostasis',
            name='person_id',
            field=models.ForeignKey(null=True, to='main.Person'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='hypostasis',
            name='postgraduate_id',
            field=models.IntegerField(unique=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='hypostasis',
            name='student_id',
            field=models.IntegerField(unique=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='person',
            name='birth_date',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
