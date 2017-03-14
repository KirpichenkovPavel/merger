from inspect import isclass
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from core_client.queries import core
from django_remote_model.serializers import DefaultModelSerializer, DateTimeSerializer, DateStringSerializer, \
    CoreResultModelSerializer, NoneEmptyStringSerializer, DateIntSerializer, DecimalSerializer
from django_remote_model.managers import RemoteManager, RemoteNSIManager, FakeManager, RemoteCoreManager, \
    RemoteLdapProxyManager
from ldap_proxy_client.queries import ldap_proxy
from nsi_client.queries import nsi
from remote_impl.remote_database_exception import RemoteDatabaseError


class NoneEmptyRemoteSerializeCharField(models.CharField):
    pass


class SerializableModel:
    # Same json model as REST used but instead of values of fields there are tuples
    # (local_name, serializer), where
    # local_name - name of field in model
    # serializer - serializer/deserializer for this field (if need)
    serialize_model = {}

    # dict {field_type: serializer}
    custom_fieldtype_serializers = {
        models.DecimalField: DecimalSerializer
    }

    @classmethod
    def get_serializer(cls):
        return DefaultModelSerializer(cls)

    def serialize(self):
        return self.get_serializer().serialize(self)

    @staticmethod
    def _convert_model_for_query(model):
        result = {}
        for r, l in model.items():
            if isinstance(l, str):
                result[r] = l
            elif isinstance(l, tuple):
                f = l[0]
                serializer = l[1]
                if hasattr(serializer, "get_model_for_query"):
                    result[r] = serializer.get_model_for_query(f)
                elif isinstance(f, str):
                    result[r] = f
            elif isinstance(l, dict):
                result[r] = SerializableModel._convert_model_for_query(l)
        return result

    @classmethod
    def get_serializable_model_for_query(cls):
        return cls._convert_model_for_query(cls.serialize_model)


class RemoteModel(models.Model, SerializableModel):

    class Meta:
        managed = False
        abstract = True

    objects = RemoteManager()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        pass

    def save_base(self, raw=False, force_insert=False, force_update=False, using=None, update_fields=None):
        pass

    def delete(self, using=None):
        pass


class RemoteNSIModelBasic(RemoteModel):

    class Meta(RemoteModel.Meta):
        abstract = True
    _client = nsi
    objects = RemoteNSIManager()

    LOCAL_ID_NAME = "id"
    url = ""

    allow_save = False
    allow_delete = False

    # dict to translate local name to query with group of allowed queries
    # {local_name: (query_name, allowed_query_group)}
    query_names = {}
    # dict to translate Django filters to query filters
    query_filters = {
        "exact": "",
        "startswith": "_startswith",
        "istartswith": "_startswith",
        "contains": "_contains",
        "icontains": "_contains",
        "isnull": "_isnull",
        "gte": "_gte",
        "lte": "_lte"
    }
    # dict of groups of allowed queries
    allowed_query_groups = {
        "exact": ["exact"],
        "exact_or_null": ["exact", "isnull"],
        "str": ["exact", "startswith", "istartswith", "contains", "icontains"],
        "startswith": ["startswith", "istartswith"],
        "gtelte": ["gte", "lte"]
    }
    custom_fieldtype_serializers = dict(RemoteModel.custom_fieldtype_serializers)
    custom_fieldtype_serializers.update({
        models.DateTimeField: DateTimeSerializer,
        models.DateField: DateStringSerializer,
        models.DecimalField: DecimalSerializer,
        NoneEmptyRemoteSerializeCharField: NoneEmptyStringSerializer
    })

    _reversed_serialize_model = None
    reverse_serialize_ignored_fields = {}
    custom_reverse_serialize = {}
    predefined_queries = {}

    @classmethod
    def get_predefined_query(cls, k, v):
        query = cls.predefined_queries.get(k)
        if query is None:
            return None
        if callable(query):
            return query(v)
        return query

    @classmethod
    def _reverse_field(cls, result, l, r, prefix):
        is_foreign_key = False
        is_m2m = False
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
                elif isinstance(field_type, models.ManyToManyField):
                    is_m2m = True
        if is_foreign_key and issubclass(field_type.rel.to, RemoteNSIModelBasic):
            result[l] = prefix + (field_type.rel.to,)
        elif is_m2m and issubclass(field_type.rel.to, RemoteNSIModelBasic):
            result[l] = prefix + (field_type.rel.to,)
            if len(prefix) > 0:
                result[l + "_any"] = prefix[:-1] + (prefix[-1] + "$any", field_type.rel.to)
                result[l + "_all"] = prefix[:-1] + (prefix[-1] + "$all", field_type.rel.to)
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
        rf = cls._reversed_serialize_model.get(field[0] if field[0] != "pk" else cls._meta.pk.name)
        if rf is None:
            return None

        sub_model = None

        if len(rf) > 0 and isclass(rf[-1]) and issubclass(rf[-1], models.Model):
            sub_model = rf[-1]
            rf = rf[:-1]

        if sub_model is not None and len(field) == 1:
            field = field + [sub_model._meta.pk.name]

        if len(field) > 1:
            if sub_model is None:
                return None
            sub_rf = sub_model.get_reversed_serialize_field(field[1:])
            if sub_rf is None:
                return None
            else:
                return rf + sub_rf
        else:
            return rf

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.allow_save:
            assert not (force_insert and force_update)
            if force_insert:
                try:
                    save_res = self._client.create_object(self)
                except RemoteDatabaseError as rdbe:
                    raise RemoteDatabaseError("Unable to save new {} object".format(self.__class__.__name__),
                                              remote_error_json=rdbe.remote_error_json)
                else:
                    self.pk = save_res.pk
            elif force_update:
                if self.pk is None:
                    raise ValueError("Unable to save edited {} object without id".format(self.__class__.__name__))
                try:
                    save_res = self._client.modify_object(self)
                except RemoteDatabaseError as rdbe:
                    raise RemoteDatabaseError("Unable to save edited {} object".format(self.__class__.__name__),
                                              remote_error_json=rdbe.remote_error_json)
            else:
                if self.pk is not None:
                    try:
                        save_res = self._client.modify_object(self)
                    except RemoteDatabaseError:
                        failed = True
                    else:
                        failed = False
                if self.pk is None or failed:
                    try:
                        save_res = self._client.create_object(self)
                    except RemoteDatabaseError as rdbe:
                        raise RemoteDatabaseError("Unable to save new {} object".format(self.__class__.__name__),
                                                  remote_error_json=rdbe.remote_error_json)
                    else:
                        self.pk = save_res.pk

    def delete(self, using=None):
        if self.allow_delete:
            try:
                self._client.delete_object(self)
            except RemoteDatabaseError as rdbe:
                raise RemoteDatabaseError("Unable to delete {} object".format(self.__class__.__name__),
                                          remote_error_json=rdbe.remote_error_json)


class RemoteNSIModel(RemoteNSIModelBasic):
    class Meta(RemoteNSIModelBasic.Meta):
        abstract = True

    id = models.IntegerField(primary_key=True, blank=True)

    def __str__(self):
        return "{}".format(self.id)


class RemoteLdapProxyModel(RemoteNSIModel):
    class Meta(RemoteNSIModel.Meta):
        abstract = True

    _client = ldap_proxy
    objects = RemoteLdapProxyManager()


class RemoteForeignKey(models.ForeignKey):
    """
    Foreign key on RemoteModel
    """
    def __init__(self, *args, **kwargs):
        kwargs["db_constraint"] = False
        super(RemoteForeignKey, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "ForeignKey"


class RemoteOneToOneField(models.OneToOneField):
    """
    Foreign key on RemoteModel
    """
    def __init__(self, *args, **kwargs):
        kwargs["db_constraint"] = False
        super(RemoteOneToOneField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "OneToOneField"


def _get_list_queryset(self, name):
    lqs = getattr(self, "_" + name, None)
    if lqs is None:
        setattr(self, name, [])
        lqs = getattr(self, "_" + name)
    return lqs


def _set_list_queryset(self, name, model, value):
    setattr(self, "_" + name, FakeManager(model, value))


class RemoteManyToManyField(models.ManyToManyField):
    """
    Foreign key on RemoteModel
    """
    def __init__(self, *args, **kwargs):
        if kwargs.get("through") is None:
            kwargs["db_constraint"] = False
        self.remote_m2m_url = kwargs.pop("remote_m2m_url", None)
        self.remote_m2m_reverse_url = kwargs.pop("remote_m2m_reverse_url", None)
        self.remote_m2m_list = kwargs.pop("remote_m2m_list", False)
        self.remote_m2m_reverse_list = kwargs.pop("remote_m2m_reverse_list", False)
        super(RemoteManyToManyField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)
        if self.remote_m2m_list and issubclass(cls, RemoteNSIModelBasic):
            setattr(cls, self.name, property(
                lambda _self: _get_list_queryset(_self, name),
                lambda _self, value: _set_list_queryset(_self, name, self.rel.to, value)))

    def contribute_to_related_class(self, cls, related):
        super().contribute_to_related_class(cls, related)
        if not self.rel.is_hidden() and not related.model._meta.swapped:
            if self.remote_m2m_reverse_list and issubclass(cls, RemoteNSIModelBasic):
                setattr(cls, related.get_accessor_name(), property(
                    lambda _self: _get_list_queryset(_self, related.get_accessor_name()),
                    lambda _self, value: _set_list_queryset(_self, related.get_accessor_name(), self.model, value)))

    def get_internal_type(self):
        return "ManyToManyField"


class RemoteCoreDeleteMixin(models.Model):
    class Meta:
        abstract = True
    objects = RemoteCoreManager()


class RemoteCoreResultModel(models.Model, SerializableModel):
    TK_DATA = "DATA"
    TK_DICTIONARY = "DICTIONARY"
    TK_FINANCE = "FINANCE"

    TYPE_KINDS = (
        (TK_DATA, TK_DATA),
        (TK_DICTIONARY, TK_DICTIONARY),
        (TK_FINANCE, TK_FINANCE)
    )

    VS_NEVER = "NEVER"
    VS_APPROVED = "APPROVED"
    VS_DECLINED = "DECLINED"
    VS_CHANGED = "CHANGED"

    VERIFICATION_STATUSES = (
        (VS_NEVER, VS_NEVER),
        (VS_APPROVED, VS_APPROVED),
        (VS_DECLINED, VS_DECLINED),
        (VS_CHANGED, VS_CHANGED)
    )

    _client = core

    primary_key = models.AutoField(primary_key=True)
    remote_id = models.IntegerField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    validity_from = models.DateTimeField(blank=True, null=True)
    validity_to = models.DateTimeField(blank=True, null=True)
    activity_from = models.DateTimeField(blank=True, null=True)
    activity_to = models.DateTimeField(blank=True, null=True)
    internal_id = models.CharField(max_length=64, blank=True, null=True)
    external_id = models.CharField(max_length=64, blank=True, null=True)
    parents = models.ManyToManyField("RemoteCoreResultModel", related_name="children")
    result_type = RemoteForeignKey("main_remote.CoreResultType")
    type_kind = models.CharField(choices=TYPE_KINDS, max_length=64)
    verification_status = models.CharField(choices=VERIFICATION_STATUSES, max_length=64, default=VS_NEVER)
    verification_comment = models.CharField(max_length=1024, blank=True, null=True)
    core_synchronized = models.BooleanField(default=False)

    basic_serialize_model = {
        "id": "remote_id",
        "version": "version",
        "validity": {
            "from": "validity_from",
            "to": "validity_to"
        },
        "activity": {
            "from": "activity_from",
            "to": "activity_to"
        },
        "internalId": "internal_id",
        "externalId": "external_id",
        "owners": [
            "owners"
        ],
        "parentResults": [
            {
                "internalId": "parents.internal_id",
                "externalId": "parents.external_id"
            }
        ],
        "fundSources": [
            "fundings"
        ],
        "type": {
            "name": "result_type"
        },
        "verificationStatus": "verification_status",
        "verificationComment": "verification_comment"
    }

    verify_model = {
        "id": "remote_id",
        "version": "version",
        "internalId": "internal_id",
        "externalId": "external_id",
        "verificationStatus": "verification_status",
        "verificationComment": "verification_comment"
    }

    JSON_FIELD_NAME = "json"
    subclasses_result_types = {}

    def get_as_subclass(self):
        model = self.subclasses_result_types.get(self.result_type_id)
        if model is not None:
            return getattr(self, model.__name__.lower())
        else:
            return None

    custom_fieldtype_serializers = dict(RemoteModel.custom_fieldtype_serializers)
    custom_fieldtype_serializers.update({
        models.DateTimeField: DateTimeSerializer,
        models.DateField: DateIntSerializer,
        models.DecimalField: DecimalSerializer
    })

    @classmethod
    def get_serializer(cls):
        return CoreResultModelSerializer(cls)

    _reversed_serialize_model = None
    reverse_serialize_ignored_fields = {}
    custom_reverse_serialize = {}

    @classmethod
    def _remove_id_from_name(cls, name):
        if name.endswith("_id"):
            new_name = name[:-3]
            try:
                field_type = cls._meta.get_field(new_name)
            except FieldDoesNotExist:
                pass
            else:
                if isinstance(field_type, models.ForeignKey):
                    name = new_name
        return name

    @classmethod
    def _reverse_serialize_model(cls, model, ignored, prefix=()):
        result = {}
        for r, l in model.items():
            ign = ignored.get(r, {})
            if r in ignored:
                if ign is None:
                    continue
            if isinstance(l, str):
                result[cls._remove_id_from_name(l)] = prefix + (r,)
            elif isinstance(l, dict):
                result.update(cls._reverse_serialize_model(l, ign, prefix + (r,)))
        return result

    @classmethod
    def _calculate_reversed_serialize_model(cls):
        serialize_model = cls.basic_serialize_model
        serialize_model[cls.JSON_FIELD_NAME] = cls.serialize_model
        serialize_model = cls._convert_model_for_query(serialize_model)
        ignored = {
            cls.JSON_FIELD_NAME: cls.reverse_serialize_ignored_fields
        }
        cls._reversed_serialize_model = cls._reverse_serialize_model(serialize_model, ignored)
        cls._reversed_serialize_model.update(cls.custom_reverse_serialize)

    @classmethod
    def get_reversed_serialize_field(cls, field):
        if not field:
            return None
        return cls._reversed_serialize_model.get(field)

    @property
    def owners(self):
        return []

    def save(self, drop_sync=True, **kwargs):
        if drop_sync:
            self.core_synchronized = False
        super().save(**kwargs)

    def post_to_core(self):
        try:
            self._client.post_json_result(self)
        except RemoteDatabaseError as rdbe:
            raise RemoteDatabaseError("Unable to post {} object to core".format(self.__class__.__name__),
                                      remote_error_json=rdbe.remote_error_json)
        else:
            self.core_synchronized = True
            self.save(drop_sync=False)

    def verify(self, status=VS_APPROVED):
        try:
            self.verification_status = status
            self._client.verify_json_result(self)
        except RemoteDatabaseError as rdbe:
            raise RemoteDatabaseError("Unable to verify {} object in core".format(self.__class__.__name__),
                                      remote_error_json=rdbe.remote_error_json)
        else:
            self.save(drop_sync=False)

    def local_delete(self, using=None):
        super().delete(using)

    def delete(self, using=None):
        try:
            self.delete_from_core()
        except RemoteDatabaseError as e:
            if e.code != RemoteDatabaseError.ENTITY_NOT_FOUND:
                raise e
        super().delete(using)

    def delete_from_core(self):
        if self.remote_id is None:
            return
        try:
            self._client.delete_json_result(self)
        except RemoteDatabaseError as rdbe:
            raise RemoteDatabaseError("Unable to delete {} object in core".format(self.__class__.__name__),
                                      remote_error_json=rdbe.remote_error_json)




