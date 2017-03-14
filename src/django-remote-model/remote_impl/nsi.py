# coding=utf-8
import base64
import urllib

from django_remote_model.util.util import query_quote, get_cached_response, cache_response, \
    invalidate_cache_for_model
from crequest.middleware import CrequestMiddleware
from django_remote_model.util.query_log import info, error
import requests
from django.conf import settings
import json
from requests.status_codes import codes

import logging
import main_remote
import polyauth_remote
from remote_impl.remote_database_exception import RemoteDatabaseError

logger = logging.getLogger('polyana_web')


class NsiImpl:
    def __init__(self, server_uri=settings.NSI_SERVER_URI, api_path=settings.NSI_API_PATH):
        self.__server_uri = server_uri
        self.__api_path = api_path

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

    def __get_bp_auth(self):
        request = CrequestMiddleware.get_request()
        if request is not None and hasattr(request, "bp") and request.bp is not None:
            return requests.auth._basic_auth_str(request.bp.username, request.bp.password)
        else:
            return None

    def bp_authenticate(self, username, password):
        bp_auth_header = requests.auth._basic_auth_str(username, password)
        r = requests.get(self.__server_uri + self.__api_path + "/businessprocess/auth",
                         headers={"X-BP-Authorization": bp_auth_header})
        return r.status_code == codes.ok

    def prepare_request_kwargs(self, kwargs):
        auth = self.__get_auth()
        if auth is not None:
            kwargs["auth"] = auth
        headers = kwargs.get("headers", {})
        role = self.__get_role()
        if role is not None:
            headers["X-User-Active-Role"] = str(base64.b64encode(bytes(role, 'UTF-8')), 'utf-8')
        bp_auth = self.__get_bp_auth()
        if bp_auth is not None:
            headers["X-BP-Authorization"] = bp_auth
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

    def auth_post(self, url, data, model=None, **kwargs):
        kwargs = self.prepare_request_kwargs(kwargs)
        headers = kwargs.get("headers", {})
        headers["content-type"] = "application/json; charset=utf8"
        kwargs["headers"] = headers
        if model is not None:
            invalidate_cache_for_model(model)
        return requests.post(url, json.dumps(data), **kwargs)

    def auth_delete(self, url, model=None, **kwargs):
        kwargs = self.prepare_request_kwargs(kwargs)
        if model is not None:
            invalidate_cache_for_model(model)
        return requests.delete(url, **kwargs)

    def paternity_test(self, child, father):
        """
        Checks with NSI query if 'child' department is a sub-department of a 'father' department
        :param child: checked daughter department
        :param father: checked father department
        :return: true if 'child' is a sub-department of 'father', else otherwise
        """

        r = self.auth_get(self.__server_uri + self.__api_path +
                     "/division/" + str(father) +
                     "/child/" + str(child), model=main_remote.models.Division)

        if r.status_code == codes.ok:
            return r.json()["result"]
        else:
            return False

    def get_department_head(self, department):
        """
        Get head of department
        :param department: department id
        :return: json object Employee corresponds to head of department
        """
        r = self.auth_get(self.__server_uri + self.__api_path +
                          "/division/" + str(department) + "/head", model=main_remote.models.Division)
        if r.status_code == codes.ok:
            return self.__json_or_none(r)
        else:
            return None

    def get_division_children(self, division):
        """
        Get head of department
        :param division: division id
        :return: json object with child divisions list
        """
        r = self.auth_get(self.__server_uri + self.__api_path + "/division/" + str(division) + "/children",
                          model=main_remote.models.Division)
        if r.status_code == codes.ok:
            return self.__json_or_none(r)
        else:
            return None

    def get_deep_registry_permissions_for_employee(self, employee):
        """
        Gets a list of instances of LocalPermissionInst class with user permissions got from NSI
        Permissions are expanded with daughter departments permissions by NSI.
        :param user: user
        :return: list of user permissions
        """
        url = self.__server_uri + self.__api_path + "/employee/" + str(employee) + "/permission/full"
        r = self.auth_get(url, model=polyauth_remote.models.RegistryRemotePermissionInst)
        if r.status_code == codes.ok:
            res = self.__json_or_none(r)
            return res
        else:
            return None

    def get_page_size(self):
        _url = self.__server_uri + self.__api_path + "/private/settings"
        r = self.auth_get(_url)
        if r.status_code == codes.ok:
            info("nsi.get_page_size", _url, r)
            paging = r.json()["paging"]
            return paging
        else:
            error("nsi.get_page_size", _url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_object_by_id(self, url, id, model):
        _url = self.__server_uri + self.__api_path + url + "/" + urllib.parse.quote(str(id), safe="")
        r = self.auth_get(_url, model=model)
        if r.status_code == codes.ok:
            info("nsi.get_object_by_id", _url, r)
            res = self.__json_or_none(r)
            return res
        elif r.status_code == codes.not_found:
            info("nsi.get_object_by_id", _url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))
        else:
            error("nsi.get_object_by_id", _url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_objects(self, url, query=None, page=0, sort=None, desc=None, model=None):
        query_url = self.__server_uri + self.__api_path + url
        if query is not None:
            query_url += "/query2;q=\"{}\"".format(query_quote(query))
        elif sort is not None and desc is not None:
            query_url += "/query2;"
        query_url += ";page={}".format(page)
        if sort:
            query_url += ";sort={}".format(sort)
        if desc:
            query_url += ";desc={}".format(desc)
        r = self.auth_get(query_url, model=model)
        if r.status_code == codes.ok:
            info("nsi.get_objects", query_url, r)
            results = self.__json_or_none(r)
            return results
        else:
            error("nsi.get_objects", query_url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_objects_count(self, url, query=None, model=None):
        query_url = self.__server_uri + self.__api_path + url
        if query is not None:
            query_url += "/query2/count;q=\"{}\"".format(query_quote(query))
        else:
            query_url += "/count"
        r = self.auth_get(query_url, model=model)
        if r.status_code == codes.ok:
            info("nsi.get_objects_count", query_url, r)
            result = r.json()
            return result
        else:
            error("nsi.get_objects_count", query_url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_objects_agg(self, url, agg, query=None, model=None):
        query_url = self.__server_uri + self.__api_path + url + "/query2/aggregate"
        query_url += ";agg={}".format(agg)
        if query is not None:
            query_url += ";q=\"{}\"".format(query_quote(query))
        r = self.auth_get(query_url, model=model)
        if r.status_code == codes.ok:
            info("nsi.get_objects_agg", query_url, r)
            result = r.json()
            if result == "NaN":
                result = None
            return result
        else:
            error("nsi.get_objects_agg", query_url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_objects_m2m(self, url, id, related_url, page=0, model=None):
        _url = self.__server_uri + self.__api_path + url + "/" + str(id) + related_url + ";page={}"
        url = _url.format(page)
        r = self.auth_get(url, model=model)
        if r.status_code == codes.ok:
            info("nsi.get_objects_m2m", _url, r)
            res = self.__json_or_none(r)
            return res
        else:
            error("nsi.get_objects_m2m", _url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def create_object(self, url, obj, model):
        _url = self.__server_uri + self.__api_path + url + "/new"
        r = self.auth_post(_url, obj, model=model)
        if r.status_code == codes.ok:
            info("nsi.create_object", _url, r, obj)
            return self.__json_or_none(r)
        else:
            error("nsi.create_object", _url, r, obj)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def modify_object(self, url, obj, model):
        _url = self.__server_uri + self.__api_path + url + "/edit"
        r = self.auth_post(_url, obj, model=model)
        if r.status_code == codes.ok:
            info("nsi.modify_object", _url, r, obj)
            return self.__json_or_none(r)
        else:
            error("nsi.modify_object", _url, r, obj)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def delete_object(self, url, id, model):
        _url = self.__server_uri + self.__api_path + url + "/" + urllib.parse.quote(str(id), safe="")
        r = self.auth_delete(_url, model=model)
        if r.status_code == codes.ok:
            info("nsi.delete_object", _url, r)
            return self.__json_or_none(r)
        else:
            error("nsi.delete_object", _url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_employee_appointments_by_date(self, employee, date):
        url = "{}{}/employee/{}/appointment/{}".format(self.__server_uri, self.__api_path, employee, date)
        r = self.auth_get(url, model=main_remote.models.Appointment)
        if r.status_code == codes.ok:
            info("nsi.get_employee_appointments_by_date", url, r)
            res = self.__json_or_none(r)
            return res
        else:
            error("nsi.get_employee_appointments_by_date", url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_current_user_nsi_permissions_with_role(self, bp_id=None):
        if bp_id is not None:
            url = "{}{}/employee/me/businessprocess/{}/permission".format(self.__server_uri, self.__api_path, bp_id)
        else:
            url = "{}{}/employee/me/businessprocess/permission".format(self.__server_uri, self.__api_path)
        r = self.auth_get(url, cache_timeout=0)
        if r.status_code == codes.ok:
            info("nsi.get_current_user_nsi_permissions_with_role", url, r)
            res = self.__json_or_none(r)
            return res
        else:
            error("nsi.get_current_user_nsi_permissions_with_role", url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_nsi_permissions_with_role(self, employee_id, bp_id):
        url = "{}{}/employee/{}/businessprocess/{}/permission".format(
            self.__server_uri,
            self.__api_path,
            employee_id,
            bp_id
        )
        r = self.auth_get(url, cache_timeout=0)
        if r.status_code == codes.ok:
            info("nsi.get_current_user_nsi_permissions_with_role", url, r)
            res = self.__json_or_none(r)
            return res
        else:
            error("nsi.get_current_user_nsi_permissions_with_role", url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

    def get_core_permissions_with_role(self, employee_id):
        url = "{}{}/employee/{}/permission".format(
            self.__server_uri,
            self.__api_path,
            employee_id
        )
        r = self.auth_get(url, cache_timeout=0)
        if r.status_code == codes.ok:
            info("nsi.get_current_user_nsi_permissions_with_role", url, r)
            res = self.__json_or_none(r)
            return res
        else:
            error("nsi.get_current_user_nsi_permissions_with_role", url, r)
            raise RemoteDatabaseError(remote_error_json=self.__json_or_none(r))

nsi_impl = NsiImpl()
