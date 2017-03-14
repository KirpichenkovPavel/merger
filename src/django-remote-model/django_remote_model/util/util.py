import collections
from datetime import datetime, date, time
import hashlib
import logging
from urllib.parse import quote

from crequest.middleware import CrequestMiddleware
from django.db.models.constants import LOOKUP_SEP
from django.db.models.loading import get_model
from django.db.models.query_utils import Q
from django.http.request import HttpRequest
from django.conf import settings
from django.core.cache import cache
from django_remote_model.serializers import DateTimeSerializer, DateIntSerializer
from requests.status_codes import codes

logger = logging.getLogger('polyana_web')
import traceback


def try_parse_int(arg):
    """
    Tries to parse an int from arg (string in most cases).
    If succeeded the parsed integer value is returned,
    otherwise returned arg itself.
    :param arg: argument
    :return: parsed int or arg itself
    """
    try:
        result = int(arg)
    except ValueError:
        return arg
    else:
        return result


def changed_forms(formset):
    """
    Construct list of changed forms in formset
    """
    form_list = list()
    for form in formset:
        if form.has_changed():
            form_list.append(form)
    return form_list


def datetime_to_string(val):
    if isinstance(val, date):
        return val.strftime(datetime_to_string.DATE_FORMAT)
    elif isinstance(val, time):
        return val.strftime(datetime_to_string.TIME_FORMAT)
    elif isinstance(val, datetime):
        return val.strftime(
            "%s %s" % (datetime_to_string.DATE_FORMAT, datetime_to_string.TIME_FORMAT))


def create_request():
    request = HttpRequest()
    request.session = dict()
    return request


def shell_authenticate(username, password):
    """
    Hack to make work remote model from shell.
    Call it before using remote model in shell
    """
    request = CrequestMiddleware.get_request()
    if request is None:
        request = create_request()
    if username and password:
        PolyUser = get_model("polyauthentication", "PolyUser")
        fake_user = PolyUser(username=username)
        request.user = fake_user
        request.session["password"] = password
    CrequestMiddleware.set_request(request)


def add_bp_credentials(request, bp_name, bp_password):
    class FakeBP:
        def __init__(self, username, password):
            self.username = username
            self.password = password
    if request is None:
        request = create_request()
    request.bp = FakeBP(bp_name, bp_password)
    return request


datetime_to_string.DATE_FORMAT = "%Y-%m-%d"
datetime_to_string.TIME_FORMAT = "%H:%M:%S"


def today_timestamp_milliseconds():
    today = date.today()
    return DateIntSerializer.serialize(today)


def __get_str_cache_key(s):
    def cache_hash(s):
        return hashlib.sha256(s.encode()).hexdigest()
    request = CrequestMiddleware.get_request()
    params = [s]
    if request is not None and hasattr(request, "user") and request.user is not None and\
            not request.user.is_anonymous():
        params.append(request.user.username)
    if request is not None and hasattr(request, "session") and request.session is not None:
        role = request.session.get("active_role")
        if role is not None:
            params.append(role)
    result = "_".join(params)
    return cache_hash(result)


def __get_base_model(model):
    while model._meta.proxy:
        model = model._meta.proxy_for_model
    return model


def __get_model_cache_version(model):
    key = "{}_cache_version".format(__get_base_model(model).__name__)
    if key not in cache:
        cache.add(key, 1, timeout=None)
    return cache.get(key)


class FakeResponse:

    def __init__(self, json, status_code=codes.ok):
        self._json = json
        self._status_code = status_code

    @property
    def status_code(self):
        return self._status_code

    def json(self):
        if self._json is None:
            raise ValueError
        else:
            return self._json


def invalidate_cache_for_model(model):
    model = __get_base_model(model)
    try:
        key = "{}_cache_version".format(model.__name__)
        if key not in cache:
            cache.add(key, 1, timeout=None)
        else:
            cache.incr(key)
    except:
        tb = traceback.format_exc()
        logger.error("Error while increment model {} cache version:\n{}".format(model, str(tb)))


def get_cached_response(url, model=None):
    try:
        key = __get_str_cache_key(url)
        if model is None:
            response_json = cache.get(key)
        else:
            response_json = cache.get(key, version=__get_model_cache_version(model))
        if response_json is not None:
            logger.info("get cached response for URL: {}".format(url))
            return FakeResponse(response_json)
        else:
            return None
    except:
        tb = traceback.format_exc()
        logger.error("Error while getting response for {} from cache:\n{}".format(url, str(tb)))
    return None


def cache_response(url, response, timeout=None, model=None):
    try:
        response_json = response.json()
        key = __get_str_cache_key(url)
        kwargs = {}
        if timeout is not None:
            kwargs["timeout"] = timeout
        if model is not None:
            kwargs["version"] = __get_model_cache_version(model)
        return cache.set(key, response_json, **kwargs)
    # if response has no JSON don't set None to cache
    except ValueError:
        pass
    except:
        tb = traceback.format_exc()
        logger.error("Error while setting key {}={} into cache:\n{}".format(url, response_json, str(tb)))
    return None


# def __try_delete_cache(key, model=None):
#     try:
#         if model is None:
#             return cache.delete(key)
#         else:
#             return cache.delete(key, version=__get_model_cache_version(model))
#     except:
#         tb = traceback.format_exc()
#         logger.error("Error while deleting key {} from cache:\n{}".format(key, str(tb)))
#     return None


core_query_op = {
    "exact": "{field} == \'{val}\'",
    "exactnot": " {field} != \'{val}\'",
    "lt": "{field} < \'{val}\'",
    "gt": "{field} > \'{val}\'",
    "lte": "{field} <= \'{val}\'",
    "gte": "{field} >= \'{val}\'",
    "contains": "{field} CONTAINS \'{val}\'",
    "startswith": "{field} LIKE \"{unquoted_val}%\"",
    "endswith": "{field} LIKE \"%{unquoted_val}\"",
    "like": "{field} LIKE \"%{unquoted_val}%\"",
    "ilike": "{field} ILIKE \"%{unquoted_val}%\"",
    "intersects": "{field} INTERSECTS \'{val}\'",
    "in": "{field} IN \'{val}\'"
}

nsi_query_op = {
    "exact": "{field} == {val}",
    "iexact": "{field} ILIKE {val}",
    "exactnot": " {field} != {val}",
    "lt": "{field} < {val}",
    "gt": "{field} > {val}",
    "lte": "{field} <= {val}",
    "gte": "{field} >= {val}",
    "contains": "{field} LIKE \"%{unquoted_val}%\"",
    "startswith": "{field} LIKE \"{unquoted_val}%\"",
    "endswith": "{field} LIKE \"%{unquoted_val}\"",
    "icontains": "{field} ILIKE \"%{unquoted_val}%\"",
    "istartswith": "{field} ILIKE \"{unquoted_val}%\"",
    "iendswith": "{field} ILIKE \"%{unquoted_val}\"",
    "in": "{field} IN \'{val}\'",
    "any": "{field} CONTAINS \'{val}\'",
}


def format_query_value(value):
    if isinstance(value, (str, float)):
        value = "\"{}\"".format(value)
    elif isinstance(value, bool):
        value = "\"true\"" if value else "\"false\""
    elif isinstance(value, datetime):
        value = DateTimeSerializer.serialize(value)
    elif isinstance(value, date):
        value = DateIntSerializer.serialize(value)
    elif value is None:
        value = "null"
    elif isinstance(value, collections.Iterable):
        value = "[{}]".format(",".join(str(format_query_value(item)) for item in value))
    return value

'''
  Makes core filter string from Django Q object
'''
def core_get_query_from_Q(model, q):
    if not q:
        return None
    query = []
    for child in q.children:
        if type(child) == Q:
            qpart = core_get_query_from_Q(model, child)
            if qpart is not None:
                query.append(qpart)
            continue
        k, v = child
        kk = k.split(LOOKUP_SEP)
        field = kk[0]
        filter = kk[1] if len(kk) > 1 else "exact"
        rfield = model.get_reversed_serialize_field(field)
        op = core_query_op.get(filter)
        if rfield is not None and op is not None:
            rfield = ".".join(rfield)
            unquoted_val = v
            if isinstance(unquoted_val, str):
                unquoted_val = unquoted_val.replace("\"", "\\\"")
            v = format_query_value(v)
            query.append(op.format(field=rfield, val=v, unquoted_val=unquoted_val))
        elif rfield is None:
            logger.warning("Wrong core filter {}={}, unknown field name {}".format(k, v, field))
        else:
            logger.warning("Wrong core filter {}={}, unknown filter {}".format(k, v, filter))
    return "(" + " {} ".format(q.connector).join(query) + ")" if query else None


def nsi_get_query_from_Q(model, q):
    if not q:
        return None
    query = []
    for child in q.children:
        if type(child) == Q:
            qpart = nsi_get_query_from_Q(model, child)
            if qpart is not None:
                query.append(qpart)
            continue
        k, v = child
        *field, filter = k.split(LOOKUP_SEP)
        rfield = model.get_reversed_serialize_field(field)
        if rfield is None and k in model.predefined_queries.keys():
            predefined = model.predefined_queries[k]
            predefined_q = predefined(v)
            qpart = nsi_get_query_from_Q(model, predefined_q)
            if qpart is not None:
                query.append(qpart)
            continue
        op = nsi_query_op.get(filter)
        if rfield is not None and op is not None:
            rfield = ".".join(rfield)
            unquoted_val = v
            if isinstance(unquoted_val, str):
                unquoted_val = unquoted_val.replace("\"", "\\\"")
            v = format_query_value(unquoted_val)
            query.append(op.format(field=rfield, val=v, unquoted_val=unquoted_val))
        elif rfield is None:
            logger.warning("Wrong nsi filter {}={}, unknown field name {}".format(k, v, field))
        else:
            logger.warning("Wrong nsi filter {}={}, unknown filter {}".format(k, v, filter))
    return "(" + " {} ".format(q.connector).join(query) + ")" if query else None


def query_quote(query):
    return quote(quote(query, safe=""), safe="")