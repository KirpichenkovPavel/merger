import asyncio
import json
import logging
from django.db.models.query_utils import Q
from remote_impl.remote_database_exception import RemoteDatabaseError

import requests
from django.conf import settings
from django_remote_model.serializers import DateTimeSerializer
from django_remote_model.util.util import core_get_query_from_Q
from remote_impl.core import CoreImpl

logger = logging.getLogger('polyana_web')

class Core:
    def __init__(self, server_uri=settings.POLYANA_SERVER_URI, api_path=settings.POLYANA_API_PATH):
        self.__server_uri = server_uri
        self.__api_path = api_path

        self.__impl = CoreImpl(server_uri, api_path)

    def get_result_types(self, model):
        result_json = self.__impl.get_json_result_types()
        yield from (model.get_serializer().deserialize(r) for r in result_json)

    def get_result_type(self, model, name):
        try:
            result_json = self.__impl.get_json_result_type(name)
        except RemoteDatabaseError:
            raise model.DoesNotExist("{} with name={} does not exist.".format(model._meta.object_name, name))
        return model.get_serializer().deserialize(result_json)

    def post_result_type(self, result_type):
        serializer = result_type.get_serializer()
        result_json = self.__impl.post_json_result_type(serializer.serialize(result_type))
        return serializer.deserialize(result_json)

    def delete_result_type(self, result_type):
        return self.__impl.delete_json_result_type(result_type.id, result_type.version, result_type.name)

    def post_json_result(self, result):
        serializer = result.get_serializer()
        result_json = self.__impl.post_json_result(serializer.serialize(result), result.type_kind, result._meta.model)
        result.remote_id = result_json["id"]
        result.version = result_json["version"]
        result.internal_id = result_json["internalId"]
        result.verification_status = result_json["verificationStatus"]
        result.validity_from = DateTimeSerializer.deserialize(result_json["validity"]["from"])
        result.validity_to = DateTimeSerializer.deserialize(result_json["validity"]["to"])
        return result

    def bulk_post_json_results(self, results):
        if not results:
            return None
        serializer = results[0].get_serializer()
        type_kind = results[0].type_kind
        model = results[0]._meta.model
        results_serialized = [serializer.serialize(result) for result in results]
        result_json = self.__impl.post_json_result(results_serialized, type_kind, model)
        for result, json in zip(results, result_json):
            result.remote_id = json["id"]
            result.version = json["version"]
            result.internal_id = json["internalId"]
            result.verification_status = json["verificationStatus"]
            result.validity_from = DateTimeSerializer.deserialize(result_json["validity"]["from"])
            result.validity_to = DateTimeSerializer.deserialize(result_json["validity"]["to"])
        return results

    def verify_json_result(self, result):
        serializer = result.get_serializer()
        result_json = self.__impl.verify_json_result(serializer.serialize_by_json_dict(result, result.verify_model),
                                              result.type_kind,
                                              result._meta.model)
        result.remote_id = result_json["id"]
        result.version = result_json["version"]
        result.internal_id = result_json["internalId"]
        result.verification_status = result_json["verificationStatus"]
        result.validity_from = DateTimeSerializer.deserialize(result_json["validity"]["from"])
        result.validity_to = DateTimeSerializer.deserialize(result_json["validity"]["to"])
        return result


    def delete_json_result(self, result):
        return self.__impl.delete_json_result(result.type_kind,
                                       result.remote_id,
                                       result.version,
                                       result.internal_id,
                                       result._meta.model)

    # TODO: why not in impl???
    def post_modified_json_result(self, result, id, version, username, password):
        json_result = json.dumps(result)
        r = requests.post(self.__server_uri + self.__api_path + "/jsonresult/data", json_result,
                          headers={"content-type": "application/json; charset=utf8"}, auth=(username, password))
        return r.status_code

    def get_allowed_objects(self, model, permission, limit_low=None, limit_high=None,
                            query=None, sort=None, desc=False, parents=None):
        page_size = self.__impl.get_page_size()
        page = limit_low // page_size if limit_low is not None else 0
        part_start = limit_low % page_size if limit_low is not None else 0
        part_end = limit_high - page * page_size if limit_high is not None else page_size
        result_type = model.doc_type().metadata.doctypecoremetadata.result_type_id
        query = core_get_query_from_Q(model, query)
        while True:
            try:
                objs = self.__impl.get_allowed_results(result_type, permission, page, query=query,
                                                sort=sort, desc=desc, parents=parents, model=model)
            except RemoteDatabaseError:
                break
            result_part = objs[part_start:part_end]
            if len(result_part) == 0:
                break
            for res in result_part:
                # ToDo: think about this shit!!!
                try:
                    yield model.objects.get(internal_id=res["internalId"])
                except model.DoesNotExist:
                    pass
            if len(objs) < page_size:
                break
            page += 1
            part_start = 0
            if limit_high is not None:
                part_end -= page_size
                if part_end <= 0:
                    break

    def get_allowed_objects_count(self, model, permission, query=None, parents=None):
        query = core_get_query_from_Q(model, query)
        result_type = model.doc_type().metadata.doctypecoremetadata.result_type_id
        count = self.__impl.get_allowed_results_count(result_type, permission, query=query, parents=parents, model=model)
        return count

    @asyncio.coroutine
    def get_allowed_objects_count_async(self, model, permission, query=None, parents=None):
        query = core_get_query_from_Q(model, query)
        result_type = model.doc_type().metadata.doctypecoremetadata.result_type_id
        result = yield from self.__impl.get_allowed_results_count_async(result_type, permission, query=query, parents=parents,
                                                      model=model)
        return result

    def get_allowed_objects_agg(self, model, permission, query, agg_type, agg_field, parents=None):
        query = core_get_query_from_Q(model, query)
        field = model.get_reversed_serialize_field(agg_field)
        agg = "{}({})".format(agg_type, ".".join(field))
        result_type = model.doc_type().metadata.doctypecoremetadata.result_type_id
        return self.__impl.get_allowed_results_agg(result_type, permission, agg, query=query, parents=parents, model=model)

    @asyncio.coroutine
    def get_allowed_objects_agg_async(self, model, permission, query, agg_type, agg_field, parents=None):
        query = core_get_query_from_Q(model, query)
        field = model.get_reversed_serialize_field(agg_field)
        agg = "{}({})".format(agg_type, ".".join(field))
        result_type = model.doc_type().metadata.doctypecoremetadata.result_type_id
        result = yield from self.__impl.get_allowed_results_agg_async(result_type, permission, agg, query=query, parents=parents,
                                                   model=model)
        return result

core = Core()
