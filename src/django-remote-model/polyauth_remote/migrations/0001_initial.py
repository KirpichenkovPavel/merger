# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NsiRemotePermissionInst',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('type', models.CharField(verbose_name='право', max_length=2, choices=[('RD', 'чтение'), ('WR', 'запись')])),
                ('catalogue', models.CharField(verbose_name='каталог', max_length=50, choices=[('BUSINESSPROCESS', 'Бизнес-процессы'), ('EXTERNALEMPLOYEEINFO', 'Внешняя информация о сотруднике'), ('CITY', 'Города'), ('POST', 'Должности'), ('GRANT', 'Конкурсы и гранты'), ('GRANTCONTAINER', 'Контейнеры конкурсов и грантов'), ('CONFERENCE', 'Конференции'), ('APPOINTMENT', 'Назначения'), ('EDUCATIONPROGRAM', 'Образовательные программы'), ('ORGANIZATION', 'Организации'), ('DIVISION', 'Подразделения'), ('NSIPERMISSION', 'Права доступа к НСИ'), ('PERMISSION', 'Права доступа к РРД'), ('ROLE', 'Роли'), ('EMPLOYEE', 'Сотрудники'), ('COUNTRY', 'Страны'), ('TOPIC', 'Тематики конференций'), ('ACADEMIC', 'Учёные звания'), ('DEGREE', 'Учёные степени'), ('ROLETEMPLATE', 'Шаблоны ролей'), ('GRADUATE', 'Аспиранты'), ('ALL', '*')])),
            ],
            options={
                'verbose_name': 'назначение удаленного права в НСИ',
                'abstract': False,
                'verbose_name_plural': 'назначения удаленных прав в НСИ',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='RegistryRemotePermissionInst',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('type', models.CharField(verbose_name='право', max_length=255, choices=[('ALL', '*'), ('READ', 'Чтение'), ('WRITE', 'Изменение'), ('VERIFY', 'Верификация'), ('ADMIN', 'Администрирование'), ('REPORT', 'Построение отчётов'), ('CREATE', 'Создание')])),
            ],
            options={
                'verbose_name': 'назначение удаленного права в Реестре',
                'abstract': False,
                'verbose_name_plural': 'назначения удаленных прав в Реестре',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
