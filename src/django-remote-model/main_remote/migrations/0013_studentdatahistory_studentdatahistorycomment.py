# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0012_student_studentdata_studenteducationform_studentexam_studentexamtype_studentgeneration_studentgroup_'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentDataHistory',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('activity_from', models.DateField(null=True, blank=True)),
                ('activity_to', models.DateField(null=True, blank=True)),
                ('contract', models.BooleanField(verbose_name='контрактный студент', default=False)),
                ('valid_from', models.DateField(null=True, verbose_name='дата поступления')),
                ('valid_to', models.DateField(null=True, verbose_name='дата отчисления')),
                ('purpose', models.BooleanField(verbose_name='целевое назначение', default=False)),
                ('purpose_org', models.CharField(null=True, verbose_name='заказчик целевого назначения', max_length=255)),
                ('diploma_date', models.DateField(null=True, verbose_name='дата защиты')),
                ('diploma_result', models.CharField(null=True, verbose_name='результат защиты', max_length=255)),
            ],
            options={
                'verbose_name': 'история данных о студенте',
                'managed': False,
                'abstract': False,
                'verbose_name_plural': 'история данных о студентах',
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StudentDataHistoryComment',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, blank=True)),
                ('report_date', models.DateField(verbose_name='дата приказа')),
                ('comment', models.CharField(verbose_name='комментарий', max_length=255)),
                ('report', models.CharField(verbose_name='номер приказа', max_length=255)),
            ],
            options={
                'managed': False,
                'abstract': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
