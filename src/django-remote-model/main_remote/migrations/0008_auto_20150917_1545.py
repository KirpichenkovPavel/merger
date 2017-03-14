# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models


class Migration(migrations.Migration):

    dependencies = [
        ('main_remote', '0007_divisionhistory_scienceinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessProcessParam',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, blank=True)),
                ('key', models.CharField(max_length=300, verbose_name='шаблон бизнес процесса')),
            ],
            options={
                'verbose_name_plural': 'значения шаблонов бизнес процессов',
                'verbose_name': 'значение шаблона бизнес процесса',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='EntityParam',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, blank=True)),
                ('key', models.CharField(max_length=300, verbose_name='шаблон каталога НСИ')),
                ('entity', models.CharField(max_length=255, choices=[('BUSINESSPROCESS', 'Бизнес-процессы'), ('EMPLOYEEINFO', 'Информация о сотруднике'), ('SCIENCEINFO', 'Научная информация'), ('CITY', 'Города'), ('POST', 'Должности'), ('GRANT', 'Конкурсы и гранты'), ('GRANTCONTAINER', 'Контейнеры конкурсов и грантов'), ('CONFERENCE', 'Конференции'), ('APPOINTMENT', 'Назначения'), ('EDUCATIONPROGRAM', 'Образовательные программы'), ('ORGANIZATION', 'Организации'), ('DIVISION', 'Подразделения'), ('NSIPERMISSION', 'Права доступа к НСИ'), ('PERMISSION', 'Права доступа к РРД'), ('ROLE', 'Роли'), ('EMPLOYEE', 'Сотрудники'), ('COUNTRY', 'Страны'), ('TOPIC', 'Тематики конференций'), ('ACADEMIC', 'Учёные звания'), ('DEGREE', 'Учёные степени'), ('ROLETEMPLATE', 'Шаблоны ролей'), ('GRADUATE', 'Аспиранты'), ('GRADUATECATEGORY', 'Категории аспирантов'), ('GRADUATEFIREREASON', 'Причины отчисления авпирантов'), ('GRADUATESUPERVISOR', 'Научные руководители аспирантов'), ('GRADUATE', 'Категории аспирантов'), ('LOCATION', 'Помещения'), ('TAG', 'Теги'), ('JOURNAL', 'Журналы'), ('JOURNALCLASSIFIER', 'Классификаторы журналов'), ('APPOINTMENTTYPE', 'Типы назначений'), ('ACADEMICRANK', 'Академические звания'), ('STAFFUNIT', 'Штатное расписание'), ('DISSCOUNCIL', 'Диссертационные советы')], verbose_name='каталог НСИ')),
            ],
            options={
                'verbose_name_plural': 'значения шаблонов каталогов НСИ',
                'verbose_name': 'значение шаблона каталога НСИ',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='NsiPermissionTemplate',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, blank=True)),
                ('employee_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(max_length=300, verbose_name='шаблон сотрудника')),
                ('permission_type', models.CharField(max_length=300, verbose_name='тип права НСИ')),
                ('business_process_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(max_length=300, verbose_name='шаблон бизнес процесса')),
                ('entity', models.CharField(max_length=300, verbose_name='каталог НСИ')),
            ],
            options={
                'verbose_name_plural': 'шаблоны прав НСИ',
                'verbose_name': 'шаблон права НСИ',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='NsiPermissionTypeParam',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, blank=True)),
                ('key', models.CharField(max_length=300, verbose_name='шаблон права НСИ')),
                ('permission_type', models.CharField(max_length=255, choices=[('RD', 'чтение'), ('WR', 'запись')], verbose_name='право НСИ')),
            ],
            options={
                'verbose_name_plural': 'значения шаблонов прав НСИ',
                'verbose_name': 'значение шаблона права НСИ',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='StaffUnitHistory',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, blank=True)),
                ('part', models.FloatField(verbose_name='ставка')),
                ('date_start', models.DateField(verbose_name='дата начала')),
                ('date_end', models.DateField(null=True, verbose_name='дата конца')),
            ],
            options={
                'verbose_name_plural': 'истории штатной единицы',
                'verbose_name': 'история штатной единицы',
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.AlterModelOptions(
            name='permissiontemplate',
            options={'verbose_name_plural': 'шаблоны прав РРД', 'managed': False, 'verbose_name': 'шаблон права РРД'},
        ),
        migrations.AlterModelOptions(
            name='permissiontypeparam',
            options={'verbose_name_plural': 'значения шаблонов прав РРД', 'managed': False, 'verbose_name': 'значение шаблона права РРД'},
        ),
    ]
