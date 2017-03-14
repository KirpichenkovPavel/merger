# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_remote_model.models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('django_remote_model', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Academic',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='название', max_length=500)),
            ],
            options={
                'verbose_name': 'учёное звание',
                'abstract': False,
                'verbose_name_plural': 'учёные звания',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('date_start', models.DateField(verbose_name='дата начала')),
                ('date_end', models.DateField(verbose_name='дата конца')),
            ],
            options={
                'verbose_name': 'назначение',
                'abstract': False,
                'verbose_name_plural': 'назначения',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='AppointmentType',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('type', models.CharField(verbose_name='тип назначения', max_length=100, null=True)),
                ('status', models.CharField(verbose_name='тип штатной единицы', max_length=100)),
            ],
            options={
                'verbose_name': 'тип назначения',
                'abstract': False,
                'verbose_name_plural': 'типы назначений',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='BusinessProcess',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='имя', max_length=64, unique=True)),
                ('base_url', models.URLField(blank=True, verbose_name='базовый URL')),
            ],
            options={
                'verbose_name': 'бизнес-процесс',
                'abstract': False,
                'verbose_name_plural': 'бизнес-процессы',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='название на русском', max_length=500)),
                ('name_en', models.CharField(verbose_name='название на английском', max_length=500)),
                ('country_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(verbose_name='страна (не из списка стран)', max_length=500)),
            ],
            options={
                'verbose_name': 'город',
                'abstract': False,
                'verbose_name_plural': 'города',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='CoreResultType',
            fields=[
                ('id', models.IntegerField(blank=True)),
                ('version', models.IntegerField(blank=True)),
                ('validity_from', models.DateTimeField(blank=True, null=True)),
                ('validity_to', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(primary_key=True, max_length=256, serialize=False)),
                ('schema', jsonfield.fields.JSONField(default={})),
            ],
            options={
                'verbose_name': 'тип результата',
                'abstract': False,
                'verbose_name_plural': 'типы результата',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='название', max_length=500)),
                ('full_name', models.CharField(verbose_name='полное название', max_length=500)),
                ('code', models.IntegerField(verbose_name='код')),
                ('alpha2', models.CharField(verbose_name='Код ISO', max_length=2)),
                ('alpha3', models.CharField(verbose_name='Код МОК', max_length=3)),
                ('eng_name', models.CharField(verbose_name='название (английское)', max_length=500)),
            ],
            options={
                'verbose_name': 'страна',
                'abstract': False,
                'verbose_name_plural': 'страны',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='название', max_length=500)),
            ],
            options={
                'verbose_name': 'учёная степень',
                'abstract': False,
                'verbose_name_plural': 'учёные степени',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='название', max_length=300)),
                ('full_name', models.CharField(verbose_name='полное название', max_length=300)),
                ('abbrv', models.CharField(verbose_name='аббревиатура', max_length=300)),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('code1', models.CharField(verbose_name='код 1', max_length=2)),
                ('code2', models.CharField(verbose_name='код 2', max_length=2)),
            ],
            options={
                'verbose_name': 'подразделение',
                'abstract': False,
                'verbose_name_plural': 'подразделения',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='DivisionParam',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('key', models.CharField(verbose_name='шаблон подразделения', max_length=300)),
            ],
            options={
                'verbose_name': 'значение шаблона подразделения',
                'abstract': False,
                'verbose_name_plural': 'значения шаблонов подразделений',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='DummyStringModel',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('text', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.CharField(blank=True, primary_key=True, max_length=5, serialize=False)),
                ('last_name', models.CharField(verbose_name='фамилия', max_length=500)),
                ('first_name', models.CharField(verbose_name='имя', max_length=500)),
                ('middle_name', models.CharField(verbose_name='отчество', max_length=500)),
                ('gender', models.CharField(verbose_name='пол', max_length=1)),
                ('date_birth', models.DateField(verbose_name='дата рождения')),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('email', models.CharField(verbose_name='email', max_length=255)),
                ('work_phone', models.CharField(verbose_name='рабочий телефон', max_length=255)),
            ],
            options={
                'verbose_name': 'сотрудник',
                'abstract': False,
                'verbose_name_plural': 'сотрудники',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='EmployeeInfo',
            fields=[
                ('employee', django_remote_model.models.RemoteOneToOneField(related_name='info', primary_key=True, verbose_name='сотрудник', serialize=False, to='main_remote.Employee', db_constraint=False)),
                ('email', models.EmailField(verbose_name='email', max_length=255)),
                ('mobile_phone', models.CharField(verbose_name='мобильный телефон', max_length=255)),
                ('work_phone', models.CharField(verbose_name='рабочий телефон', max_length=255)),
                ('home_phone', models.CharField(verbose_name='домашний телефон', max_length=255)),
                ('work_place', models.CharField(verbose_name='рабочее место', max_length=255)),
            ],
            options={
                'verbose_name': 'информация о сотруднике',
                'abstract': False,
                'verbose_name_plural': 'информация о сотрудниках',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='EmployeeParam',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('key', models.CharField(verbose_name='шаблон сотрудника', max_length=300)),
            ],
            options={
                'verbose_name': 'значение шаблона сотрудника',
                'abstract': False,
                'verbose_name_plural': 'значения шаблонов сотрудников',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='ExternalEmployeeInfo',
            fields=[
                ('employee', django_remote_model.models.RemoteOneToOneField(related_name='external_info', primary_key=True, verbose_name='сотрудник', serialize=False, to='main_remote.Employee', db_constraint=False)),
            ],
            options={
                'verbose_name': 'внешняя информация о сотруднике',
                'abstract': False,
                'verbose_name_plural': 'внешняя информация о сотрудниках',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('date_from', models.DateField(verbose_name='Начало действия', null=True)),
                ('date_to', models.DateField(verbose_name='Конец действия', null=True)),
                ('internalid', models.IntegerField(verbose_name='Внутренний id')),
                ('title_ru', models.CharField(verbose_name='Русское название', max_length=500)),
                ('title_en', models.CharField(verbose_name='Английское название', max_length=500)),
                ('journal_url', models.URLField(verbose_name='URL')),
                ('issn', models.CharField(verbose_name='ISSN', max_length=200)),
                ('e_issn', models.CharField(verbose_name='eISSN', max_length=200)),
                ('publisher', models.CharField(verbose_name='Издательство', max_length=500)),
                ('scopusid', models.CharField(verbose_name='ID в Scopus', max_length=200, null=True)),
                ('impact_factor', models.FloatField(verbose_name='Импакт-фактор')),
                ('snip', models.FloatField(verbose_name='SNIP')),
                ('ipp', models.FloatField(verbose_name='IPP')),
                ('sjr', models.FloatField(verbose_name='SJR')),
                ('scopus_indexed', models.NullBooleanField()),
                ('vak_indexed', models.NullBooleanField()),
                ('wos_indexed', models.NullBooleanField()),
                ('spin_indexed', models.NullBooleanField()),
            ],
            options={
                'verbose_name': 'журнал',
                'abstract': False,
                'verbose_name_plural': 'журналы',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='JournalClassifier',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('code', models.IntegerField(verbose_name='Код')),
                ('name_en', models.CharField(verbose_name='Название на английском', max_length=255)),
            ],
            options={
                'verbose_name': 'классификатор журнала',
                'abstract': False,
                'verbose_name_plural': 'классификаторы журналов',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='название на русском', max_length=500)),
                ('name_en', models.CharField(verbose_name='название на английском', max_length=500)),
                ('scopusid', models.IntegerField(verbose_name='Scopus Id')),
            ],
            options={
                'verbose_name': 'организация',
                'abstract': False,
                'verbose_name_plural': 'организации',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='PermissionTemplate',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('employee_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(verbose_name='шаблон сотрудника', max_length=300)),
                ('permission_type', models.CharField(verbose_name='тип права', max_length=300)),
                ('result_type', models.CharField(verbose_name='тип результата', max_length=300)),
                ('division_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(verbose_name='шаблон подразделения', max_length=300)),
            ],
            options={
                'verbose_name': 'шаблон права',
                'abstract': False,
                'verbose_name_plural': 'шаблоны прав',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='PermissionTypeParam',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('key', models.CharField(verbose_name='шаблон права', max_length=300)),
                ('permission_type', models.CharField(verbose_name='право', max_length=255, choices=[('ALL', '*'), ('READ', 'Чтение'), ('WRITE', 'Изменение'), ('VERIFY', 'Верификация'), ('ADMIN', 'Администрирование'), ('REPORT', 'Построение отчётов'), ('CREATE', 'Создание')])),
            ],
            options={
                'verbose_name': 'значение шаблона права',
                'abstract': False,
                'verbose_name_plural': 'значения шаблонов прав',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='название', max_length=500)),
            ],
            options={
                'verbose_name': 'должность',
                'abstract': False,
                'verbose_name_plural': 'должности',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Postgraduate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('last_name', models.CharField(verbose_name='Фамилия', max_length=500)),
                ('first_name', models.CharField(verbose_name='Имя', max_length=500)),
                ('middle_name', models.CharField(verbose_name='Отчество', max_length=500)),
                ('gender', models.CharField(verbose_name='Пол', max_length=1)),
                ('date_birth', models.DateField(verbose_name='Дата рождения')),
                ('status', models.CharField(verbose_name='Форма обучения', max_length=42, choices=[('INTRAMURAL', 'Очная'), ('EXTRAMURAL', 'Заочная'), ('APPLICANT', 'Соискатель')])),
                ('enrollment', models.DateField(verbose_name='Дата зачисления')),
                ('exclusion', models.DateField(verbose_name='Дата отчисления')),
                ('protection', models.DateField(verbose_name='Дата защиты')),
                ('external_director', models.CharField(verbose_name='Сторонний руководитель', max_length=255)),
                ('funded_by', models.CharField(verbose_name='Финансирование', max_length=42, choices=[('BUDGET', 'Бюджет'), ('CONTRACT', 'Контракт')])),
            ],
            options={
                'verbose_name': 'аспирант',
                'abstract': False,
                'verbose_name_plural': 'аспиранты',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='наименование', max_length=500)),
                ('code', models.CharField(verbose_name='код', max_length=20)),
                ('class_сode', models.CharField(verbose_name='код классификатора', max_length=20, choices=[('FGOS', 'ФГОС'), ('OKSO', 'ОКСО'), ('ORDER1061', 'Приказ 1061')])),
                ('type', models.CharField(verbose_name='направление', max_length=20, choices=[('BACHELOR', 'бакалавриат'), ('MASTER', 'магистратура'), ('SPECIALIST', 'специалитет')])),
            ],
            options={
                'verbose_name': 'специальность',
                'abstract': False,
                'verbose_name_plural': 'специальности',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='RemoteConference',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('russian_name', models.CharField(verbose_name='название на русском', max_length=300)),
                ('english_name', models.CharField(verbose_name='название на английском', max_length=300)),
                ('acronyms', models.CharField(verbose_name='аббревиатуры конференции', max_length=300)),
                ('website', models.URLField(blank=True, verbose_name='веб-сайт', null=True)),
                ('start_date', models.DateField(verbose_name='дата начала')),
                ('end_date', models.DateField(verbose_name='дата окончания')),
                ('country_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(blank=True, verbose_name='страна', max_length=100, null=True)),
                ('city_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(blank=True, verbose_name='город', max_length=100, null=True)),
                ('organization_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(blank=True, verbose_name='учреждение', max_length=300, null=True)),
            ],
            options={
                'verbose_name': 'конференция',
                'abstract': False,
                'verbose_name_plural': 'конференции',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='RemoteTextConferenceOrganizers',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', django_remote_model.models.NoneEmptyRemoteSerializeCharField(verbose_name='название', max_length=256)),
            ],
            options={
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='ResultOwnerModel',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('contribution', models.FloatField()),
            ],
            options={
                'abstract': False,
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='ResultTypeParam',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('key', models.CharField(verbose_name='шаблон типа результата', max_length=300)),
            ],
            options={
                'verbose_name': 'значение шаблона типа результата',
                'abstract': False,
                'verbose_name_plural': 'значения шаблонов типов результата',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'роль',
                'abstract': False,
                'verbose_name_plural': 'роли',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='RoleTemplate',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='имя', max_length=300)),
            ],
            options={
                'verbose_name': 'шаблон роли',
                'abstract': False,
                'verbose_name_plural': 'шаблоны роли',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.IntegerField(blank=True, primary_key=True, serialize=False)),
                ('name', models.CharField(verbose_name='название', max_length=500)),
            ],
            options={
                'verbose_name': 'тематика конференции',
                'abstract': False,
                'verbose_name_plural': 'тематики конференции',
                'managed': False,
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
        migrations.CreateModel(
            name='FundingSource',
            fields=[
                ('remotecoreresultmodel_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, to='django_remote_model.RemoteCoreResultModel', parent_link=True)),
                ('name', models.CharField(verbose_name='название', max_length=200)),
                ('short_name', models.CharField(default='', blank=True, verbose_name='краткое название', max_length=100)),
                ('volume', models.CharField(default='', blank=True, verbose_name='объем', max_length=20)),
                ('start_date', models.DateField(verbose_name='дата начала')),
                ('end_date', models.DateField(verbose_name='дата окончания')),
                ('organization_text', django_remote_model.models.NoneEmptyRemoteSerializeCharField(blank=True, verbose_name='организация', max_length=300, null=True)),
                ('organization', django_remote_model.models.RemoteForeignKey(blank=True, verbose_name='организация', null=True, db_constraint=False, to='main_remote.Organization', related_name='+')),
            ],
            options={
                'verbose_name': 'источник финансирования',
                'verbose_name_plural': 'источники финансирования',
            },
            bases=('django_remote_model.remotecoreresultmodel', models.Model),
        ),
        migrations.CreateModel(
            name='ResultFundingModel',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('fraction', models.FloatField()),
                ('funding', django_remote_model.models.RemoteForeignKey(db_constraint=False, to='main_remote.FundingSource')),
                ('result', models.ForeignKey(related_name='fundings', to='django_remote_model.RemoteCoreResultModel')),
            ],
            options={
            },
            bases=(models.Model, django_remote_model.models.SerializableModel),
        ),
    ]
