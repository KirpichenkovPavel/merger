# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20170203_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupRecord',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('last_name', models.CharField(max_length=255, null=True)),
                ('first_name', models.CharField(max_length=255, null=True)),
                ('middle_name', models.CharField(max_length=255, null=True)),
                ('birth_date', models.DateField(null=True)),
                ('group', models.ForeignKey(to='main.Group')),
                ('hypostasis', models.ForeignKey(to='main.Hypostasis')),
                ('person', models.ForeignKey(to='main.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
