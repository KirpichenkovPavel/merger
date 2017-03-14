from datetime import datetime
from django.db import models
from django.db.backends.utils import typecast_date
import time
import decimal

class DateTimeSerializer:
    @staticmethod
    def serialize(value):
        return int(value.timestamp()) * 1000 if value is not None else None

    @staticmethod
    def deserialize(value):
        return datetime.fromtimestamp(value / 1000) if value is not None else None


class DateIntSerializer:
    @staticmethod
    def serialize(value):
        return int(time.mktime(value.timetuple())) * 1000 if value is not None else None

    @staticmethod
    def deserialize(value):
        return datetime.fromtimestamp(value / 1000).date() if value is not None else None


class DateStringSerializer:
    @staticmethod
    def serialize(value):
        return str(value) if value is not None else None

    @staticmethod
    def deserialize(value):
        return typecast_date(value) if value is not None else None


class DecimalSerializer:
    @staticmethod
    def serialize(value):
        return float(value) if value is not None else None

    @staticmethod
    def deserialize(value):
        return decimal.Decimal(value) if value is not None else None


class NoneEmptyStringSerializer:
    @staticmethod
    def serialize(value):
        return value if value != "" else None

    @staticmethod
    def deserialize(value):
        return value if value is not None else ""


class DefaultModelSerializer:
    def __init__(self, model):
        self.model = model

    def _default_serialize_convertion(self, field_type, value):
        fieldtype_serializer = self.model.custom_fieldtype_serializers.get(field_type)
        if fieldtype_serializer is not None:
            return fieldtype_serializer.serialize(value)
        else:
            return value

    def _default_deserialize_convertion(self, field_type, value):
        fieldtype_serializer = self.model.custom_fieldtype_serializers.get(field_type)
        if fieldtype_serializer is not None:
            return fieldtype_serializer.deserialize(value)
        else:
            return value

    def _get_lname_and_serializer(self, local):
        if isinstance(local, tuple):
            lname = local[0]
            serializer = local[1] if len(local) > 1 else None
        else:
            lname = local
            serializer = None
        return lname, serializer

    def _get_field_and_model_by_name(self, name):
        names = name.split(".")
        model = self.model
        for field_name in names:
            field, m, direct, m2m = model._meta.get_field_by_name(field_name)
            f = field.field if m2m and not direct else field
            model = f.rel.to if hasattr(f, "rel") and f.rel is not None and not m2m else f.model
        return field, model

    def _get_field_by_name(self, name):
        return self._get_field_and_model_by_name(name)[0]

    def _get_linked_model_by_name(self, name):
        return self._get_field_and_model_by_name(name)[1]

    def _get_field_value_by_name(self, obj, name):
        names = name.split(".")
        for field_name in names:
            obj = getattr(obj, field_name)
        return obj

    def _serialize_item(self, obj, lname, serializer):
        if serializer is None:
            f = self._get_field_by_name(lname)
            field_type = type(f)
            if isinstance(f, models.ForeignKey):
                lname += "_id"
                field_type = type(f.related_field)
            local_field = self._get_field_value_by_name(obj, lname)
            return self._default_serialize_convertion(field_type, local_field)
        else:
            if isinstance(lname, (list, tuple)):
                local_field = [self._get_field_value_by_name(obj, name) for name in lname]
            else:
                local_field = self._get_field_value_by_name(obj, lname)
            return serializer.serialize(local_field)

    def serialize_by_json_dict(self, obj, json_dict):
        if obj is None:
            return None
        result = {}
        for remote, local in json_dict.items():
            if isinstance(local, dict):
                result[remote] = self.serialize_by_json_dict(obj, local)
            elif isinstance(local, list):
                item = local[0]
                if isinstance(item, dict):
                    fname = {(self._get_lname_and_serializer(v)[0]).split(".")[0] for k, v in item.items()}.pop()
                    nested_serializer = self._get_linked_model_by_name(fname).get_serializer()
                    nested_serialize_model = {}
                    for k, v in item.items():
                        lname, ser = self._get_lname_and_serializer(v)
                        lname = lname.split(".", 1)[1]
                        nested_serialize_model[k] = (lname, ser)
                    result[remote] = [nested_serializer.serialize_by_json_dict(it, nested_serialize_model)
                                      for it in getattr(obj, fname).all()]
                else:
                    field_list = getattr(obj, item)
                    if hasattr(field_list, "all"):
                        field_list = field_list.all()
                    result[remote] = [it.serialize() for it in field_list]
            else:
                result[remote] = self._serialize_item(obj, *self._get_lname_and_serializer(local))
        return result

    # lists and related models in schema are not supported
    def deserialize_by_json_dict(self, json_data, obj, json_dict):
        if json_data is None:
            return None
        for remote, local in json_dict.items():
            if isinstance(local, dict):
                self.deserialize_by_json_dict(json_data.get(remote), obj, local)
            else:
                lname, serializer = self._get_lname_and_serializer(local)
                remote_field = json_data.get(remote)
                if serializer is None:
                    f = self.model._meta.get_field(lname)
                    field_type = type(f)
                    if isinstance(f, models.ForeignKey):
                        lname += "_id"
                        field_type = type(f.related_field)
                    local_field = self._default_deserialize_convertion(field_type, remote_field)
                    setattr(obj, lname, local_field)
                else:
                    local_field = serializer.deserialize(remote_field)
                    if isinstance(lname, (list, tuple)):
                        for name, val in zip(lname, local_field):
                            setattr(obj, name, val)
                    else:
                        setattr(obj, lname, local_field)
        return obj

    def serialize(self, obj):
        return self.serialize_by_json_dict(obj, self.model.serialize_model)

    # lists and related models in schema are not supported
    def deserialize(self, json_data, from_database=True):
        result = self.deserialize_by_json_dict(json_data, self.model(), self.model.serialize_model)
        result._state.adding = not from_database
        return result


class CoreResultModelSerializer(DefaultModelSerializer):
    def serialize(self, obj):
        serialize_model = self.model.basic_serialize_model
        serialize_model[self.model.JSON_FIELD_NAME] = self.model.serialize_model
        return self.serialize_by_json_dict(obj, serialize_model)

    # lists and related models in schema are not supported
    def deserialize(self, json_data, from_database=True):
        serialize_model = self.model.basic_serialize_model
        serialize_model[self.model.JSON_FIELD_NAME] = self.model.serialize_model
        result = self.deserialize_by_json_dict(json_data, self.model(), serialize_model)
        result._state.adding = not from_database
        return result


class ListSerializer:
    def __init__(self, model):
        self.model = model

    def serialize(self, local_field):
        return [self.model.get_serializer().serialize(obj) for obj in local_field.all()]

    def deserialize(self, remote_field):
        return [self.model.get_serializer().deserialize(obj) for obj in remote_field]

    @staticmethod
    def get_model_for_query(local_field_name):
        return {"id": local_field_name}


class IdOrNoneSerializer:
    def __init__(self, model=None):
        self.model = model

    def serialize(self, local_field):
        return {"id": local_field} if local_field is not None else None

    def deserialize(self, remote_field):
        return remote_field["id"] if remote_field is not None else None

    @staticmethod
    def get_model_for_query(local_field_name):
        return {"id": local_field_name[:-3]}


class IdListSerializer:
    def __init__(self, model):
        self.model = model

    def serialize(self, local_field):
        if hasattr(local_field, "all"):
            thr = local_field.through
            src = local_field.source_field_name + "_id"
            tgt = local_field.target_field_name + "_id"
            return list(thr.objects.filter(**{src: local_field.related_val[0]}).values_list(tgt, flat=True))
        else:
            return [t.id for t in local_field]

    def deserialize(self, remote_field):
        return [self.model.objects.get(id=id) for id in remote_field]


class PropertySerializer:
    @staticmethod
    def serialize(local_field):
        return local_field


class StringSerializer:
    @staticmethod
    def serialize(local_field):
        if local_field is not None:
            return str(local_field)
        return None
