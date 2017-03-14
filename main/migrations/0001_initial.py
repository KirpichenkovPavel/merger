# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hypostasis',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('employee_id', models.IntegerField(unique=True)),
                ('student_id', models.IntegerField(unique=True)),
                ('postgraduate_id', models.IntegerField(unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=200)),
                ('middle_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('birth_date', models.DateField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='hypostasis',
            name='person_id',
            field=models.ForeignKey(to='main.Person'),
            preserve_default=True,
        ),
    ]
