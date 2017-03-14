import asyncio
import base64
import json
import logging

import aiohttp
import requests
from aiohttp.helpers import BasicAuth
from crequest.middleware import CrequestMiddleware
from django.conf import settings
from requests.status_codes import codes

import main_remote
from django_remote_model.util.query_log import info, error
from django_remote_model.util.util import query_quote, invalidate_cache_for_model, get_cached_response, \
    cache_response, FakeResponse
from remote_impl.remote_database_exception import RemoteDatabaseError

logger = logging.getLogger('polyana_web')


class CoreImpl:
    def __init__(self, server_uri=settings.POLYANA_SERVER_URI, api_path=settings.POLYANA_API_PATH):
        self.__server_uri = server_uri
        self.__api_path = api_path

        self.__polyana_url = self.__server_uri + self.__api_path
        self.__settings_url = self.__polyana_url + "/private/settings"
        self.__result_type_url = self.__polyana_url + "/jsonresulttype"
        self.__result_url = self.__polyana_url + "/jsonresult"
        self.__data_url = self.__result_url + "/data"
        self.__finance_url = self.__result_url + "/finance"
        self.__data_count_url = self.__data_url + "/count"
        self.__data_agg_url = self.__data_url + "/aggregate"

    def __json_or_none(self, r):
        try:
            return r.json()
        except ValueError:
            return None

    def __get_auth(self):
        request = CrequestMiddleware.get_request()
        if request is not None and hasattr(request, "user") and request.user is not None and\
                not request.user.is_anonymous():
            return request.user.username, request.session.get("password")
        else:
            return None

    def __get_role(self):
        request = CrequestMiddleware.get_request()
        if request is not None and hasattr(request, "user") and request.user is not None and\
                not request.user.is_anonymous():
            return request.session.get("active_role")
        else:
            return None

    def prepare_request_kwargs(self, kwargs):
        auth = self.__get_auth()
        if auth is not None:
            kwargs["auth"] = auth
        headers = kwargs.get("headers", {})
        role = self.__get_role()
        if role is not None:
            headers["X-User-Active-Role"] = str(base64.b64encode(bytes(role, 'UTF-8')), 'utf-8')
        kwargs["headers"] = headers
        return kwargs

    def auth_get(self, url, cache_timeout=None, model=None, **kwargs):
        response = get_cached_response(url, model=model)
        if response is not None:
            return response
        kwargs = self.prepare_request_kwargs(kwargs)
        response = requests.get(url, **kwargs)
        if response.status_code == codes.ok:
            cache_response(url, response, timeout=cache_timeout, model=model)
        return response

    @asyncio.coroutine
    def auth_get_async(self, url, cache_timeout=None, model=None, **kwargs):
        response = get_cached_response(url, model=model)
        if response is not None:
            return response

        kwargs = self.prepare_request_kwargs(kwargs)
        auth = kwargs["auth"]
        if isinstance(auth, tuple):
            kwargs["auth"] = BasicAuth(login=auth[0], password=auth[1])

        with aiohttp.ClientSession() as session:
            response = yield from session.get(url, **kwargs)
            js = yield from response.json()
            response = FakeResponse(js, status_code=response.status)

        if response.status_code == codes.ok:
            cache_response(url, response, timeout=cache_timeout, model=model)
        return response

    def auth_post(self, url, data, model=None, **kwargs):
        headers = kwargs.get("headers", {})
        headers["content-type"] = "application/json; charset=utf8"
        kwargs["headers"] = headers
        kwargs = self.prepare_request_kwargs(kwargs)
        if model is not None:
            invalidate_cache_for_model(model)
        return requests.post(url, json.dumps(data), **kwargs)

    def auth_delete(self, url, model=None, **kwargs):
        kwargs = self.prepare_request_kwargs(kwargs)
        if model is not None:
            invalidate_cache_for_model(model)
        return requests.delete(url, **kwargs)

    def get_page_size(self):
        r = self.auth_get(self.__settings_url)
        if r.status_code == codes.ok:
            paging = r.json()["paging"]
            return paging
        else:
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    # TODO remove this later
    def get_report_types(self):
        params = {
            "jsonResultType": "report"
        }
        params = ";".join(["{}={}".format(k,v) for k,v in params.items()])
        url = "{};{}".format(self.__data_url, params)
        r = self.auth_get(url, cache_timeout=0)
        if r.status_code == codes.ok:
            return self.__json_or_none(r)
        else:
            return None

    def get_json_result_types(self):
        r = self.auth_get(self.__result_type_url, model=main_remote.models.CoreResultType)
        if r.status_code == codes.ok:
            info("core.get_json_result_types", self.__result_type_url, r)
            return self.__json_or_none(r)
        else:
            error("core.get_json_result_types", self.__result_type_url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_json_result_type(self, name):
        _url = "{};name={}".format(self.__result_type_url, name)
        r = self.auth_get(_url, model=main_remote.models.CoreResultType)
        if r.status_code == codes.ok:
            info("core.get_json_result_type", _url, r)
            return self.__json_or_none(r)
        else:
            error("core.get_json_result_type", _url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))


    def post_json_result_type(self, result_type):
        _url = self.__result_type_url
        r = self.auth_post(_url, result_type, model=main_remote.models.CoreResultType)
        if r.status_code == codes.ok:
            info("core.post_json_result_type", _url, r, result_type)
            return self.__json_or_none(r)
        else:
            error("core.post_json_result_type", _url, r, result_type)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def delete_json_result_type(self, id, version, name):
        _url = "{};id={};version={};name={}".format(self.__result_type_url, id, version, name)
        r = self.auth_delete(_url, model=main_remote.models.CoreResultType)
        if r.status_code == codes.ok:
            info("core.delete_json_result_type", _url, r)
            return self.__json_or_none(r)
        else:
            error("core.delete_json_result_type", _url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def post_json_result(self, result, type, model):
        url = "{}/{}".format(self.__result_url, type)
        r = self.auth_post(url, result, model=model)
        if r.status_code == codes.ok:
            info("core.post_json_result", url, r, result)
            return self.__json_or_none(r)
        else:
            error("core.post_json_result", url, r, result)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def verify_json_result(self, result, type, model):
        url = "{}/{}/verify".format(self.__result_url, type)
        r = self.auth_post(url, result, model=model)
        if r.status_code == codes.ok:
            info("core.verify_json_result", url, r, result)
            return self.__json_or_none(r)
        else:
            error("core.verify_json_result", url, r, result)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def delete_json_result(self, type, id, version, internal_id, model):
        url = "{}/{};id={};version={};internalId={}".format(self.__result_url, type, id, version, internal_id)
        r = self.auth_delete(url, model=model)
        if r.status_code == codes.ok:
            info("core.delete_json_result", url, r)
            return self.__json_or_none(r)
        else:
            error("core.delete_json_result", url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def ensure_result_type(self, result_type):
        """ result_type object is main.models.documents.ResulType """
        r = self.auth_get(self.__result_type_url + ";name=" + result_type.name, model=main_remote.models.CoreResultType)
        if r.status_code != codes.ok:
            data = {"name": result_type.name, "schema": result_type.json}
            r2 = self.auth_post(self.__result_type_url, data, model=main_remote.models.CoreResultType)
            if r2.status_code != codes.ok:
                return False
        return True

    def prepare_query_params(self, result_type, permission, page=None, query=None, sort=None, desc=None,
                             parents=None, agg=None):
        params = [
            ("jsonResultType", result_type),
            ("permissionType", permission),
            ("brief", "true")
        ]
        if page is not None:
            params.append(("page",  page))
        if desc is not None:
            params.append(("sortDesc",  desc))
        if sort is not None:
            params.append(("sortBy", sort))
        if query is not None:
            q = "\"{}\"".format(query_quote(query))
            params.append(("q", q))
        if agg is not None:
            params.append(("agg", agg))
        if parents is not None:
            params += [("parentInternalIds", parent.internal_id) for parent in parents]
        return ";".join(["{}={}".format(k, v) for k, v in params])

    def get_allowed_results(self, result_type, permission, page=0, query=None, sort=None, desc=False, parents=None, model=None):
        params = self.prepare_query_params(result_type, permission, page, query, sort, desc, parents)
        url = "{};{}".format(self.__data_url, params)
        r = self.auth_get(url, model=model)
        if r.status_code == codes.ok:
            info("core.get_allowed_results", url, r, result_type)
            res = self.__json_or_none(r)
            return res
        else:
            error("core.get_allowed_results", url, r, result_type)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_allowed_results_count(self, result_type, permission, query=None, parents=None, model=None):
        params = self.prepare_query_params(result_type, permission, query=query, parents=parents)
        url = "{};{}".format(self.__data_count_url, params)
        r = self.auth_get(url, model=model)
        if r.status_code == codes.ok:
            info("core.get_allowed_results_count", url, r, result_type)
            return r.json()

        else:
            error("core.get_allowed_results_count", url, r, result_type)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    @asyncio.coroutine
    def get_allowed_results_count_async(self, result_type, permission, query=None, parents=None, model=None):
        params = self.prepare_query_params(result_type, permission, query=query, parents=parents)
        url = "{};{}".format(self.__data_count_url, params)
        r = yield from self.auth_get_async(url, model=model)
        if r.status_code == codes.ok:
            info("core.get_allowed_results_count", url, r, result_type)
            return r.json()

        else:
            error("core.get_allowed_results_count", url, r, result_type)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_allowed_results_agg(self, result_type, permission, agg, query=None, parents=None, model=None):
        params = self.prepare_query_params(result_type, permission, query=query, parents=parents, agg=agg)
        url = "{};{}".format(self.__data_agg_url, params)
        r = self.auth_get(url, model=model)
        if r.status_code == codes.ok:
            info("core.get_allowed_results_agg", url, r, result_type)
            result = r.json()
            if result == "NaN":
                result = None
            return result

        else:
            error("core.get_allowed_results_agg", url, r, result_type)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    @asyncio.coroutine
    def get_allowed_results_agg_async(self, result_type, permission, agg, query=None, parents=None, model=None):
        params = self.prepare_query_params(result_type, permission, query=query, parents=parents, agg=agg)
        url = "{};{}".format(self.__data_agg_url, params)
        r = yield from self.auth_get_async(url, model=model)
        if r.status_code == codes.ok:
            info("core.get_allowed_results_agg", url, r, result_type)
            result = r.json()
            if result == "NaN":
                result = None
            return result

        else:
            error("core.get_allowed_results_agg", url, r, result_type)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

core_impl = CoreImpl()
