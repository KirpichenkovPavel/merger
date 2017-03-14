"""
This module contains common remote models from NSI and Registry
"""
from datetime import date
from inspect import isclass
from django.db.models.fields import FieldDoesNotExist, IntegerField
from django.db.models.loading import get_model
from django.db.models.query_utils import Q
from django.utils.datetime_safe import datetime
from _collections_abc import Iterable
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator
from django.db import models

from core_client.queries import core
from django_remote_model.managers import RemoteCoreResultTypeManager
from django_remote_model.models import RemoteNSIModel, RemoteForeignKey, RemoteManyToManyField, RemoteNSIModelBasic, \
    RemoteModel, RemoteCoreResultModel, SerializableModel, NoneEmptyRemoteSerializeCharField, RemoteOneToOneField, \
    RemoteCoreDeleteMixin
from django_remote_model.util.util import today_timestamp_milliseconds
from main_remote.mixins import NamedPersonMixin, AccessByDivisionMixin
from remote_impl.remote_database_exception import RemoteDatabaseError

from django_remote_model.serializers import DateTimeSerializer, IdOrNoneSerializer, ListSerializer
from django_remote_model.util import util
import jsonfield

NSI_C_ACADEMIC = "ACADEMIC"
NSI_C_APPOINTMENT = "APPOINTMENT"
NSI_C_BUSINESSPROCESS = "BUSINESSPROCESS"
NSI_C_CITY = "CITY"
NSI_C_CONFERENCE = "CONFERENCE"
NSI_C_COUNTRY = "COUNTRY"
NSI_C_DEGREE = "DEGREE"
NSI_C_DIVISION = "DIVISION"
NSI_C_EMPLOYEE = "EMPLOYEE"
NSI_C_NSIPERMISSION = "NSIPERMISSION"
NSI_C_ORGANIZATION = "ORGANIZATION"
NSI_C_PERMISSION = "PERMISSION"
NSI_C_POST = "POST"
NSI_C_TOPIC = "TOPIC"
NSI_C_GRANT = "GRANT"
NSI_C_GRANTCONTAINER = "GRANTCONTAINER"
NSI_C_ROLETEMPLATE = "ROLETEMPLATE"
NSI_C_ROLE = "ROLE"
NSI_C_EMPLOYEE_INFO = "EMPLOYEEINFO"
NSI_C_SCIENCE_INFO = "SCIENCEINFO"
NSI_C_POSTGRADUATE = "GRADUATE"
NSI_C_POSTGRADUATE_CATEGORY = "GRADUATECATEGORY"
NSI_C_POSTGRADUATE_FIREREASON = "GRADUATEFIREREASON"
NSI_C_POSTGRADUATE_SUPERVISOR = "GRADUATESUPERVISOR"
NSI_C_GRADUATE_PROGRAM = "GRADUATEPROGRAM"
NSI_C_PARCEL = "PARCEL"
NSI_C_BUILDING = "BUILDING"
NSI_C_LOCATIONKINDGROUP = "LOCATIONKINDGROUP"
NSI_C_LOCATIONKIND = "LOCATIONKIND"
NSI_C_LOCATIONNORMKIND = "LOCATIONNORMKIND"
NSI_C_LOCATION = "LOCATION"
NSI_C_TAG = "TAG"
NSI_C_JOURNAL = "JOURNAL"
NSI_C_JOURNAL_CLASSIFIER = "JOURNALCLASSIFIER"
NSI_C_ACADEMICRANK = "ACADEMICRANK"
NSI_C_APPOINTMENTTYPE = "APPOINTMENTTYPE"
NSI_C_STAFF_UNIT = "STAFFUNIT"
NSI_C_STAFF_UNIT_HISTORY = "STAFFUNITHISTORY"
NSI_C_DISSCOUNCIL = "DISSCOUNCIL"
NSI_C_STUDENT = "STUDENT"
NSI_C_STUDENT_DATA = "STUDENTDATA"
NSI_C_STUDENT_GROUP = "STUDENTGROUP"
NSI_C_STUDENT_STATE = "STUDENTSTATE"
NSI_C_STUDENT_EXAM_TYPE = "STUDENTEXAMTYPE"
NSI_C_STUDENT_EXAM = "STUDENTEXAM"
NSI_C_STUDENT_PRIVILEGE = "STUDENTPRIVILEGE"
NSI_C_STUDENT_GENERATION = "STUDENTGENERATION"
NSI_C_STUDENT_EDUCATION_FORM = "STUDENTDUCATIONFORM"
NSI_C_STUDENT_PROGRAM = "STUDENTPROGRAM"
NSI_C_ACCOUNT = "ACCOUNT"
NSI_C_MATERIAL_POINT = "MATERIALPOINT"
NSI_C_MOOCPLATFORM = "MOOCPLATFORM"

NSI_CATALOGUES = (
    (NSI_C_BUSINESSPROCESS, "Бизнес-процессы"),
    (NSI_C_EMPLOYEE_INFO, "Информация о сотруднике"),
    (NSI_C_SCIENCE_INFO, "Научная информация"),
    (NSI_C_CITY, "Города"),
    (NSI_C_POST, "Должности"),
    (NSI_C_GRANT, "Конкурсы и гранты"),
    (NSI_C_GRANTCONTAINER, "Контейнеры конкурсов и грантов"),
    (NSI_C_CONFERENCE, "Конференции"),
    (NSI_C_APPOINTMENT, "Назначения"),
    (NSI_C_ORGANIZATION, "Организации"),
    (NSI_C_DIVISION, "Подразделения"),
    (NSI_C_NSIPERMISSION, "Права доступа к НСИ"),
    (NSI_C_PERMISSION, "Права доступа к РРД"),
    (NSI_C_ROLE, "Роли"),
    (NSI_C_EMPLOYEE, "Сотрудники"),
    (NSI_C_COUNTRY, "Страны"),
    (NSI_C_TOPIC, "Тематики конференций"),
    (NSI_C_ACADEMIC, "Учёные звания"),
    (NSI_C_DEGREE, "Учёные степени"),
    (NSI_C_ROLETEMPLATE, "Шаблоны ролей"),
    (NSI_C_POSTGRADUATE, "Аспиранты"),
    (NSI_C_GRADUATE_PROGRAM, "Программы аспирантов"),
    (NSI_C_POSTGRADUATE_CATEGORY, "Категории аспирантов"),
    (NSI_C_POSTGRADUATE_FIREREASON, "Причины отчисления аспирантов"),
    (NSI_C_POSTGRADUATE_SUPERVISOR, "Научные руководители аспирантов"),
    (NSI_C_TAG, "Теги"),
    (NSI_C_JOURNAL, "Журналы"),
    (NSI_C_JOURNAL_CLASSIFIER, "Классификаторы журналов"),
    (NSI_C_APPOINTMENTTYPE, "Типы назначений"),
    (NSI_C_ACADEMICRANK, "Академические звания"),
    (NSI_C_STAFF_UNIT, "Штатное расписание"),
    (NSI_C_STAFF_UNIT_HISTORY, "История штатного расписания"),
    (NSI_C_DISSCOUNCIL, "Диссертационные советы"),
    (NSI_C_PARCEL, "Земельные участки"),
    (NSI_C_BUILDING, "Здания"),
    (NSI_C_LOCATIONKINDGROUP, "Группы категорий помещения"),
    (NSI_C_LOCATIONKIND, "Категории помещения"),
    (NSI_C_LOCATIONNORMKIND, "Норм. кат. помещения"),
    (NSI_C_LOCATION, "Помещения"),
    (NSI_C_STUDENT, "Студенты"),
    (NSI_C_STUDENT_DATA, "Данные о студентах"),
    (NSI_C_STUDENT_GROUP, "Студенческие группы"),
    (NSI_C_STUDENT_STATE, "Статусы студента"),
    (NSI_C_STUDENT_EXAM_TYPE, "Типы экзаменов студентов"),
    (NSI_C_STUDENT_EXAM, "Экзамены студентов"),
    (NSI_C_STUDENT_PRIVILEGE, "Типы льготных студентов"),
    (NSI_C_STUDENT_GENERATION, "Поколения стандартов"),
    (NSI_C_STUDENT_EDUCATION_FORM, "Формы обучения судентов"),
    (NSI_C_STUDENT_PROGRAM, "Программы студентов"),
    (NSI_C_ACCOUNT, "Лицевые счета"),
    (NSI_C_MATERIAL_POINT, "Материальные точки"),
    (NSI_C_MOOCPLATFORM, "МООК платформа"),

)


class RemoteNSIAbstractNamedModel(RemoteNSIModel):
    class Meta:
        abstract = True

    name = models.CharField("название", max_length=255)

    serialize_model = {
        "id": "id",
        "name": "name",
    }

    def __str__(self):
        return str(self.name)


class CoreResultType(RemoteModel):

    class Meta(RemoteModel.Meta):
        verbose_name = "тип результата"
        verbose_name_plural = "типы результата"
        app_label = "main_remote"
    _client = core
    id = models.IntegerField(blank=True)
    version = models.IntegerField(blank=True)
    validity_from = models.DateTimeField(blank=True, null=True)
    validity_to = models.DateTimeField(blank=True, null=True)
    name = models.CharField(primary_key=True, max_length=256)
    schema = jsonfield.JSONField(default={})

    objects = RemoteCoreResultTypeManager()

    LOCAL_ID_NAME = "name"

    custom_fieldtype_serializers = dict(RemoteModel.custom_fieldtype_serializers)
    custom_fieldtype_serializers.update({
        models.DateTimeField: DateTimeSerializer
    })

    serialize_model = {
        "id": "id",
        "version": "version",
        "validity": {
            "from": "validity_from",
            "to": "validity_to"
        },
        "name": "name",
        "schema": "schema"
    }

    _reversed_serialize_model = None
    reverse_serialize_ignored_fields = {}
    custom_reverse_serialize = {}

    @classmethod
    def _reverse_field(cls, result, l, r, prefix):
        is_foreign_key = False
        if l.endswith("_id"):
            new_name = l[:-3]
            try:
                field_type = cls._meta.get_field(new_name)
            except FieldDoesNotExist:
                pass
            else:
                if isinstance(field_type, models.ForeignKey):
                    l = new_name
                    is_foreign_key = True
        else:
            try:
                field_type = cls._meta.get_field(l)
            except FieldDoesNotExist:
                pass
            else:
                if isinstance(field_type, models.ForeignKey):
                    is_foreign_key = True
        if is_foreign_key and issubclass(field_type.rel.to, RemoteNSIModelBasic):
            result[l] = prefix + (field_type.rel.to,)
        else:
            result[l] = prefix + (r,)

    @classmethod
    def _reverse_serialize_model(cls, model, ignored, prefix=()):
        result = {}
        for r, l in model.items():
            ign = ignored.get(r, {})
            if r in ignored:
                if ign is None:
                    continue
            if isinstance(l, str):
                cls._reverse_field(result, l, r, prefix)
            elif isinstance(l, dict):
                result.update(cls._reverse_serialize_model(l, ign, prefix + (r,)))
        return result

    @classmethod
    def _calculate_reversed_serialize_model(cls):
        cls._reversed_serialize_model = cls._reverse_serialize_model(cls.get_serializable_model_for_query(),
                                                                     cls.reverse_serialize_ignored_fields)
        cls._reversed_serialize_model.update(cls.custom_reverse_serialize)

    @classmethod
    def get_reversed_serialize_field(cls, field):
        if not field:
            return None
        rf = cls._reversed_serialize_model.get(field[0])
        if rf is None:
            return None

        sub_model = None

        if len(rf) > 0 and isclass(rf[-1]) and issubclass(rf[-1], models.Model):
            sub_model = rf[-1]
            rf = rf[:-1]

        if len(field) > 1:
            if sub_model is None:
                try:
                    field_type = cls._meta.get_field(field[0])
                except FieldDoesNotExist:
                    return None
                else:
                    if isinstance(field_type, models.ForeignKey):
                        sub_model = field_type.rel.to
                    else:
                        return None
            sub_rf = sub_model.get_reversed_serialize_field(field[1:])
            if sub_rf is None:
                return None
            else:
                return rf + sub_rf
        else:
            return rf

    @property
    def allow_save(self):
        return self.name != "*"

    @property
    def allow_delete(self):
        return self.name != "*"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.allow_save:
            try:
                save_res = self._client.post_result_type(self)
            except RemoteDatabaseError as rdbe:
                raise RemoteDatabaseError("Unable to post CoreResultType object",
                                          remote_error_json=rdbe.remote_error_json)
            else:
                self.id = save_res.id
                self.version = save_res.version
                self.validity_from = save_res.validity_from
                self.validity_to = save_res.validity_to

    def delete(self, using=None):
        if self.allow_delete:
            try:
                self._client.delete_result_type(self)
            except RemoteDatabaseError as rdbe:
                raise RemoteDatabaseError("Unable to delete CoreResultType object",
                                          remote_error_json=rdbe.remote_error_json)

    def __str__(self):
        return "{}".format(self.name)


class BusinessProcess(RemoteNSIModel):
    """Model for business processes"""
    name = models.CharField("имя", max_length=64, unique=True)
    base_url = models.URLField("базовый URL", blank=True)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "бизнес-процесс"
        verbose_name_plural = "бизнес-процессы"
        app_label = "main_remote"

    url = "/businessprocess"

    serialize_model = {
        "id": "id",
        "name": "name",
        "url": "base_url"
    }

    def __str__(self):
        return "{}".format(self.name)


class Tag(RemoteNSIModel):
    tag = models.CharField("Тег", max_length=255, primary_key=True)
    description = models.CharField("Описание", max_length=255)

    url = '/tag'

    allow_save = True
    allow_delete = True

    serialize_model = {
        'id': 'tag',
        'description': 'description',
    }

    def __str__(self):
        return self.description


class Division(RemoteNSIModel):
    """Model that describes divisions. Because the name can be changed, the entity is temporal"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "подразделение"
        verbose_name_plural = "подразделения"
        app_label = "main_remote"
    
    TOP_LEVEL_ID = 0
    
    parent = RemoteForeignKey("self", verbose_name="родительское подразделение",
                               related_name="children", null=True, blank=True)
    name = models.CharField("название", max_length=300)
    full_name = models.CharField("полное название", max_length=300)  # what the fuck is this?
    abbrv = models.CharField("аббревиатура", max_length=300)

    valid_from = models.DateField()
    valid_to = models.DateField(null=True)
    code1 = models.CharField("код 1", max_length=2, null=True)
    code2 = models.CharField("код 2", max_length=2, null=True)
    tags = RemoteManyToManyField(Tag, remote_m2m_list=True, verbose_name="теги", related_name="+")

    allow_save = True
    allow_delete = True
    url = "/division"

    serialize_model = {
        "id": "id",
        "validFrom": "valid_from",
        "validTo": "valid_to",
        "parent": "parent",
        "name": "name",
        "fullName": "full_name",
        "abbreviation": "abbrv",
        "code1": "code1",
        "code2": "code2",
        "tags": ("tags", ListSerializer(Tag))
    }

    query_names = {
        "parent": ("parent", "exact"),
        "name": ("name", "str"),
        "abbrv": ("abbr", "str"),
        "valid": ("valid", "exact"),
        "code1": ("code1", "exact"),
        "code2": ("code2", "exact")
    }

    predefined_queries = {
        "valid": lambda valid:
            Q(valid_to__isnull=True) | Q(valid_to__gte=date.today()) | Q(id=0) if valid
            else Q(valid_to__lt=date.today()) & Q(id__exactnot=0)
    }

    def __str__(self):
        return str(self.name)

    @property
    def head(self):
        return self._client.get_department_head(self)

    custom_reverse_serialize = {
        "parent": ("parent",)
    }


class DivisionHistory(RemoteNSIModel):
    """Model that describes divisions. Because the name can be changed, the entity is temporal"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "история подразделения"
        verbose_name_plural = "история подразделений"
        app_label = "main_remote"
    activity_from = models.DateTimeField(blank=True, null=True)
    activity_to = models.DateTimeField(blank=True, null=True)

    division = RemoteForeignKey(Division, verbose_name="подразделение", related_name="+")
    parent = RemoteForeignKey("self", verbose_name="родительское подразделение",
                               related_name="children", null=True, blank=True)
    name = models.CharField("название", max_length=300)
    full_name = models.CharField("полное название", max_length=300)
    abbrv = models.CharField("аббревиатура", max_length=300)

    valid_from = models.DateField()
    valid_to = models.DateField(null=True)
    code1 = models.CharField("код 1", max_length=2, null=True)
    code2 = models.CharField("код 2", max_length=2, null=True)

    allow_save = True
    allow_delete = True
    url = "/division/history"

    serialize_model = {
        "activity": {
            "from": "activity_from",
            "to": "activity_to"
        },
        "division": {
            "id": "division"
        },
        "id": "id",
        "validFrom": "valid_from",
        "validTo": "valid_to",
        "parent": "parent",
        "name": "name",
        "fullName": "full_name",
        "abbreviation": "abbrv",
        "code1": "code1",
        "code2": "code2"
    }

    custom_reverse_serialize = {
        "parent": ("parent",)
    }

    query_names = {
        "division": ("division", "exact"),
        "parent": ("parent", "exact"),
        "name": ("name", "str"),
        "abbrv": ("abbr", "str"),
        "valid": ("valid", "exact"),
        "code1": ("code1", "exact"),
        "code2": ("code2", "exact")
    }

    predefined_queries = {
        "valid": lambda valid:
            Q(valid_to__isnull=True) | Q(valid_to__gte=date.today()) | Q(id=0) if valid
            else Q(valid_to__lt=date.today()) & Q(id__exactnot=0)
    }

    def __str__(self):
        return str(self.name)

    @property
    def head(self):
        return self._client.get_department_head(self)

    def diff(self, arg):
        exclude_fields = ["id", "activity_from", "activity_to"]
        res = {}
        for field in self._meta.fields:
            if field.name in exclude_fields:
                continue
            self_value = field.value_from_object(self)
            arg_value = field.value_from_object(arg)
            if self_value != arg_value:
                res[field.name] = (arg_value, self_value)
        return res


class Country(RemoteNSIModel):
    """Model for countries"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "страна"
        verbose_name_plural = "страны"
        app_label = "main_remote"

    name = models.CharField("название", max_length=500)
    full_name = models.CharField("полное название", max_length=500)
    code = models.IntegerField("код")
    alpha2 = models.CharField("Код ISO", max_length=2)
    alpha3 = models.CharField("Код МОК", max_length=3)
    eng_name = models.CharField("название (английское)", max_length=500)

    url = "/country"

    serialize_model = {
        "id": "id",
        "name": "name",
        "fullName": "full_name",
        "code": "code",
        "alpha2": "alpha2",
        "alpha3": "alpha3",
        "engName": "eng_name"
    }

    query_names = {
        "name": ("name", "str"),
        "full_name": ("full_name", "str"),
        "eng_name": ("eng_name", "str")
    }

    allow_save = True

    def __str__(self):
        return str(self.full_name if self.full_name else self.name)


class City(RemoteNSIModel):
    """Model for cities"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "город"
        verbose_name_plural = "города"
        app_label = "main_remote"

    name = models.CharField("название на русском", max_length=500)
    name_en = models.CharField("название на английском", max_length=500)
    country = RemoteForeignKey(Country, verbose_name="страна", null=True, blank=True)
    country_text = NoneEmptyRemoteSerializeCharField("страна (не из списка стран)", max_length=500)

    url = "/city"

    serialize_model = {
        "id": "id",
        "name": "name",
        "nameEn": "name_en",
        "country": {
            "reference": {
                "id": "country"
            },
            "text": "country_text"
        }
    }

    query_names = {
        "name": ("name", "str"),
        "country": ("countryRef", "exact"),
        "country_text": ("countryText", "str"),
        "name_en": ("nameEn", "str")
    }

    custom_reverse_serialize = {
        "country": ("country", "reference", Country)
    }

    allow_save = True

    def __str__(self):
        return str(self.name)


class Organization(RemoteNSIModel):
    """Model for external organizations"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "организация"
        verbose_name_plural = "организации"
        app_label = "main_remote"

    name = models.CharField("название на русском", max_length=500)
    name_en = models.CharField("название на английском", max_length=500)
    scopusid = models.IntegerField("Scopus Id")
    spinid = models.IntegerField("РИНЦ Id", null=True, default=None)
    city = RemoteForeignKey("main_remote.City", null=True)
    country = RemoteForeignKey("main_remote.Country", null=True)

    url = "/organization"

    serialize_model = {
        "id": "id",
        "name": "name",
        "nameEn": "name_en",
        "scopusId": "scopusid",
        "spinId": "spinid",
        "city": ("city_id", IdOrNoneSerializer(City)),
        "country": ("country_id", IdOrNoneSerializer(Country))
    }

    query_names = {
        "name": ("name", "str"),
        "name_en": ("nameEn", "str"),
        "scopusid": ("scopusId", "exact")
    }

    allow_save = True

    def __str__(self):
        return str(self.name)


class Post(RemoteNSIModel):
    """Model for posts"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "должность"
        verbose_name_plural = "должности"
        app_label = "main_remote"

    name = models.CharField("название", max_length=500, null=True)
    short_name = models.CharField("сокращённое название", max_length=500, null=True)
    tags = RemoteManyToManyField(Tag, remote_m2m_list=True, verbose_name="теги", related_name="+")

    allow_save = True
    allow_delete = True
    url = "/post"

    serialize_model = {
        "id": "id",
        "name": "name",
        "shortName": "short_name",
        "tags": ("tags", ListSerializer(Tag))
    }

    query_names = {
        "name": ("name", "str")
    }

    def __str__(self):
        return str(self.name)


class Degree(RemoteNSIModel):
    """Model for degrees"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "учёная степень"
        verbose_name_plural = "учёные степени"
        app_label = "main_remote"

    name = models.CharField("название", max_length=500, null=True)
    short_name = models.CharField("сокращённое название", max_length=500, null=True)
    full_name = models.CharField("полное название", max_length=500, null=True)

    allow_save = True
    allow_delete = True
    url = "/degree"

    serialize_model = {
        "id": "id",
        "name": "name",
        "shortName": "short_name",
        "fullName": "full_name"
    }

    query_names = {
        "name": ("name", "str")
    }

    def __str__(self):
        return str(self.name)


class Academic(RemoteNSIModel):
    """Model for academics"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "учёное звание"
        verbose_name_plural = "учёные звания"
        app_label = "main_remote"

    name = models.CharField("название", max_length=500)
    short_name = models.CharField("сокращённое название", max_length=500, null=True)
    full_name = models.CharField("полное название", max_length=500, null=True)

    allow_save = True
    allow_delete = True
    url = "/academic"

    serialize_model = {
        "id": "id",
        "name": "name",
        "shortName": "short_name",
        "fullName": "full_name"
    }

    query_names = {
        "name": ("name", "str")
    }

    def __str__(self):
        return str(self.name)


class AcademicRank(RemoteNSIModel):
    """Model for academic ranks"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "академическое звание"
        verbose_name_plural = "академические звания"
        app_label = "main_remote"

    name = models.CharField("название", max_length=500)
    short_name = models.CharField("сокращённое название", max_length=500, null=True)
    full_name = models.CharField("полное название", max_length=500, null=True)

    allow_save = True
    allow_delete = True
    url = "/academicrank"

    serialize_model = {
        "id": "id",
        "name": "name",
        "shortName": "short_name",
        "fullName": "full_name"
    }

    query_names = {
        "name": ("name", "str")
    }

    def __str__(self):
        return str(self.name)


class EmployeeInfo(RemoteNSIModelBasic):
    """Model for employee info"""
    class Meta(RemoteNSIModelBasic.Meta):
        verbose_name = "информация о сотруднике"
        verbose_name_plural = "информация о сотрудниках"
        app_label = "main_remote"

    employee = RemoteOneToOneField('main_remote.Employee', verbose_name="сотрудник", primary_key=True, related_name='info')
    email = models.EmailField(verbose_name="email", max_length=255)
    mobile_phone = models.CharField(verbose_name="мобильный телефон", max_length=255)
    work_phone = models.CharField(verbose_name="рабочий телефон", max_length=255)
    home_phone = models.CharField(verbose_name="домашний телефон", max_length=255)
    work_place = models.CharField(verbose_name="рабочее место", max_length=255)

    url = "/employee/info"
    allow_save = True
    LOCAL_ID_NAME = "employee"

    serialize_model = {
        "employee": {
            "id": "employee"
        },
        "email": "email",
        "mobilePhone": "mobile_phone",
        "workPhone": "work_phone",
        "homePhone": "home_phone",
        "workPlace": "work_place"
    }

    query_names = {
        "employee": ("employeeId", "exact"),
    }

    def __str__(self):
        return str(self.employee)


class ScienceInfoElement(RemoteNSIModelBasic):
    class Meta(RemoteNSIModelBasic.Meta):
        app_label = "main_remote"

    identifier = models.CharField(max_length=255, primary_key=True)
    h_index = models.CharField(max_length=255)
    pub_count = models.IntegerField(null=True, default=None)
    LOCAL_ID_NAME = "identifier"

    serialize_model = {
        "identifier": "identifier",
        "hIndex": "h_index",
        "pubCount": "pub_count"
    }

    def __str__(self):
        return self.identifier


class ScienceInfo(RemoteNSIModel):
    """Model for external employee info"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "внешняя информация о сотруднике"
        verbose_name_plural = "внешняя информация о сотрудниках"
        app_label = "main_remote"

    employee = RemoteOneToOneField('main_remote.Employee', verbose_name="сотрудник", related_name='science_info', null=True)
    postgraduate = RemoteOneToOneField('main_remote.Postgraduate', verbose_name="аспирант", related_name='science_info', null=True)
    student = RemoteOneToOneField('main_remote.Student', verbose_name="стуент", related_name="science_info", null=True)
    scopusids = RemoteManyToManyField(ScienceInfoElement, verbose_name="Scopus Author IDs", remote_m2m_list=True, related_name='+')
    orcids = RemoteManyToManyField(ScienceInfoElement, verbose_name="ORCIDs", remote_m2m_list=True, related_name='+')
    researcherids = RemoteManyToManyField(ScienceInfoElement, verbose_name="Researcher IDs", remote_m2m_list=True, related_name='+')
    spin_codes = RemoteManyToManyField(ScienceInfoElement, verbose_name="SPIN-коды", remote_m2m_list=True, related_name='+')
    spin_authorids = RemoteManyToManyField(ScienceInfoElement, verbose_name="РИНЦ Author IDs", remote_m2m_list=True, related_name='+')

    url = "/info/science"
    allow_save = True

    serialize_model = {
        "id": "id",
        "employee": ("employee_id", IdOrNoneSerializer(None)),
        "graduate": ("postgraduate_id", IdOrNoneSerializer(None)),
        "student": ("student_id", IdOrNoneSerializer(None)),
        "scopusIds": ("scopusids", ListSerializer(ScienceInfoElement)),
        "orcIds": ("orcids", ListSerializer(ScienceInfoElement)),
        "researcherIds": ("researcherids", ListSerializer(ScienceInfoElement)),
        "spinCodes": ("spin_codes", ListSerializer(ScienceInfoElement)),
        "spinAuthorIds": ("spin_authorids", ListSerializer(ScienceInfoElement))
    }

    query_names = {
        "scopusid": ("scopusId", "exact"),
        "orcid": ("orcId", "exact"),
        "researcherid": ("researcherId", "exact"),
        "spin_code": ("spinCode", "exact"),
        "spin_authorid": ("spinAuthorId", "exact"),
        "employee": ("employeeId", "exact")
    }

    predefined_queries = {
        "scopusid": lambda scopusid: Q(scopusids__any=[scopusid]),
        "orcid": lambda orcid: Q(orcids__any=[orcid]),
        "researcherid": lambda researcherid: Q(researcherids__any=[researcherid]),
        "spin_code": lambda spin_code: Q(spin_code__any=[spin_code]),
        "spin_authorid": lambda spin_authorid: Q(spin_authorids__any=[spin_authorid]),
    }

    def __str__(self):
        return "Сотрудник: " + str(self.employee) if self.employee \
            else "Аспирант: " + str(self.postgraduate) if self.postgraduate \
            else "Студент: " + str(self.student) if self.student else "Неопознанная сущность"


class Employee(RemoteNSIModelBasic, NamedPersonMixin, AccessByDivisionMixin):
    division_field = "appointments__division"

    """Model for employees"""
    class Meta(RemoteNSIModelBasic.Meta):
        verbose_name = "сотрудник"
        verbose_name_plural = "сотрудники"
        app_label = "main_remote"

    id = models.CharField(max_length=5, primary_key=True, blank=True)
    last_name = models.CharField("фамилия", max_length=500)
    first_name = models.CharField("имя", max_length=500)
    middle_name = models.CharField("отчество", max_length=500, null=True)
    gender = models.CharField("пол", max_length=1)
    date_birth = models.DateField("дата рождения", null=True)
    country = RemoteForeignKey(Country, verbose_name="гражданство", null=True)
    post = RemoteForeignKey(Post, verbose_name="должность", null=True)
    division = RemoteForeignKey(Division, verbose_name="подразделение", null=True)
    degree = RemoteForeignKey(Degree, verbose_name="учёная степень", null=True)
    academic = RemoteForeignKey(Academic, verbose_name="учёное звание", null=True)
    academic_rank = RemoteForeignKey(AcademicRank, verbose_name="академическое звание", null=True)

    appointment_divisions = RemoteManyToManyField(Division, through="Appointment", related_name="appointment_employees",
                                                  remote_m2m_url="/division",
                                                  remote_m2m_reverse_url="/employee",
                                                  verbose_name="подразделения по назначениям")

    appointment_posts = RemoteManyToManyField(Post, through="Appointment", related_name="appointment_employees",
                                              remote_m2m_url="/post",
                                              remote_m2m_reverse_url="/employee",
                                              verbose_name="должности по назначениям")

    valid_from = models.DateField(null=True)
    valid_to = models.DateField(null=True)
    email = models.CharField("email", max_length=255, null=True)
    work_phone = models.CharField("рабочий телефон", max_length=255, null=True)

    allow_save = True
    allow_delete = True
    url = "/employee"

    serialize_model = {
        "id": "id",
        "validFrom": "valid_from",
        "validTo": "valid_to",
        "lastName": "last_name",
        "firstName": "first_name",
        "middleName": "middle_name",
        "gender": "gender",
        "dateBirth": "date_birth",
        "country": ("country_id", IdOrNoneSerializer(Country)),
        "post": ("post_id", IdOrNoneSerializer(Post)),
        "division": ("division_id", IdOrNoneSerializer(Division)),
        "degree": ("degree_id", IdOrNoneSerializer(Degree)),
        "academic": ("academic_id", IdOrNoneSerializer(Academic)),
        "academicRank": ("academic_rank_id", IdOrNoneSerializer(AcademicRank)),
        "email": "email",
        "workPhone": "work_phone"
    }

    query_names = {
        "first_name": ("firstName", "str"),
        "last_name": ("lastName", "str"),
        "middle_name": ("middleName", "str"),
        "degree": ("degree", "exact"),
        "division": ("division", "exact"),
        "post": ("post", "exact"),
        "academic": ("academic", "exact"),
        "valid": ("valid", "exact"),
        "valid_from": ("validFrom", "gtelte"),
        "valid_to": ("validTo", "gtelte"),
        "date_birth": ("dateBirth", "gtelte"),
        "period_start": ("periodStart", "exact"),
        "period_end": ("periodEnd", "exact"),
    }

    predefined_queries = {
        "valid": lambda valid:
            Q(appointments__isnull=False) & (
                Q(appointments__date_end__isnull=True) |
                Q(appointments__date_end__gte=date.today()) if valid
                else Q(appointments__date_end__lt=date.today())
            ),
        "period_start": lambda period_start:
            Q(appointments__date_end__isnull=True) |
            Q(appointments__date_end__gte=period_start) |
            (
                Q(appointments__isnull=True) &
                Q(valid_to__isnull=False) &
                Q(valid_to__gte=period_start)
            ),
        "period_end": lambda period_end:
            Q(appointments__date_start__isnull=True) |
            Q(appointments__date_start__lte=period_end) |
            (
                Q(appointments__isnull=True) &
                Q(valid_from__isnull=False) &
                Q(valid_from__lte=period_end)
            )
    }

    custom_reverse_serialize = {
        "info": ("info", EmployeeInfo),
        "science_info": ("scienceInfo", ScienceInfo)
    }

    @staticmethod
    def stringify_science_info(obj, field_name):
        values_str = ''
        if hasattr(obj, 'science_info'):
            field_value = getattr(obj.science_info, field_name)
            if hasattr(field_value, 'values') and isinstance(field_value.values, Iterable):
                for element in field_value.values:
                    if element is not None:
                        values_str += element.identifier if values_str == '' else ', ' + element.identifier
        return values_str if values_str else '-'

    export_fields = [
        {
            "label": "Табельный номер",
            "field": "id",
        },
        {
            "label": "Фамилия",
            "field": "last_name",
        },
        {
            "label": "Имя",
            "field": "first_name",
        },
        {
            "label": "Отчество",
            "field": "middle_name",
        },
        {
            "label": "Возраст",
            "field": "age",
        },
        {
            "label": "Учёная степень",
            "function": lambda obj: obj.degree.full_name if obj.degree is not None else '-',
        },

        {
            "label": "Учёное звание",
            "function": lambda obj: obj.academic.full_name if obj.academic is not None else '-',
        },

        {
            "label": "Должность",
            "field": "post",
        },
        {
            "label": "Дата поступления",
            "function": lambda obj: obj.valid_from.strftime("%d.%m.%Y") if obj.valid_from else '-',
        },
        {
            "label": "Дата увольнения",
            "function": lambda obj: obj.valid_to.strftime("%d.%m.%Y") if obj.valid_to else '-',
        },
        {
            "label": "ScopusID",
            "function": lambda obj: Employee.stringify_science_info(obj, "scopusids"),
        },
        {
            "label": "ORCID",
            "function": lambda obj: Employee.stringify_science_info(obj, "orcids"),
        },
        {
            "label": "ResearcherID",
            "function": lambda obj: Employee.stringify_science_info(obj, "researcherids"),
        },
        {
            "label": "РИНЦ SPIN-коды",
            "function": lambda obj: Employee.stringify_science_info(obj, "spin_codes"),
        },
        {
            "label": "РИНЦ Author ID",
            "function": lambda obj: Employee.stringify_science_info(obj, "spin_authorids"),
        },
    ]

    @property
    def age(self):
        today = datetime.today().date()
        if self.date_birth and hasattr(self.date_birth, "year") \
                and hasattr(self.date_birth, "month") and hasattr(self.date_birth, "day"):
            correction = int((today.month, today.day) < (self.date_birth.month, self.date_birth.day))
            return (today.year - self.date_birth.year) - correction
        else:
            return None

    def ids_count(self, field_name):
        items = self.ids_get(field_name)
        return len(items)

    def ids_get(self, field_name):
        result = []
        if hasattr(self, 'science_info'):
            field_value = getattr(self.science_info, field_name)
            if hasattr(field_value, 'values') and isinstance(field_value.values, Iterable):
                result = field_value.values
        return result

    def __str__(self):
        return self.red_tape_full_name


class AppointmentType(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "тип назначения"
        verbose_name_plural = "типы назначений"
        app_label = "main_remote"

    type = models.CharField(verbose_name="тип назначения", max_length=100, null=True)
    status = models.CharField(verbose_name="тип штатной единицы", max_length=100)

    allow_save = True
    allow_delete = True
    url = '/appointment/type'

    serialize_model = {
        'id': 'id',
        'type': 'type',
        'status': 'status'
    }

    def __str__(self):
        return "{}, {}".format(self.type, self.status)


class StaffUnit(RemoteNSIModel, AccessByDivisionMixin):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "штатная единица"
        verbose_name_plural = "штатные единицы"
        app_label = "main_remote"

    division = RemoteForeignKey(Division, verbose_name="подразделение", related_name="staff_units")
    post = RemoteForeignKey(Post, verbose_name="должность", related_name="staff_units")
    part = models.FloatField("ставка")
    type = RemoteForeignKey(AppointmentType, verbose_name="тип")
    date_start = models.DateField("дата начала")
    date_end = models.DateField("дата конца", null=True)

    allow_save = True
    allow_delete = True
    url = "/staffunit"

    export_fields = [
        {
            "label": "id",
            "field": "id",
        },
        {
            "label": "Подразделение",
            "field": "division",
        },
        {
            "label": "Должность",
            "field": "post",
        },
        {
            "label": "Количество ставок",
            "field": "part",
        },
        {
            "label": "Дата начала",
            "function": lambda obj: obj.date_start.strftime("%d.%m.%Y") if obj.date_start else '',
        },
        {
            "label": "Дата окончания",
            "function": lambda obj: obj.date_end.strftime("%d.%m.%Y") if obj.date_end else '',
        }
    ]

    serialize_model = {
        "id": "id",
        "division": {
            "id": "division"
        },
        "post": {
            "id": "post"
        },
        "part": "part",
        "type": {
            "id": "type"
        },
        "validFrom": "date_start",
        "validTo": "date_end"
    }

    predefined_queries = {
        "valid": lambda valid:
            Q(date_end__exact=None) | Q(date_end__gte=date.today()) if valid
            else Q(date_end__lte=date.today()),
        "timestamp": lambda timestamp:
            Q(date_start__lte=timestamp) & (Q(date_end__exact=None) | Q(date_end__gte=timestamp))
    }

    @property
    def occupied_part(self):
        return self._client.get_objects_agg(get_model("main_remote.Appointment"),
                               Q(staff_unit__exact=self.pk, valid=True),
                               "sum", "staff_unit_part") or 0.0

    @property
    def free_part(self):
        return self.part - self.occupied_part

    def __str__(self):
        return "{}, {} ({})".format(self.division,
                                    self.post,
                                    self.part)


class StaffUnitHistory(RemoteNSIModel, AccessByDivisionMixin):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "история штатной единицы"
        verbose_name_plural = "истории штатной единицы"
        app_label = "main_remote"

    division_field = "staff_unit__division"

    staff_unit = RemoteForeignKey(StaffUnit, verbose_name="штатная единица", related_name="history_entries")
    part = models.FloatField("ставка")
    date_start = models.DateField("дата начала")
    date_end = models.DateField("дата конца", null=True)

    allow_save = True
    allow_delete = True
    url = "/staffunit/history"

    serialize_model = {
        "id": "id",
        "staffUnit": {
            "id": "staff_unit"
        },
        "part": "part",
        "validFrom": "date_start",
        "validTo": "date_end"
    }

    export_fields = [
        {
            "label": "id",
            "function": lambda obj: obj.staff_unit.id,
        },
        {
            "label": "Подразделение",
            "function": lambda obj: obj.staff_unit.division,
        },
        {
            "label": "Должность",
            "function": lambda obj: obj.staff_unit.post,
        },
        {
            "label": "Тип должности",
            "function": lambda obj: obj.staff_unit.type.type,
        },
        {
            "label": "Количество ставок",
            "field": "part",
        },
        {
            "label": "Дата начала",
            "function": lambda obj: obj.date_start.strftime("%d.%m.%Y") if obj.date_start else '',
        },
        {
            "label": "Дата окончания",
            "function": lambda obj: obj.date_end.strftime("%d.%m.%Y") if obj.date_end else '',
        }
    ]

    predefined_queries = {
        "valid": lambda valid:
            Q(date_end__exact=None) | Q(date_end__gte=date.today()) if valid
            else Q(date_end__lte=date.today()),
        "timestamp": lambda timestamp:
            Q(date_start__lte=timestamp) & (Q(date_end__exact=None) | Q(date_end__gte=timestamp))
    }

    def __str__(self):
        return "{}: {} ({} - {})".format(self.staff_unit_id,
                                         self.part,
                                         self.date_start,
                                         self.date_end)


class Appointment(RemoteNSIModel):
    """Model for appointments"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "назначение"
        verbose_name_plural = "назначения"
        app_label = "main_remote"

    date_start = models.DateField("дата начала")
    date_end = models.DateField("дата конца", null=True)
    employee = RemoteForeignKey(Employee, verbose_name="сотрудник", related_name="appointments")
    post = RemoteForeignKey(Post, verbose_name="должность", related_name="appointments")
    division = RemoteForeignKey(Division, verbose_name="подразделение", related_name="appointments")
    type = RemoteForeignKey(AppointmentType, verbose_name="тип")
    staff_unit = RemoteForeignKey(StaffUnit, verbose_name="штатная единица")
    staff_unit_part = models.FloatField("ставка")

    allow_save = True
    allow_delete = True
    url = "/appointment"

    serialize_model = {
        "id": "id",
        "dateStart": "date_start",
        "dateEnd": "date_end",
        "employee": {
            "id": "employee"
        },
        "post": {
            "id": "post"
        },
        "division": {
            "id": "division"
        },
        "type": {
            "id": "type"
        },
        "staffUnit": {
            "id": "staff_unit"
        },
        "staffUnitPart": "staff_unit_part"
    }

    query_names = {
        "employee": ("employee", "exact"),
        "division": ("division", "exact"),
        "post": ("post", "exact"),
        "valid": ("valid", "exact"),
        "timestamp": ("timestamp", "exact")
    }

    predefined_queries = {
        "valid": lambda valid:
            Q(date_end__exact=None) | Q(date_end__gte=date.today()) if valid
            else Q(date_end__lt=date.today()),
        "timestamp": lambda timestamp:
            Q(date_start__lte=timestamp) & (Q(date_end__exact=None) | Q(date_end__gte=timestamp))
    }

    def __str__(self):
        return "{}, {} ({})".format(str(self.employee),
                                    self.post,
                                    self.division)


class DivisionsSerializer:
    @staticmethod
    def serialize(local_field):
        return [{"id": d.id} for d in local_field.all()]

    @staticmethod
    def deserialize(remote_field):
        return [Division.objects.get(id=d["id"]) for d in remote_field]


class PostgraduateProgram(RemoteNSIModel):
    """Model for program"""

    PT_POSTGRADUATE_AREA = "GRADUATE_AREA"
    PT_POSTGRADUATE_SPECIALITY = "GRADUATE_SPECIALITY"

    PROGRAM_TYPE = (
        (PT_POSTGRADUATE_AREA, "направление аспирантуры"),
        (PT_POSTGRADUATE_SPECIALITY, "специальность аспирантуры"),
    )

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "специальность"
        verbose_name_plural = "специальности"
        app_label = "main_remote"

    name = models.CharField("наименование", max_length=500)
    code = models.CharField("код", max_length=20)
    type = models.CharField("направление", max_length=20, choices=PROGRAM_TYPE)
    divisions = RemoteManyToManyField(Division, verbose_name="подразделения",
                                      related_name="+", blank=True, remote_m2m_list=True)

    url = "/graduate/program"

    serialize_model = {
        "id": "id",
        "name": "name",
        "code": "code",
        "type": "type",
        "divisions": ("divisions", DivisionsSerializer)
    }

    query_names = {
        "name": ("name", "str"),
        "code": ("code", "startswith"),
        "class_code": ("classCode", "exact"),
        "type": ("type", "exact"),
    }

    allow_save = True
    allow_delete = True

    def __str__(self):
        return "{} - {} - {}".format(self.code, self.type, self.name)


class StudentProgram(RemoteNSIModel):
    """Model for program"""

    PT_BACHELOR = "BACHELOR"
    PT_MASTER = "MASTER"
    PT_SPECIALIST = "SPECIALIST"
    PT_POSTGRADUATE = "POSTGRADUATE"
    PT_FAKE = "FAKE"

    PROGRAM_TYPE = (
        (PT_BACHELOR, "бакалавриат"),
        (PT_MASTER, "магистратура"),
        (PT_SPECIALIST, "специалитет"),
        (PT_POSTGRADUATE, "аспирантура"),
        (PT_FAKE, ""),
    )

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "специальность"
        verbose_name_plural = "специальности"
        app_label = "main_remote"

    name = models.CharField("наименование", max_length=500)
    code = models.CharField("код", max_length=20)
    generation = RemoteForeignKey("main_remote.StudentGeneration", verbose_name="стандарт", null=True)
    type = models.CharField("направление", max_length=20, choices=PROGRAM_TYPE)
    divisions = RemoteManyToManyField(Division, verbose_name="подразделения",
                                      related_name="+", blank=True, remote_m2m_list=True)

    url = "/student/program"

    serialize_model = {
        "id": "id",
        "name": "name",
        "code": "code",
        "generation": ("generation_id", IdOrNoneSerializer()),
        "type": "type",
        "divisions": ("divisions", DivisionsSerializer)
    }

    query_names = {
        "name": ("name", "str"),
        "code": ("code", "startswith"),
        "class_code": ("classCode", "exact"),
        "type": ("type", "exact"),
    }

    allow_save = True
    allow_delete = True

    def __str__(self):
        s = "{} - {} - {}".format(self.code, self.get_type_display(), self.name)
        if self.generation:
            s = "{} - {}".format(self.generation, s)
        return s


class Topic(RemoteNSIModel):
    """Model for topics"""
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "тематика конференции"
        verbose_name_plural = "тематики конференции"
        app_label = "main_remote"

    name = models.CharField("название", max_length=500)

    url = "/topic"

    serialize_model = {
        "id": "id",
        "name": "name"
    }

    query_names = {
        "name": ("name", "str")
    }

    allow_save = True

    def __str__(self):
        return str(self.name)


class RemoteTextConferenceOrganizers(RemoteNSIModel):
    name = NoneEmptyRemoteSerializeCharField("название", max_length=256)

    def __str__(self):
        return self.name


class AcronymsSerializer:
    @staticmethod
    def serialize(local_field):
        return [sa for sa in (a.strip() for a in local_field.split(",")) if sa]

    @staticmethod
    def deserialize(remote_field):
        return ", ".join(remote_field)


class CitySerializer:
    @staticmethod
    def serialize(local_field):
        city_id, city_text, country_id, country_text = local_field
        country = Country.objects.get(id=country_id) if country_id else None
        country_name = country.name if country else country_text
        result = {
            "reference": {
                "id": city_id
            },
            "text": ("{}, {}".format(city_text, country_name) if country_name else city_text) if not city_id else None
        } if city_id or city_text else None
        return result

    @staticmethod
    def deserialize(remote_field):
        if remote_field is None:
            return None, None, None, None
        city = remote_field["reference"]
        if city is not None:
            if city["country"] is not None:
                country = city["country"]["reference"]
                country_text = city["country"]["text"]
                if country is not None:
                    return city["id"], None, country["id"], None
                else:
                    return city["id"], None, None, country_text
            else:
                return city["id"], None, None, None
        r = remote_field["text"].rsplit(",", 1)
        if len(r) == 2:
            return None, r[0], None, r[1]
        else:
            return None, r[0], None, None


class OrganizationSerializer:
    @staticmethod
    def serialize(local_field):
        org_id, text_org = local_field
        result = {
            "reference": {
                "id": org_id
            },
            "text": text_org if text_org else None
        } if org_id or text_org else None
        return result

    @staticmethod
    def deserialize(remote_field):
        org_id = None
        text_org = None
        if remote_field is not None:
            if remote_field["reference"] is not None:
                org_id = remote_field["reference"]["id"]
            else:
                text_org = remote_field["text"]
        return org_id, (text_org if text_org else "")


class OrganizersSerializer:
    @staticmethod
    def serialize(local_field):
        orgs, text_orgs = local_field
        result = []
        for o in orgs.all():
            result.append({
                "reference": {
                    "id": o.id
                }
            })
        for to in text_orgs.all():
            result.append({
                "text": to.name
            })
        return result

    @staticmethod
    def deserialize(remote_field):
        orgs = []
        text_orgs = []
        for o in remote_field:
            if o["reference"] is not None:
                orgs.append(Organization.objects.get(id=o["reference"]["id"]))
            else:
                text_orgs.append(RemoteTextConferenceOrganizers(name=o["text"]))
        return orgs, text_orgs


class TopicsSerializer:
    @staticmethod
    def serialize(local_field):
        return [{"id": t.id} for t in local_field.all()]

    @staticmethod
    def deserialize(remote_field):
        return [Topic.objects.get(id=t["id"]) for t in remote_field]


class RemoteConference(RemoteNSIModel):
    russian_name = models.CharField("название на русском", max_length=300)
    english_name = models.CharField("название на английском", max_length=300)
    # ToDo: maybe replace to acronyms list
    acronyms = models.CharField("аббревиатуры конференции", max_length=300)
    website = models.URLField("веб-сайт", blank=True, null=True)
    start_date = models.DateField("дата начала")
    end_date = models.DateField("дата окончания")
    country = RemoteForeignKey(Country, verbose_name="страна", null=True, blank=True, related_name="+")
    country_text = NoneEmptyRemoteSerializeCharField("страна", max_length=100, null=True, blank=True)
    city = RemoteForeignKey(City, verbose_name="город", null=True, blank=True, related_name="+")
    city_text = NoneEmptyRemoteSerializeCharField("город", max_length=100, null=True, blank=True)
    organization = RemoteForeignKey(Organization, verbose_name="учреждение",
                                    null=True, blank=True, related_name="+")
    organization_text = NoneEmptyRemoteSerializeCharField("учреждение", max_length=300,
                                         null=True, blank=True,)
    themes = RemoteManyToManyField(Topic, verbose_name="тематики конференции",
                                   related_name="+", blank=True, remote_m2m_list=True)
    organizers = RemoteManyToManyField(Organization, verbose_name="организаторы",
                                       related_name="+", blank=True, remote_m2m_list=True)
    organizers_text = RemoteManyToManyField(RemoteTextConferenceOrganizers, verbose_name="организаторы",
                                            related_name="+", blank=True, remote_m2m_list=True)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "конференция"
        verbose_name_plural = "конференции"
        app_label = "main_remote"

    def __str__(self):
        return "{}, {}' {} - {}".format(
            self.russian_name if self.russian_name else self.english_name,
            self.acronyms,
            util.datetime_to_string(self.start_date),
            util.datetime_to_string(self.end_date))

    serialize_model = {
        "id": "id",
        "nameRu": "russian_name",
        "nameEn": "english_name",
        "abbreviations": ("acronyms", AcronymsSerializer),
        "website": "website",
        "dateStart": "start_date",
        "dateEnd": "end_date",
        "placeCity": (["city_id", "city_text", "country_id", "country_text"], CitySerializer),
        "placeOrg": (["organization_id", "organization_text"], OrganizationSerializer),
        "organizers": (["organizers", "organizers_text"], OrganizersSerializer),
        "topics": ("themes", TopicsSerializer)
    }

    url = "/conference"

    query_names = {
        "russian_name": ("nameRu", "str"),
        "english_name": ("nameEn", "str"),
        "city": ("cityRef", "exact"),
        "city_text": ("cityText", "str"),
        "organization": ("orgRef", "exact"),
        "organization_text": ("orgText", "str")
    }

    custom_reverse_serialize = {
        "organization": ("placeOrg", "reference", Organization)
    }

    allow_save = True

    def get_absolute_url(self):
        return reverse("conference:dispatch_conference", kwargs={"pk": self.pk})

    def get_conf_part_create_url(self):
        return reverse("conference:confpart_create") + "?confId={}".format(self.pk)

    # noinspection PyUnusedLocal
    def allow_create_conf_part(self, user):
        return True


class ResultOwnerModel(RemoteModel):
    employee = RemoteForeignKey(Employee, blank=True, null=True)
    appointment = RemoteForeignKey(Appointment, blank=True, null=True)
    division = RemoteForeignKey(Division)
    contribution = models.FloatField()

    serialize_model = {
        "employeeId": "employee",
        "appointmentId": "appointment",
        "divisionId": "division",
        "contribution": "contribution"
    }


class FundingSource(RemoteCoreDeleteMixin, RemoteCoreResultModel):
    TYPE = "funding"

    name = models.CharField("название", max_length=200)
    short_name = models.CharField("краткое название", max_length=100, blank=True, default="")
    volume = models.CharField("объем", max_length=20, blank=True, default="")
    start_date = models.DateField("дата начала")
    end_date = models.DateField("дата окончания")
    organization = RemoteForeignKey(Organization, verbose_name="организация",
                                    null=True, blank=True, related_name="+")
    organization_text = NoneEmptyRemoteSerializeCharField("организация", max_length=300,
                                         null=True, blank=True)

    serialize_model = {
        "name": "name",
        "shortName": "short_name",
        "volume": "volume",
        "startDate": "start_date",
        "endDate": "end_date",
        "organization": (["organization_id", "organization_text"], OrganizationSerializer)
    }

    class Meta:
        verbose_name = "источник финансирования"
        verbose_name_plural = "источники финансирования"
        app_label = "main_remote"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type_kind = self.TK_FINANCE
        self.result_type_id = self.TYPE
        # TODO: funding result_type choosing?

    def __str__(self):
        return self.name

    @property
    def owners(self):
        return [ResultOwnerModel(division_id=0, contribution=1)]

    @property
    def full_name(self):
        current = self
        res = ""
        while current:
            if res:
                res = " > " + res
            res = current.name + res
            parents = current.parents.all()
            if parents.count() == 0:
                break
            current = parents[0].fundingsource
        return res

    @property
    def parent(self):
        parents = self.parents.all()
        return parents[0].fundingsource if parents.count() != 0 else None


class GrantParentSerializer:
    @staticmethod
    def serialize(local_field):
        return {"id": local_field} if local_field is not None else None

    @staticmethod
    def deserialize(remote_field):
        return remote_field["id"] if remote_field is not None else None


class GrantContainer(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        app_label = "grant"

    parent = models.ForeignKey('self', related_name="child_containers", null=True)
    name = models.CharField('Название', max_length=255, null=False)
    short_name = models.CharField('Краткое название', max_length=100, null=True)
    grant_url = models.URLField('URL', null=True)

    url = "/grant/container"

    query_names = {
        "parent": ("parent", "exact_or_null"),
        "name": ("name", "str"),
        "short_name": ("shortName", "str")
    }

    allow_save = True
    allow_delete = True

    @property
    def name_list(self):
        res = [self.name]
        if self.parent:
            res = self.parent.name_list + res
        return res

    @property
    def short_name_list(self):
        res = [self.short_name if self.short_name else self.name]
        if self.parent:
            res = self.parent.short_name_list + res
        return res

    @property
    def short_path(self):
        return " > ".join(self.short_name_list)

    @property
    def full_path(self):
        return " > ".join(self.name_list)

    def get_absolute_url(self):
        return reverse("grant:grant_container_edit", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.name)

GrantContainer.serialize_model = {
    "id": "id",
    "parent": ("parent_id", IdOrNoneSerializer(GrantContainer)),
    "name": "name",
    "shortName": "short_name",
    "url": "grant_url"
}


class Grant(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        app_label = "grant"

    parent = models.ForeignKey(GrantContainer, related_name="children", null=False)
    name = models.CharField('Название', max_length=255, null=False)
    short_name = models.CharField('Краткое название', max_length=100, null=True)
    grant_url = models.URLField('URL', null=True)
    max_funding = models.IntegerField('Макс. объем финансирования', null=True, validators=[MinValueValidator(1)])
    project_count = models.IntegerField('Число проектов', null=True, validators=[MinValueValidator(1)])
    single_project_max_funding = models.IntegerField('Макс. финансирование одного проекта', null=True, validators=[MinValueValidator(1)])
    date_start = models.DateField('Начало проекта', null=True)
    date_end = models.DateField('Окончание проекта ', null=True)
    app_date_start = models.DateField('Начало приема заявок', null=True)
    app_date_end = models.DateField('Окончание приема заявок ', null=True)
    app_address = models.CharField('Адрес приема заявок', max_length=255, null=True)
    person_max_project_count = models.IntegerField('Макс. число проектов от одного заявителя', null=True, validators=[MinValueValidator(1)])

    url = "/grant"

    serialize_model = {
        "id": "id",
        "parent": {
            "id": "parent"
        },
        "name": "name",
        "shortName": "short_name",
        "url": "grant_url",
        "maxFunding": "max_funding",
        "projectCount": "project_count",
        "singleProjectMaxFunding": "single_project_max_funding",
        "appDateStart": "app_date_start",
        "appDateEnd": "app_date_end",
        "appAddress": "app_address",
        "personMaxProjectCount": "person_max_project_count",
        "dateStart": "date_start",
        "dateEnd": "date_end"
    }

    query_names = {
        "parent": ("parent", "exact"),
        "name": ("name", "str"),
        "short_name": ("short_name", "str")
    }

    allow_save = True
    allow_delete = True

    def __str__(self):
        return str(self.name)

    @property
    def name_list(self):
        return self.parent.name_list + [self.name]

    @property
    def short_name_list(self):
        return self.parent.short_name_list + [self.short_name if self.short_name else self.name]

    @property
    def short_path(self):
        return " > ".join(self.short_name_list)

    @property
    def full_path(self):
        return " > ".join(self.name_list)

    def get_absolute_url(self):
        return reverse("grant:grant_edit", kwargs={"pk": self.pk})


class JournalClassifier(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "классификатор журнала"
        verbose_name_plural = "классификаторы журналов"
        app_label = "main_remote"

    code = models.IntegerField('Код', null=False)
    name_en = models.CharField('Название на английском', max_length=255, null=False)

    url = "/journal/classifier"

    serialize_model = {
        "id": "id",
        "code": "code",
        "nameEn": "name_en",
    }

    query_names = {
        "code": ("code", "exact"),
        "name_en": ("nameEn", "str"),
    }

    def __str__(self):
        return str("{} {}".format(self.code, self.name_en))


class JournalClassifierSerializer:
    @staticmethod
    def serialize(local_field):
        return [{"id": c.id} for c in local_field.all()]

    @staticmethod
    def deserialize(remote_field):
        return [JournalClassifier.objects.get(id=c["id"]) for c in remote_field]



class TemporalRemoteNSIModel(RemoteNSIModel):
    class Meta(RemoteNSIModel.Meta):
        abstract = True

    date_from = models.DateTimeField("Начало действия", null=True)
    date_to = models.DateTimeField("Конец действия", null=True)
    internalid = models.IntegerField("Внутренний id")

    serialize_model = {
        "activity": {
            "from": "date_from",
            "to": "date_to",
        },
        "internalId": "internalid"
    }

    custom_fieldtype_serializers = dict(RemoteNSIModel.custom_fieldtype_serializers)

    predefined_queries = {
        "active": lambda active:
            Q(date_to__isnull=True) | Q(date_to__gte=today_timestamp_milliseconds()) if active
            else Q(date_to__lt=today_timestamp_milliseconds()),
        "timestamp": lambda timestamp:  (Q(date_from__isnull=True) | Q(date_from__lte=timestamp)) &
                                        (Q(date_to__isnull=True) | Q(date_to__gte=timestamp))
    }


class Account(TemporalRemoteNSIModel):
    TYPE_CONTRACT = "CONTRACT"
    TYPE_PROGRAM5100 = "PROGRAM5100"
    TYPE_EDUCATION = "EDUCATION"

    TYPE_CHOICES = (
        (TYPE_CONTRACT, "НИОКР"),
        (TYPE_PROGRAM5100, "Программа 5-100"),
        (TYPE_EDUCATION, "Образование")
    )

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "лицевой счет"
        verbose_name_plural = "лицевые счета"
        app_label = "main_remote"

    number = models.CharField(verbose_name="номер", max_length=100)
    name = models.CharField(verbose_name="название", max_length=500, null=True, default=None)
    valid_from = models.DateField(verbose_name="дата начала")
    valid_to = models.DateField(verbose_name="дата окончания")
    type = models.CharField(verbose_name="тип", choices=TYPE_CHOICES, max_length=20)
    division = RemoteForeignKey(Division, verbose_name="подразделение", null=True, default=None)
    employee = RemoteForeignKey(Employee, verbose_name="ответственный", null=True, default=None)
    tags = RemoteManyToManyField(Tag, remote_m2m_list=True, verbose_name="теги", related_name="+")

    url = "/account"

    allow_save = True
    allow_delete = True

    serialize_model = dict({
        "id": "id",
        "number": "number",
        "name": "name",
        "validFrom": "valid_from",
        "validTo": "valid_to",
        "type": "type",
        "division": ("division_id", IdOrNoneSerializer()),
        "employee": ("employee_id", IdOrNoneSerializer())
    }, **TemporalRemoteNSIModel.serialize_model)

    predefined_queries = {
        "valid": lambda valid:
            Q(valid_from__lte=date.today()) & (Q(valid_to__isnull=True) | Q(valid_to__gte=date.today())) if valid
            else Q(valid_from__gt=date.today()) | Q(valid_to__lt=date.today())
    }
    predefined_queries.update(TemporalRemoteNSIModel.predefined_queries)

    def __str__(self):
        return self.number


class AccountIdSerializer:
    @staticmethod
    def serialize(local_field):
        return local_field if local_field is not None else None

    @staticmethod
    def deserialize(remote_field):
        return remote_field if remote_field is not None else None


class ResultFundingModel(models.Model, SerializableModel):
    account = RemoteForeignKey(Account, null=True)
    fraction = models.FloatField()
    result = models.ForeignKey(RemoteCoreResultModel, related_name="fundings")

    serialize_model = {
        "fundSource": ("account_id", AccountIdSerializer),
        "fraction": "fraction"
    }


class Journal(TemporalRemoteNSIModel):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "журнал"
        verbose_name_plural = "журналы"
        app_label = "main_remote"

    url = "/journal"
    allow_save = True
    allow_delete = True

    title_ru = models.CharField("Русское название", max_length=500)
    title_en = models.CharField("Английское название", max_length=500)
    journal_url = models.URLField("URL")  # this can't be called url as it overrides RemoteNSIModelBasic property otherwise
    issn = models.CharField("ISSN", max_length=200)
    e_issn = models.CharField("eISSN", max_length=200)
    publisher = models.CharField("Издательство", max_length=500)
    scopusid = models.CharField("ID в Scopus", max_length=200, null=True)
    spinid = models.IntegerField("ID в РИНЦ", null=True, default=None)
    classifiers = RemoteManyToManyField(
        JournalClassifier,
        related_name="+",
        remote_m2m_list=True,
        verbose_name="Классификаторы",
        blank=True
    )
    country = RemoteForeignKey(Country, verbose_name="Страна", related_name="+", null=True)
    impact_factor = models.FloatField("Импакт-фактор")
    snip = models.FloatField("SNIP")
    ipp = models.FloatField("IPP")
    sjr = models.FloatField("SJR")
    scopus_indexed = models.NullBooleanField()
    vak_indexed = models.NullBooleanField()
    wos_indexed = models.NullBooleanField()
    spin_indexed = models.NullBooleanField()

    serialize_model = dict({
        "id": "id",
        "titleRu": "title_ru",
        "titleEn": "title_en",
        "url": "journal_url",
        "printISSN": "issn",
        "eISSN": "e_issn",
        "publisher": "publisher",
        "scopusId": "scopusid",
        "spinId": "spinid",
        "classifiers": ("classifiers", JournalClassifierSerializer),
        "country": ("country_id", IdOrNoneSerializer(Country)),
        "impactFactor": "impact_factor",
        "snip": "snip",
        "ipp": "ipp",
        "sjr": "sjr",
        "scopusIndexed": "scopus_indexed",
        "vakindexed": "vak_indexed",
        "wosindexed": "wos_indexed",
        "spinindexed": "spin_indexed",
    }, **TemporalRemoteNSIModel.serialize_model)

    query_names = {
        "issn": ("printISSN", "exact"),
        "e_issn": ("eISSN", "exact"),
        "title_en": ("titleEn", "str"),
        "title_ru": ("titleRu", "str"),
        "internalid": ("internalId", "exact"),
        "timestamp": ("timestamp", "exact"),
        "scopusid": ("scopusId", "exact")
    }

    def __str__(self):
        return self.title_ru if self.title_ru else self.title_en


class PostgraduateSupervisor(RemoteNSIModel, NamedPersonMixin):

    class Meta(RemoteNSIModelBasic.Meta):
        verbose_name = "руководитель аспиранта"
        verbose_name_plural = "руководители аспирантов"
        app_label = "main_remote"

    remote_id = models.IntegerField("id в csv", null=True)

    last_name = models.CharField("фамилия", max_length=500)
    first_name = models.CharField("имя", max_length=500)
    middle_name = models.CharField("отчество", max_length=500, null=True)

    gender = models.CharField("пол", max_length=1, null=True)
    date_birth = models.DateField("дата рождения", null=True)

    employee = RemoteForeignKey(Employee, verbose_name="сотрудник", null=True)
    division = RemoteForeignKey(Division, verbose_name="подразделение", null=True)

    is_staff = models.NullBooleanField("является сотрудником")

    allow_save = True
    allow_delete = True
    url = "/graduate/supervisor"

    serialize_model = {
        "id": "id",
        "remoteId": "remote_id",
        "lastName": "last_name",
        "firstName": "first_name",
        "middleName": "middle_name",
        "gender": "gender",
        "dateBirth": "date_birth",
        "employee": ("employee_id", IdOrNoneSerializer(Employee)),
        "division": ("division_id", IdOrNoneSerializer(Division)),
        "staff": "is_staff"
    }

    @property
    def brief_name(self):
        names = '{0} {1}.'.format(self.last_name, self.first_name.upper()[0])
        if self.middle_name:
            names += " {0}.".format(self.middle_name.upper()[0])
        return names

    def __str__(self):
        return self.full_name


class PostgraduateCategory(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "категория аспиранта"
        verbose_name_plural = "категории аспиранта"
        app_label = "main_remote"

    name = models.CharField("название", max_length=500, null=True)

    allow_save = True
    allow_delete = True
    url = "/graduate/category"

    serialize_model = {
        "id": "id",
        "name": "name"
    }

    def __str__(self):
        return str(self.name)


class PostgraduateFireReason(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "причина отчисления аспиранта"
        verbose_name_plural = "причины отчисления аспиранта"
        app_label = "main_remote"

    name = models.CharField("название", max_length=500, null=True)

    allow_save = True
    allow_delete = True
    url = "/graduate/firereason"

    serialize_model = {
        "id": "id",
        "name": "name"
    }

    def __str__(self):
        return str(self.name)


class Postgraduate(RemoteNSIModel, NamedPersonMixin, AccessByDivisionMixin):

    class Meta(RemoteNSIModelBasic.Meta):
        verbose_name = "аспирант"
        verbose_name_plural = "аспиранты"
        app_label = "main_remote"

    last_name = models.CharField("фамилия", max_length=500)
    first_name = models.CharField("имя", max_length=500)
    middle_name = models.CharField("отчество", max_length=500, null=True)

    gender = models.CharField("пол", max_length=1)
    date_birth = models.DateField("дата рождения")

    area = RemoteForeignKey(PostgraduateProgram, verbose_name="направление", null=True, related_name="postgraduates")
    speciality = RemoteForeignKey(PostgraduateProgram, verbose_name="специальность", null=True, related_name="postgraduates2")

    enrollment = models.DateField("дата зачисления", null=True)
    exclusion = models.DateField("дата отчисления", null=True)
    protection = models.DateField("дата защиты", null=True)

    country = RemoteForeignKey(Country, verbose_name="страна", null=True)

    supervisor = RemoteForeignKey(PostgraduateSupervisor, verbose_name="руководитель", null=True, related_name="postgraduates")
    supervisor2 = RemoteForeignKey(PostgraduateSupervisor, verbose_name="второй руководитель", null=True, related_name="postgraduates2")
    division = RemoteForeignKey(Division, verbose_name="подразделение")
    is_commercial = models.BooleanField("является коммерческим", default=False)

    category = RemoteForeignKey(PostgraduateCategory, verbose_name="категория")
    fire_reason = RemoteForeignKey(PostgraduateFireReason, verbose_name="причина отчисления", null=True)

    allow_save = True
    allow_delete = True
    url = "/graduate"

    serialize_model = {
        "id": "id",
        "lastName": "last_name",
        "firstName": "first_name",
        "middleName": "middle_name",
        "gender": "gender",
        "dateBirth": "date_birth",
        "area": ("area_id", IdOrNoneSerializer()),
        "speciality": ("speciality_id", IdOrNoneSerializer()),
        "validFrom": "enrollment",
        "validTo": "exclusion",
        "graduateDate": "protection",
        "country": ("country_id", IdOrNoneSerializer()),
        "supervisor": ("supervisor_id", IdOrNoneSerializer()),
        "supervisor2": ("supervisor2_id", IdOrNoneSerializer()),
        "division": ("division_id", IdOrNoneSerializer()),
        "commercial": "is_commercial",
        "category": ("category_id", IdOrNoneSerializer()),
        "firereason": ("fire_reason_id", IdOrNoneSerializer())
    }

    predefined_queries = {
        "period_start": lambda period_start:
            Q(exclusion__isnull=True) | Q(exclusion__gte=period_start),
        "period_end": lambda period_end:
            Q(enrollment__isnull=True) | Q(enrollment__lte=period_end),
        "valid": lambda valid:
            Q(enrollment_isnull=False) & Q(enrollment__lte=date.today()) &
                (Q(exclusion__isnull=True) | Q(exclusion__gte=date.today())) if valid
            else Q(enrollment__isnull=True) | Q(enrollment__gt=date.today()) |
                Q(exclusion__isnull=False) & Q(exclusion__lt=date.today())
    }

    export_fields = [
        {
            "label": "Фамилия",
            "field": "last_name",
        },
        {
            "label": "Имя",
            "field": "first_name",
        },
        {
            "label": "Отчество",
            "field": "middle_name",
        },
        {
            "label": "Пол",
            "field": "gender",
        },
        {
            "label": "Дата рождения",
            "function": lambda obj: obj.date_birth.strftime("%d.%m.%Y") if obj.date_birth else '',
        },
        {
            "label": "Категория",
            "field": "category"
        },
        {
            "label": "Направление подготовки",
            "function": lambda obj: obj.area.name if hasattr(obj, "area") and obj.area else '',
        },
        {
            "label": "Специальность",
            "function": lambda obj: obj.speciality.name if hasattr(obj, "speciality") and obj.speciality else '',
        },
        {
            "label": "Зачисление",
            "function": lambda obj: obj.enrollment.strftime("%d.%m.%Y") if obj.enrollment else '',
        },
        {
            "label": "Отчисление",
            "function": lambda obj: obj.exclusion.strftime("%d.%m.%Y") if obj.exclusion else '',
        },
        {
            "label": "Защита",
            "function": lambda obj: obj.protection.strftime("%d.%m.%Y") if obj.protection else '',
        },
        {
            "label": "Страна",
            "function": lambda obj: obj.country.name if hasattr(obj, "country") and obj.country else '',
        },
        {
            "label": "Руководитель",
            "function": lambda obj: obj.supervisor.brief_name if hasattr(obj, "supervisor") and obj.supervisor else ''
        },
        {
            "label": "Второй руководитель",
            "function": lambda obj: obj.supervisor2.brief_name if hasattr(obj, "supervisor2") and obj.supervisor2 else ''
        },
        {
            "label": "Институт",
            "function": lambda obj:
                obj.division.parent.abbrv if hasattr(obj, "division") and obj.division and
                hasattr(obj.division, "parent") and obj.division.parent else ''
        },
        {
            "label": "Кафедра",
            "function": lambda obj:
                obj.division.abbrv if hasattr(obj, "division") and obj.division else ''
        },
        {
            "label": "Является коммерческим",
            "function": lambda obj: "" if obj.is_commercial is None else ("да" if obj.is_commercial else "нет")
        },
        {
            "label": "Причина отчисления",
            "field": "fire_reason"
        },
    ]

    def __str__(self):
        return self.full_name


class Parcel(RemoteNSIModelBasic):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "земельный участок"
        verbose_name_plural = "земельные участки"
        app_label = "main_remote"

    url = '/parcel'
    allow_save = True
    allow_delete = True

    serialize_model = {
        'id': 'id',
        'address': 'address',
        'cadastrNum': 'cadastr_num'
    }

    id = models.CharField(max_length=255, primary_key=True, blank=True)
    cadastr_num = models.CharField("Кадастровый номер", max_length=255, null=True)
    address = models.CharField("Адрес", max_length=255)


class Building(RemoteNSIModelBasic):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "здание"
        verbose_name_plural = "здания"
        app_label = "main_remote"

    url = '/building'
    allow_save = True
    allow_delete = True

    serialize_model = {
        'id': 'id',
        'parcel': ('parcel_id', IdOrNoneSerializer(Parcel)),
        'name': 'name',
        'address': 'address',
        'cadastrNum': 'cadastr_num',
        'buildYear': 'build_year',
        'floors': 'floors',
        'space': 'space'
    }

    id = models.CharField(max_length=255, primary_key=True, blank=True)
    parcel = RemoteForeignKey(Parcel, verbose_name="участок")
    name = models.CharField("Название", max_length=255, null=True)
    address = models.CharField("Адрес", max_length=255, null=True)
    cadastr_num = models.CharField("Кадастровый номер", max_length=255, null=True)
    build_year = models.CharField("Год постройки", max_length=255, null=True)
    floors = models.CharField("Этажность", max_length=255, null=True)
    space = models.FloatField("Суммарная площадь", null=True)

    def __str__(self):
        return self.name if self.name else ""


class LocationKindGroup(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "группа категорий исп. помещения"
        verbose_name_plural = "группы категорий исп. помещения"
        app_label = "main_remote"

    name = models.CharField("название", max_length=255, null=True)
    description = models.CharField("описание", max_length=255, null=True)

    allow_save = True
    allow_delete = True
    url = "/location/kindgroup"

    serialize_model = {
        "id": "id",
        "name": "name",
        "description": "description"
    }

    def __str__(self):
        return str(self.name)


class LocationKind(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "категория исп. помещения"
        verbose_name_plural = "категория исп. помещения"
        app_label = "main_remote"

    name = models.CharField("название", max_length=255, null=True)
    group = RemoteForeignKey(LocationKindGroup, verbose_name="группа")

    allow_save = True
    allow_delete = True
    url = "/location/kind"

    serialize_model = {
        "id": "id",
        "name": "name",
        "group": ("group_id", IdOrNoneSerializer(LocationKindGroup))
    }

    def __str__(self):
        return str(self.name)


class LocationNormKind(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "категория норм. использования помещения"
        verbose_name_plural = "категории норм. использования помещения"
        app_label = "main_remote"

    name = models.CharField("название", max_length=255, null=True)

    allow_save = True
    allow_delete = True
    url = "/location/normkind"

    serialize_model = {
        "id": "id",
        "name": "name"
    }

    def __str__(self):
        return str(self.name)


class Location(RemoteNSIModelBasic, AccessByDivisionMixin):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "помещение"
        verbose_name_plural = "помещения"
        app_label = "main_remote"

    id = models.CharField(max_length=255, primary_key=True, blank=True)
    building = RemoteForeignKey(Building, verbose_name="здание")
    floor = models.CharField("Этаж", max_length=255)
    number = models.CharField("Номер", max_length=255, null=True)
    kind = RemoteForeignKey(LocationKind, verbose_name="категория", null=True)
    norm_kind = RemoteForeignKey(LocationNormKind, verbose_name="использование", null=True)
    space = models.FloatField("Площадь", null=True)
    height = models.FloatField("Высота", null=True)
    division = RemoteForeignKey(Division, verbose_name="Подразделение")

    url = '/location'
    allow_save = True
    allow_delete = True

    serialize_model = {
        'id': 'id',
        'building': ('building_id', IdOrNoneSerializer(Building)),
        'floor': 'floor',
        'number': 'number',
        'kind': ('kind_id', IdOrNoneSerializer(LocationKind)),
        'normKind': ('norm_kind_id', IdOrNoneSerializer(LocationNormKind)),
        'space': 'space',
        'height': 'height',
        'division': {'id': 'division'}
    }

    export_fields = [
        {
            "label": "Корпус",
            "field": "building",
        },
        {
            "label": "Этаж",
            "field": "floor",
        },
        {
            "label": "Номер",
            "field": "number",
        },
        {
            "label": "Подразделение",
            "field": "division",
        },
        {
            "label": "Использование",
            "field": "norm_kind",
        },
        {
            "label": "Категория",
            "field": "kind",
        },
        {
            "label": "Площадь (м. кв.)",
            "field": "space",
        },
        {
            "label": "Высота (м.)",
            "field": "height",
        }
    ]


class DissertationCouncil(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "диссертационный совет"
        verbose_name_plural = "диссертационные советы"
        app_label = "main_remote"

    code = models.CharField("шифр совета", max_length=255)
    date_from = models.DateField("дата открытия")
    date_to = models.DateField("дата закрытия", null=True)

    allow_save = True
    allow_delete = True
    url = "/disscouncil"

    serialize_model = {
        "id": "id",
        "code": "code",
        "dateStart": "date_from",
        "dateEnd": "date_to"
    }

    export_fields = [
        {
            "label": "Шифр совета",
            "field": "code",
        },
        {
            "label": "Дата открытия",
            "function": lambda obj: obj.date_from.strftime("%d.%m.%Y") if obj.date_from else ""
        },
        {
            "label": "Дата закрытия",
            "function": lambda obj: obj.date_to.strftime("%d.%m.%Y") if obj.date_to else ""
        },
        {
            "label": "Число членов (текущее)",
            "function": lambda obj: obj.members.filter(Q(date_to=None) | Q(date_to__gte=date.today())).count()
        },
        {
            "label": "Число членов (за все время)",
            "function": lambda obj: obj.members.count()
        }
    ]


    def is_closed(self):
        return self.date_to is not None and self.date_to < date.today()

    def get_absolute_url(self):
        return reverse("disscouncil:disscouncil_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return str(self.code)


class StudentState(RemoteNSIAbstractNamedModel):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "статус студента"
        verbose_name_plural = "статусы студента"
        app_label = "main_remote"

    allow_save = True
    allow_delete = True
    url = "/student/state"

    is_active = models.NullBooleanField(verbose_name="активно")

    serialize_model = dict(RemoteNSIAbstractNamedModel.serialize_model)
    serialize_model.update({
        "isActive": "is_active"
    })


class StudentPrivilege(RemoteNSIAbstractNamedModel):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "тип льготников"
        verbose_name_plural = "типы льготников"
        app_label = "main_remote"

    allow_save = True
    allow_delete = True
    url = "/student/privilege"


class StudentGeneration(RemoteNSIAbstractNamedModel):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "поколение стандарта"
        verbose_name_plural = "поколение стандартов"
        app_label = "main_remote"

    allow_save = True
    allow_delete = True
    url = "/student/generation"

    code = models.CharField(verbose_name="код", max_length=255)

    serialize_model = dict(RemoteNSIAbstractNamedModel.serialize_model)
    serialize_model.update({
        "code": "code"
    })

    def __str__(self):
        return str(self.code)


class StudentExamType(RemoteNSIAbstractNamedModel):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "тип экзамена"
        verbose_name_plural = "типы экзаменов"
        app_label = "main_remote"

    allow_save = True
    allow_delete = True
    url = "/student/exam/type"


class StudentEducationForm(RemoteNSIAbstractNamedModel):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "форма обучения"
        verbose_name_plural = "формы обучения"
        app_label = "main_remote"

    allow_save = True
    allow_delete = True
    url = "/student/edu/form"


class StudentGroup(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "учебная группа"
        verbose_name_plural = "учебные группы"
        app_label = "main_remote"

    number = models.CharField("название", max_length=255)
    division = RemoteForeignKey(Division, verbose_name="подразделение")

    allow_save = True
    allow_delete = True
    url = "/student/group"

    serialize_model = {
        "id": "id",
        "number": "number",
        "division": {
            "id": "division"
        }
    }

    def __str__(self):
        return str(self.number)


class Student(RemoteNSIModel, NamedPersonMixin, AccessByDivisionMixin):
    division_field = "data__division"

    GENDER_CHOICE_M = "м"
    GENDER_CHOICE_F = "ж"
    GENDER_CHOICES = (
        (GENDER_CHOICE_M, "мужской"),
        (GENDER_CHOICE_F, "женский")
    )

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "студент"
        verbose_name_plural = "студенты"
        app_label = "main_remote"

    last_name = models.CharField("фамилия", max_length=255)
    first_name = models.CharField("имя", max_length=255)
    middle_name = models.CharField("отчество", max_length=255, null=True)
    gender = models.CharField("пол", max_length=1, choices=GENDER_CHOICES)
    date_birth = models.DateField("дата рождения", null=True)
    country = RemoteForeignKey(Country, verbose_name="гражданство", null=True)
    region = models.CharField("регион", max_length=255, null=True)
    email = models.CharField("email", max_length=255, null=True)
    phone = models.CharField("телефон", max_length=255, null=True)

    allow_save = True
    allow_delete = True
    url = "/student"

    serialize_model = {
        "id": "id",
        "lastName": "last_name",
        "firstName": "first_name",
        "middleName": "middle_name",
        "gender": "gender",
        "dateBirth": "date_birth",
        "country": ("country_id", IdOrNoneSerializer(Country)),
        "region": "region",
        "email": "email",
        "phone": "phone"
    }

    custom_reverse_serialize = {
        "science_info": ("scienceInfo", ScienceInfo)
    }

    predefined_queries = {
        "timestamp": lambda timestamp:
            (Q(history__activity_from__exact=None) | Q(history__activity_from__lte=timestamp)) &
            (Q(history__activity_to__exact=None) | Q(history__activity_to__gte=timestamp))
    }

    @property
    def age(self):
        today = date.today()
        if self.date_birth and hasattr(self.date_birth, "year") \
                and hasattr(self.date_birth, "month") and hasattr(self.date_birth, "day"):
            correction = int((today.month, today.day) < (self.date_birth.month, self.date_birth.day))
            return (today.year - self.date_birth.year) - correction
        else:
            return None

    def __get_one_data_field(self, field_name, func):
        history = self.history.filter(timestamp=date.today())
        if history.count() == 0:
            return None
        elif history.count() == 1:
            return getattr(history[0], field_name)
        else:
            lst = [getattr(h, field_name) for h in history]
            return func(lst) if lst else None

    def __get_list_data_field(self, field_name, timestamp=None):
        if timestamp is None:
            timestamp = date.today()
        return {getattr(h, field_name) for h in self.history.filter(timestamp=timestamp)}

    def __get_list_valid_data_field(self, field_name):
        today = date.today()
        return {getattr(h, field_name) for h in self.history.filter(timestamp=today, state__is_active=True)}

    @property
    def groups(self, timestamp=None):
        return self.__get_list_data_field("group", timestamp)

    def divisions(self, timestamp=None):
        return self.__get_list_data_field("division", timestamp)

    @property
    def valid_from(self):
        return self.__get_one_data_field("valid_from", lambda lst: min([l for l in lst if l is not None]))

    @property
    def valid_to(self):
        return self.__get_one_data_field("valid_to", lambda lst: None if None in lst else max(lst))

    export_fields = [
        {
            "label": "Фамилия",
            "field": "last_name",
        },
        {
            "label": "Имя",
            "field": "first_name",
        },
        {
            "label": "Отчество",
            "field": "middle_name",
        },
        {
            "label": "Возраст",
            "field": "age",
        }
    ]

    def __str__(self):
        return self.red_tape_full_name


class StudentExam(RemoteNSIModel):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "экзамен"
        verbose_name_plural = "экзамены"
        app_label = "main_remote"

    type = RemoteForeignKey(StudentExamType, verbose_name="экзамен")
    value = IntegerField(verbose_name="баллы")

    serialize_model = {
        "type": ("type_id", IdOrNoneSerializer()),
        "value": "value"
    }

    def __str__(self):
        return "{} - {}".format(self.type, self.value)


class StudentDataHistoryComment(RemoteNSIModel):
    class Meta(RemoteNSIModel.Meta):
        app_label = "main_remote"

    report_date = models.DateField(verbose_name="дата приказа", null=True)
    comment = models.CharField(verbose_name="комментарий", max_length=255, null=True)
    report = models.CharField(verbose_name="номер приказа", max_length=255, null=True)

    serialize_model = {
        "reportDate": "report_date",
        "comment": "comment",
        "report": "report"
    }

    def __str__(self):
        return self.comment


class StudentDataHistory(RemoteNSIModel):
    class Meta(RemoteNSIModel.Meta):
        verbose_name = "история данных о студенте"
        verbose_name_plural = "история данных о студентах"
        app_label = "main_remote"

    internal_id = models.IntegerField(blank=False, null=False)
    activity_from = models.DateField(blank=True, null=True)
    activity_to = models.DateField(blank=True, null=True)

    student = RemoteForeignKey(Student, verbose_name="студент", related_name="history")
    division = RemoteForeignKey(Division, verbose_name="подразделение")
    group = RemoteForeignKey(StudentGroup, verbose_name="группа")
    education_form = RemoteForeignKey(StudentEducationForm, verbose_name="форма обучения")
    contract = models.BooleanField(verbose_name="контрактный студент", default=False)
    speciality = RemoteForeignKey(StudentProgram, verbose_name="направление")
    valid_from = models.DateField(verbose_name="дата поступления", null=True)
    valid_to = models.DateField(verbose_name="дата отчисления", null=True)
    state = RemoteForeignKey(StudentState, verbose_name="статус")
    purpose = models.BooleanField(verbose_name="целевое назначение", default=False)
    purpose_org = models.CharField(verbose_name="заказчик целевого назначения", max_length=255, null=True)
    diploma_date = models.DateField(verbose_name="дата защиты", null=True)
    diploma_result = models.CharField(verbose_name="результат защиты", max_length=255, null=True)
    privileges = RemoteManyToManyField(StudentPrivilege, verbose_name="льготы", remote_m2m_list=True, blank=True,
                                       related_name="+")
    exams = RemoteManyToManyField(StudentExam, verbose_name="экзамены", remote_m2m_list=True, blank=True,
                                  related_name="data")
    comments = RemoteManyToManyField(StudentDataHistoryComment, verbose_name="комментарии", remote_m2m_list=True,
                                     blank=True, related_name="+")

    allow_save = True
    allow_delete = True
    url = "/student/data/history"

    serialize_model = {
        "id": "id",
        "internalId": "internal_id",
        "activeFrom": "activity_from",
        "activeTo": "activity_to",
        "student": ("student_id", IdOrNoneSerializer()),
        "division": ("division_id", IdOrNoneSerializer()),
        "group": ("group_id", IdOrNoneSerializer()),
        "educationForm": ("education_form_id", IdOrNoneSerializer()),
        "contract": "contract",
        "speciality": ("speciality_id", IdOrNoneSerializer()),
        "validFrom": "valid_from",
        "validTo": "valid_to",
        "state": ("state_id", IdOrNoneSerializer()),
        "purpose": "purpose",
        "purposeOrg": "purpose_org",
        "diplomaDate": "diploma_date",
        "diplomaResult": "diploma_result",
        "privileges": ("privileges", ListSerializer(StudentPrivilege)),
        "exams": ("exams", ListSerializer(StudentExam)),
        "comments": ("comments", ListSerializer(StudentDataHistoryComment))
    }

    predefined_queries = {
        "valid": lambda valid: Q(state__is_active=True) if valid else Q(state__is_active=False),
        "timestamp": lambda timestamp:
            (Q(activity_from__exact=None) | Q(activity_from__lte=timestamp)) &
            (Q(activity_to__exact=None) | Q(activity_to__gte=timestamp))
    }

    def is_valid(self):
        return self.state.is_active

    def __str__(self):
        return "{} {} ({})".format(self.student, self.group, self.division.abbrv)


class FiasParentSerializer:

    def __init__(self, model):
        self.model = model

    def serialize(self, value):
        return value.guid

    def deserialize(self, value):
        if value:
            return self.model.objects.get(guid=value, act_status=1)
        else:
            return None


class FiasAddress(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "адресный объект"
        verbose_name_plural = "адресные объекты"
        app_label = "main_remote"

    region_code = models.CharField(verbose_name="код региона", max_length=2)
    formal_name = models.CharField(verbose_name="название", max_length=100)
    short_name = models.CharField(max_length=50)
    guid = models.CharField(max_length=100)
    act_status = models.IntegerField(verbose_name="статус")
    level = models.IntegerField(verbose_name="уровень")
    parent = RemoteForeignKey("self", related_name="children", null=True, blank=True)

    url = "/fias/address"

    serialize_model = {
        "id": "id",
        "regionCode": "region_code",
        "formalName": "formal_name",
        "shortName": "short_name",
        "guid": "guid",
        "actStatus": "act_status",
        "level": "level"
    }

    TYPE_BEFORE = ["г", "респ"]

    def __str__(self):
        if self.short_name.lower() in self.TYPE_BEFORE:
            return "{} {}".format(self.short_name, self.formal_name)
        else:
            return "{} {}".format(self.formal_name, self.short_name)


class MaterialPoint(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "материальная точка"
        verbose_name_plural = "материальные точки"
        app_label = "main_remote"

    number = models.CharField(verbose_name="номер мат.точки", max_length=32)
    responsible_person = RemoteForeignKey(Employee, verbose_name="ответственное лицо", related_name="+", null=True)
    divisions = RemoteManyToManyField(Division, verbose_name="подразделения",
                                      remote_m2m_list=True, blank=True, related_name="+")
    identifier = models.CharField(verbose_name="идентификатор", max_length=32, null=True)
    raw_responsible_person = models.CharField(verbose_name="нераспознанное отв. лицо", max_length=255, null=True)
    raw_division = models.CharField(verbose_name="нераспознанное подразделение", max_length=255, null=True)

    url = "/material_point"

    allow_save = True
    allow_delete = True

    serialize_model = {
        "id": "id",
        "number": "number",
        "employee": ("responsible_person_id", IdOrNoneSerializer()),
        "divisions": ("divisions", DivisionsSerializer),
        "identifier": "identifier",
        "rawEmployee": "raw_responsible_person",
        "rawDivision": "raw_division",
    }

    def __str__(self):
        divisions = ", ".join([str(d) for d in self.divisions.all()])
        return "%s%s" % (
            self.identifier if self.identifier else "?",
            (" (%s)" % divisions) if divisions else ""
        )


class MoocPlatform(RemoteNSIModel):

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "МООК-платформа"
        verbose_name_plural = "МООК-платформы"
        app_label = "main_remote"

    name = models.CharField(verbose_name="имя", max_length=255)
    platform_url = models.URLField(verbose_name="URL", max_length=255)

    allow_save = True
    allow_delete = True

    url = "/mooc_platform"

    serialize_model = {
        "id": "id",
        "name": "name",
        "url": "platform_url"
    }

    def __str__(self):
        return "{} ({})".format(self.name, self.platform_url)



Employee.custom_reverse_serialize["appointments"] = ("appointments", Appointment)
Employee.custom_reverse_serialize["appointments_any"] = ("appointments$any", Appointment)
Employee.custom_reverse_serialize["appointments_all"] = ("appointments$all", Appointment)

Student.custom_reverse_serialize["history"] = ("history", StudentDataHistory)

FiasAddress.serialize_model["parentGuid"] = ("parent", FiasParentSerializer(FiasAddress))
