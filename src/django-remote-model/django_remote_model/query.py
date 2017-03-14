import asyncio
import logging
from inspect import isclass

from django.db import models
from django.db.models import query
from django.db.models.constants import LOOKUP_SEP
from django.db.models.fields import FieldDoesNotExist
from django.db.models.query_utils import Q

import django_remote_model
import django_remote_model.models
from core_client.queries import core
from django_remote_model.util.util import nsi_get_query_from_Q
from ldap_proxy_client.queries import ldap_proxy
from nsi_client.queries import nsi
from remote_impl.ldap_proxy import ldap_proxy_impl
from remote_impl.nsi import nsi_impl
from remote_impl.nsi_async import nsi_impl_async

logger = logging.getLogger('polyana_web')


class Query(object):
    def __init__(self):
        self.order_by = []
        self.extra_order_by = []
        self.default_ordering = []
        self.filters = {}
        self.excludes = {}
        self.filterable = True
        self.limit_high = None
        self.limit_low = 0
        self.where = False
        self.having = False
        self.select_related = False
        self.max_depth = None
        self.extra_select = {}
        self.select_for_update = False
        self._extra = None
        self._aggregates = None
        self.empty = False

    def can_filter(self):
        return self.filterable

    def clone(self):
        query = type(self)()
        query.order_by = self.order_by.copy()
        query.extra_order_by = self.extra_order_by.copy()
        query.default_ordering = self.default_ordering.copy()
        query.filters = self.filters.copy()
        query.excludes = self.excludes.copy()
        query.filterable = self.filterable
        query.limit_high = self.limit_high
        query.limit_low = self.limit_low
        query.where = self.where
        query.having = self.having
        query.select_related = self.select_related
        query.max_depth = self.max_depth
        query.extra_select = self.extra_select.copy()
        query.select_for_update = self.select_for_update
        query.empty = self.empty
        return query

    def clear_ordering(self, force_empty=False):
        self.order_by = []

    def filter(self, *args, **kwargs):
        self.filters.update(kwargs)

    def exclude(self, *args, **kwargs):
        self.excludes.update(kwargs)

    def set_limits(self, low=None, high=None):
        if high is not None:
            if self.limit_high is not None:
                self.limit_high = min(self.limit_high, self.limit_low + high)
            else:
                self.limit_high = self.limit_low + high
        if low is not None:
            if self.limit_high is not None:
                self.limit_low = min(self.limit_high, self.limit_low + low)
            else:
                self.limit_low = self.limit_low + low
        self.filterable = False

    def add_select_related(self, fields):
        """
        Sets up the select_related data structure so that we only select
        certain related models (as opposed to all models, when
        self.select_related=True).
        """
        field_dict = {}
        for field in fields:
            d = field_dict
            for part in field.split(LOOKUP_SEP):
                d = d.setdefault(part, {})
        self.select_related = field_dict
        self.related_select_cols = []
        self.related_select_fields = []

    def set_empty(self):
        self.empty = True

    def is_empty(self):
        return self.empty

    ##########################################
    # Fake methods required by admin options #
    ##########################################

    def add_fields(self, field_names, allow_m2m=True):
        """ Fake method. """
        pass

    def trim_extra_select(self, names):
        """ Fake method. """
        pass

    def results_iter(self):
        """ Fake method. """
        return []

    def combine(self, rhs, connector):
        """ Fake method. """
        pass

    def has_results(self, *args, **kwargs):
        """ Fake method. """
        return True

    def has_filters(self):
        """ Fake method. """
        return False

    def clear_deferred_loading(self):
        """ Fake method. """
        pass

    def add_deferred_loading(self, field_names):
        """ Fake method. """
        pass

    def add_immediate_loading(self, field_names):
        """ Fake method. """
        pass

    def clear_select_fields(self):
        """ Fake method. """
        pass

    def set_extra_mask(self, names):
        """ Fake method. """
        pass

    def set_aggregate_mask(self, names):
        """ Fake method. """
        pass

    def append_aggregate_mask(self, names):
        """ Fake method. """
        pass

    def get_compiler(self, using=None, connection=None):
        """ Fake method. """

        class compilerStub:
            def results_iter(self):
                return ()

        return compilerStub()


class RemoteQuerySet(query.QuerySet):
    """
    QuerySet which access remote resources.
    """
    def __init__(self, model=None, query=None):
        self.model = model
        self.query = query or Query()
        self._result_cache = None
        self._iter = None
        self._sticky_filter = False
        self._hints = {}
        self._db = False
        self._for_write = False
        self._prefetch_related_lookups = False

        self.params = {}

    ########################
    # PYTHON MAGIC METHODS #
    ########################

    # def __repr__(self):
    #     if not self.query.limit_start and not self.query.limit_stop:
    #         data = list(self[:query.REPR_OUTPUT_SIZE + 1])
    #         if len(data) > query.REPR_OUTPUT_SIZE:
    #             data[-1] = "...(remaining elements truncated)..."
    #     else:
    #         data = list(self)
    #     return repr(data)

    ########################################
    # METHODS THAT DO RESOURCE nsi_queries #
    ########################################

    def __bool__(self):
        return self.exists()

    def count(self):
        return len(self)

    def latest(self, field_name=None):
        """
        Returns the latest object, according to the model"s "get_latest_by"
        option or optional given field_name.
        """
        latest_by = field_name or self.model._meta.get_latest_by
        assert bool(latest_by), "latest() requires either a field_name parameter or \"get_latest_by\" in the model"

        self.query.order_by.append("-%s" % latest_by)
        return self.iterator().next()

    def exists(self):
        if self._result_cache is not None:
            return len(self._result_cache) > 0
        try:
            next(self.iterator())
        except StopIteration:
            return False
        else:
            return True

    def bulk_create(self, objs, batch_size=None):
        for obj in objs:
            obj.save(force_insert=True)
        return objs

    def update(self, **kwargs):
        rows = 0
        for obj in self:
            for attr, val in kwargs.items():
                setattr(obj, attr, val)
            obj.save(force_update=True)
            rows += 1
        return rows

    def delete(self):
        """
        Deletes the records in the current QuerySet.
        """
        del_query = self._clone()

        # Disable non-supported fields.
        del_query.query.select_related = False
        del_query.query.clear_ordering()

        for obj in list(del_query):
            obj.delete()

        # Clear the result cache, in case this QuerySet gets reused.
        self._result_cache = None
    delete.alters_data = True

    ##################################################################
    # PUBLIC METHODS THAT ALTER ATTRIBUTES AND RETURN A NEW QUERYSET #
    ##################################################################

    def filter(self, *args, **kwargs):
        """
        Returns a filtered QuerySet instance.
        """
        if args or kwargs:
            assert self.query.can_filter(), "Cannot filter a query once a slice has been taken."

        clone = self._clone()
        clone.query.filter(*args, **kwargs)
        return clone

    def exclude(self, *args, **kwargs):
        """
        Returns a filtered QuerySet instance.
        """
        if args or kwargs:
            assert self.query.can_filter(), "Cannot filter a query once a slice has been taken."

        clone = self._clone()
        clone.query.exclude(*args, **kwargs)
        return clone

    def complex_filter(self, filter_obj):
        """
        Returns a new QuerySet instance with filter_obj added to the filters.

        filter_obj can be a Q object (or anything with an add_to_query()
        method) or a dictionary of keyword lookup arguments.

        This exists to support framework features such as "limit_choices_to",
        and usually it will be more natural to use other methods.
        """
        if isinstance(filter_obj, Q):
            return self.filter(filter_obj)
        elif hasattr(filter_obj, "add_to_query"):
            raise NotImplementedError("Not implemented yet")
        return self.filter(**filter_obj)

    def select_related(self, *fields, **kwargs):
        """
        Returns a new QuerySet instance that will select related objects.

        If fields are specified, they must be ForeignKey fields and only those
        related objects are included in the selection.
        """
        depth = kwargs.pop("depth", 0)
        if kwargs:
            raise TypeError("Unexpected keyword arguments to select_related: %s"
                    % (kwargs.keys(),))
        obj = self._clone()
        if fields:
            if depth:
                raise TypeError("Cannot pass both \"depth\" and fields to select_related()")
            obj.query.add_select_related(fields)
        else:
            obj.query.select_related = True
        if depth:
            obj.query.max_depth = depth
        return obj

    def order_by(self, *field_names):
        """
        Returns a QuerySet instance with the ordering changed.
        """
        assert self.query.can_filter(), \
                "Cannot reorder a query once a slice has been taken."

        clone = self._clone()
        for field_name in field_names:
            clone.query.order_by.append(field_name)
        return clone

    def extra(self, select=None, where=None, params=None, tables=None,
              order_by=None, select_params=None):
        """
        Only to handle the case of the "cute trick" used in ModelForms (and
        per extension admin) for unique and date constraints.

        Example: ``.extra(select={"a": 1}).values("a").order_by()``.

        http://code.djangoproject.com/browser/django/trunk/django/forms/models.py#L322
        is an interesting documentation for details.
        """
        assert self.query.can_filter(), \
                "Cannot change a query once a slice has been taken"
        if select == {"a": 1}:
            # Totally hackish but we need a fake object to deal with
            # successive calls to values and order_by based on a count
            # which is the less expensive action for our implementation.
            class FakeInt(object):
                def __init__(self, count):
                    self.count = count

                def values(self, *fields):
                    if fields == ("a",): # double check that it's our case
                        return self

                def order_by(self):
                    return self.count

            return FakeInt(self.count())
        raise NotImplementedError("extra is not yet fully implemented.")

    ###################
    # PRIVATE METHODS #
    ###################

    def _clone(self, klass=None, setup=False, **kwargs):
        if klass is None:
            klass = self.__class__
        query = self.query.clone()
        if self._sticky_filter:
            query.filter_is_sticky = True
        c = klass(model=self.model, query=query)
        c.__dict__.update(kwargs)
        if setup and hasattr(c, "_setup_query"):
            c._setup_query()
        return c

    def _as_url(self):
        """
        Returns the internal query"s URL and parameters

        as (u"url", {"arg_key": "arg_value"}).
        """
        return self.model.get_resource_url_list(), self.query.parameters


class NSIQuery(Query):
    def __init__(self, model=None, queryset=None):
        super().__init__()
        self.model = model
        self.queryset = queryset
        self.q = Q()

    def clone(self, queryset=None):
        query = super().clone()
        query.model = self.model
        query.queryset = self.queryset
        query.q = self.q
        return query

    def _relate_Q(self, q, relate_to):
        if not q:
            return q
        result = q.clone()
        for i, child in enumerate(result.children):
            if isinstance(child, Q):
                result.children[i] = self._relate_Q(child, relate_to)
            else:
                result.children[i] = (LOOKUP_SEP.join(relate_to + [child[0]]), child[1])
        return result

    def _convert_Q(self, q, model=None):
        if not q:
            return q
        model = model or self.model
        result = q.clone()
        for i, child in enumerate(result.children):
            if isinstance(child, Q):
                result.children[i] = self._convert_Q(child, model)
            else:
                k, v = child
                spl = k.split(LOOKUP_SEP)
                f_model = model

                not_found = False

                idx = 0

                for f_name in spl:
                    custom = f_model.custom_reverse_serialize.get(f_name)
                    if custom:
                        if isclass(custom[-1]) and issubclass(custom[-1], models.Model):
                            f_model = custom[-1]
                            idx += 1
                        else:
                            break
                    else:
                        try:
                            field_type = f_model._meta.get_field(f_name)
                        except FieldDoesNotExist:
                            if f_name != "pk":
                                not_found = True
                            break
                        else:
                            if (isinstance(field_type, models.ForeignKey) or isinstance(field_type, models.ManyToManyField))\
                                    and issubclass(field_type.rel.to, django_remote_model.models.RemoteNSIModelBasic):
                                f_model = field_type.rel.to
                                idx += 1
                            else:
                                break

                predefined_query = f_model.get_predefined_query(LOOKUP_SEP.join(spl[idx:]), v)
                if predefined_query is not None:
                    result.children[i] = self._relate_Q(self._convert_Q(predefined_query, f_model), spl[:idx])
                    continue

                if not_found:
                    if spl[idx].endswith("_id"):
                        new_field_name = spl[idx][:-3]
                        try:
                            field_type = f_model._meta.get_field(new_field_name)
                        except FieldDoesNotExist:
                            pass
                        else:
                            if isinstance(field_type, models.ForeignKey) or isinstance(field_type, models.ManyToManyField):
                                spl[idx] = new_field_name
                                idx += 1
                                spl.insert(idx, "pk")
                                f_model = field_type.rel.to
                                not_found = False

                if not_found:
                    # query on foreign_key -> query on foreign_key.pk
                    if idx > 0 and idx == len(spl) - 1:
                        spl.insert(-1, "pk")
                    else:
                        continue

                if idx == len(spl):
                    spl.append("pk")

                if idx == len(spl) - 1 or len(spl) == 1:
                    spl.append("exact")

                if idx < len(spl) - 2:
                    logger.warning("No remote implementation for filter '{}={}' for model {}"
                                   .format(k, v, model.__name__))
                    continue

                if len(spl) > 1 and spl[-2] == "+":
                    continue

                if len(spl) > 1 and spl[-2] == "pk":
                    spl[-2] = f_model._meta.pk.name

                if isinstance(v, models.Model):
                    v = v.pk
                elif isinstance(v, (list, tuple, set)):
                    v = type(v)(vv.pk if isinstance(vv, models.Model) else vv for vv in v)
                # __isnull = True(False) -> ==(!=) null
                if spl[-1] == "isnull":
                    spl[-1] = "exact" if v else "exactnot"
                    v = None
                result.children[i] = (LOOKUP_SEP.join(spl), v)
        return result

    def filter(self, *args, **kwargs):
        for a in args:
            self.q &= self._convert_Q(a)
        if kwargs:
            self.q &= self._convert_Q(Q(**kwargs))

    @property
    def excluding_parameters(self):
        parameters = {}

        # Filtering
        for k, v in self.excludes.items():
            spl = k.split(LOOKUP_SEP)
            if len(spl) > 2:
                # skip related fields filters
                logger.warning("Not implemented exclude '{}={}' for model {}".format(k, v, self.model.__name__))
                continue
            elif len(spl) == 2 and spl[1] != "exact":
                logger.warning("Not implemented exclude '{}={}' for model {}".format(k, v, self.model.__name__))
                continue
            parameters[spl[0]] = v

        return parameters

    def get_compiler(self, using=None, connection=None):
        """ Fake method. """

        class CompilerStub:
            def __init__(self, queryset):
                self.queryset = queryset

            def results_iter(self):
                return ([o.id] for o in self.queryset)

        return CompilerStub(self.queryset)

    def as_query_string(self):
        return nsi_get_query_from_Q(self.model, self.q)

    def is_simple(self):
        return self.q.connector == Q.AND and not any(isinstance(c, Q) for c in self.q.children)

    def simple_filters(self):
        if self.q.connector == Q.AND:
            return dict(c for c in self.q.children if not isinstance(c, Q))
        else:
            return dict()


class RemoteNSIQuerySet(RemoteQuerySet):
    """
    QuerySet which access remote NSI resources.
    """

    _nsi_impl = nsi_impl
    _nsi = nsi
    _nsi_impl_async = nsi_impl_async

    def __init__(self, model=None, query=None):
        super().__init__(model, query or NSIQuery(model, self))
        self.sort = None
        self.desc = None

    def count(self):
        if self.query.empty:
            return 0
        m2m_field, rel_id = self._try_to_find_m2m_in_query()
        if m2m_field is not None:
            return len(list(self))
        else:
            return self._nsi_impl.get_objects_count(self.model.url, query=self.query.as_query_string(), model=self.model)

    @asyncio.coroutine
    def count_async(self):
        if self.query.empty:
            return 0
        m2m_field, rel_id = self._try_to_find_m2m_in_query()
        if m2m_field is not None:
            return len(list(self))
        else:
            result = yield from self._nsi_impl_async.get_objects_count(self.model.url,
                                                                  query=self.query.as_query_string(),
                                                                  model=self.model)
            return result

    def exists(self):
        if self._result_cache is not None:
            return len(self._result_cache) > 0
        else:
            return self.count() > 0

    def order_by(self, *field_names):
        """
        Returns a QuerySet instance with the ordering changed.
        """
        assert self.query.can_filter(), "Cannot reorder a query once a slice has been taken."

        if len(field_names) == 0:
            return self
        clone = self._clone()
        desc = field_names[0].startswith("-")
        sort_names = []
        for sort_name in field_names:
            if sort_name[0] == "-":
                sort_name = sort_name[1:]
            spl = sort_name.split(LOOKUP_SEP)
            sort_fields = self.model.get_reversed_serialize_field(spl)
            if sort_fields is not None:
                sort_names.append(".".join(sort_fields))
        if not sort_names:
            return clone
        clone.sort = ",".join(sort_names)
        clone.desc = desc
        clone.query.order_by = list(field_names)
        return clone

    def reverse(self):
        clone = self._clone()
        clone.desc = not clone.desc
        return clone

    ####################################
    # METHODS THAT DO RESOURCE nsi_queries #
    ####################################

    def _exclude(self, obj):

        for k, v in self.query.excluding_parameters.items():
            if getattr(obj, k) == v:
                return True
        return False

    def _get_id_query(self, filter_params):
        custom_pk = self.model._meta.pk.attname

        local_id = self.model.LOCAL_ID_NAME

        id_query = {local_id, local_id + LOOKUP_SEP + "exact"}

        if custom_pk == local_id:
            id_query.add("pk")
            id_query.add("pk" + LOOKUP_SEP + "exact")

        not_id_query = set(filter_params.keys())
        not_id_query.difference_update(id_query)

        id_query.intersection_update(filter_params.keys())
        return id_query, not_id_query

    def _try_to_get_by_id(self, query_params):

        filter_params = dict(query_params)
        filter_params.update(self.query.simple_filters())

        id_query, not_id_query = self._get_id_query(filter_params)

        if len(not_id_query) > 0:
            return None

        if len(id_query) > 0:
            return self._nsi.get_object_by_id(self.model, filter_params[id_query.pop()])

        return None

    def _try_to_find_m2m_in_query(self):
        for k, v in self.query.simple_filters().items():
            spl = k.split(LOOKUP_SEP, 1)
            if len(spl) < 2:
                spl.append("exact")
            field_name, query = spl
            try:
                field_type, m, direct, m2m = self.model._meta.get_field_by_name(field_name)
            except FieldDoesNotExist:
                continue
            if not m2m:
                continue
            m2m_field = field_type if direct else field_type.field
            if not isinstance(m2m_field, django_remote_model.models.RemoteManyToManyField):
                continue
            id_name = m2m_field.m2m_reverse_target_field_name() if direct else m2m_field.m2m_target_field_name()
            if query not in [id_name, id_name + LOOKUP_SEP + "exact", "exact"]:
                continue
            return field_name, v
        return None, None

    def _get_as_m2m(self, field_name, rel_id):
        field_type, m, direct, m2m = self.model._meta.get_field_by_name(field_name)
        m2m_field = field_type if direct else field_type.field
        m2m_url = m2m_field.remote_m2m_reverse_url if direct else m2m_field.remote_m2m_url
        if m2m_url is not None:
            rel_model = m2m_field.rel.to if direct else m2m_field.model
            model_url = rel_model.url
            yield from self._nsi.get_objects_with_paging(self.model,
                                                           lambda page: self._nsi_impl.get_objects_m2m(model_url, rel_id, m2m_url,
                                                                                            page=page, model=rel_model),
                                                           self.query.limit_low, self.query.limit_high)
        else:
            through = m2m_field.rel.through
            through_query = m2m_field.m2m_reverse_name() if direct else m2m_field.m2m_column_name()
            through_field = m2m_field.m2m_column_name() if direct else m2m_field.m2m_reverse_name()
            through_objects = through.objects.filter(**{through_query: rel_id})
            if isinstance(through, django_remote_model.models.RemoteNSIModel):
                through_objects = through_objects.filter(valid=True)
            result_set = set()
            result_idx = 0
            for rid in (getattr(t, through_field) for t in through_objects):
                if rid not in result_set:
                    if result_idx >= self.query.limit_low and\
                            (self.query.limit_high is None or result_idx < self.query.limit_high):
                        yield self._nsi.get_object_by_id(self.model, rid)
                    result_idx += 1
                    result_set.add(rid)

    def iterator(self):
        if not self.query.empty:
            try:
                result = self._try_to_get_by_id({})
            except self.model.DoesNotExist:
                pass
            else:
                if result is not None:
                    if not self._exclude(result):
                        yield result
                else:
                    m2m_field, rel_id = self._try_to_find_m2m_in_query()
                    if m2m_field is not None:
                        yield from (obj for obj in self._get_as_m2m(m2m_field, rel_id) if not self._exclude(obj))
                    else:
                        yield from (obj for obj in self._nsi.get_objects_with_paging(
                            self.model,
                            lambda page: self._nsi_impl.get_objects(self.model.url, query=self.query.as_query_string(),
                                                         page=page, sort=self.sort, desc=self.desc, model=self.model),
                            self.query.limit_low, self.query.limit_high) if not self._exclude(obj))

    def __iter__(self):
        if self._result_cache is None:
            return self.iterator()
        else:
            return iter(self._result_cache)

    def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        # special case, get(id=X) directly request the resource URL and do not
        # filter on ids like Django's ORM do.

        # keep the custom attribute name of model for later use

        if not self.query.empty:
            result = self._try_to_get_by_id(kwargs)
            if result is not None and not self._exclude(result):
                return result

        # filter the request rather than retrieve it through get method
        return super(RemoteQuerySet, self).get(*args, **kwargs)

    def _clone(self, klass=None, setup=False, **kwargs):
        c = super()._clone(klass, setup, **kwargs)
        c.sort = self.sort
        c.desc = self.desc
        if klass is None or klass == RemoteNSIQuerySet:
            c.query.queryset = c
        return c


class RemoteLdapProxyQuerySet(RemoteNSIQuerySet):
    """
    QuerySet which access remote LDAP proxy resources.
    """

    _nsi_impl = ldap_proxy_impl
    _nsi = ldap_proxy


class CoreResultTypeQuery(Query):
    def __init__(self, queryset=None):
        super().__init__()
        self.queryset = queryset

    def clone(self, queryset=None):
        query = super().clone()
        query.queryset = self.queryset
        return query

    def get_compiler(self, using=None, connection=None):
        """ Fake method. """

        class CompilerStub:
            def __init__(self, queryset):
                self.queryset = queryset

            def results_iter(self):
                return ([o.id] for o in self.queryset)

        return CompilerStub(self.queryset)


class RemoteCoreResultTypeQuerySet(RemoteQuerySet):
    """
    QuerySet which access remote Core ResultTypes.
    """

    def __init__(self, model=None, query=None):
        super().__init__(model, query or CoreResultTypeQuery(self))

    ####################################
    # METHODS THAT DO RESOURCE nsi_queries #
    ####################################

    def _try_to_get_by_name(self, query_params):

        custom_pk = self.model._meta.pk.attname

        local_id = self.model.LOCAL_ID_NAME

        id_query = {local_id, local_id + LOOKUP_SEP + "exact"}

        if custom_pk == local_id:
            id_query.add("pk")
            id_query.add("pk" + LOOKUP_SEP + "exact")

        filter_params = dict(query_params)
        filter_params.update(self.query.filters)
        id_query.intersection_update(filter_params.keys())
        if len(id_query) > 0:
            name = filter_params[id_query.pop()]
            if name == "*":
                return self.model(name="*", schema={})
            else:
                return core.get_result_type(self.model, name)
        return None

    def iterator(self):
        if not self.query.empty:
            in_filter = None
            in_suffix = LOOKUP_SEP + "in"
            for k, v in self.query.filters.items():
                if k.endswith(in_suffix):
                    in_filter = (k, v)
                    break
            if in_filter is not None:
                for i in in_filter[1]:
                    c = self._clone()
                    c.query.filters.pop(in_filter[0])
                    c.query.filters[in_filter[0][:-len(in_suffix)]] = i
                    yield from c.iterator()
            else:
                try:
                    result = self._try_to_get_by_name({})
                except self.model.DoesNotExist:
                    pass
                else:
                    if result is not None:
                        yield result
                    else:
                        for k, v in self.query.filters.items():
                            logger.warning("Not implemented filter '{}={}' for model {}"
                                            .format(k, v, self.model.__name__))
                        for k, v in self.query.excludes.items():
                            logger.warning("Not implemented exclude '{}={}' for model {}"
                                            .format(k, v, self.model.__name__))
                        yield from core.get_result_types(self.model)
                        yield self.model(name="*", schema={})

    def get(self, *args, **kwargs):
        """
        Performs the query and returns a single object matching the given
        keyword arguments.
        """
        # special case, get(id=X) directly request the resource URL and do not
        # filter on ids like Django's ORM do.

        # keep the custom attribute name of model for later use

        if not self.query.empty:
            result = self._try_to_get_by_name(kwargs)
            if result is not None:
                return result

        # filter the request rather than retrieve it through get method
        return super(RemoteQuerySet, self).get(*args, **kwargs)

    def _clone(self, klass=None, setup=False, **kwargs):
        c = super()._clone(klass, setup, **kwargs)
        if klass is None or klass == RemoteCoreResultTypeQuerySet:
            c.query.queryset = c
        return c


class RemoteCoreQuerySet(query.QuerySet):

    def delete(self):
        """
        Deletes the records in the current QuerySet.
        """
        assert self.query.can_filter(), \
            "Cannot use 'limit' or 'offset' with delete."

        del_query = self._clone()

        # The delete is actually 2 queries - one to find related objects,
        # and one to delete. Make sure that the discovery of related
        # objects is performed on the same database as the deletion.
        del_query._for_write = True

        # Disable non-supported fields.
        del_query.query.select_for_update = False
        del_query.query.select_related = False
        del_query.query.clear_ordering(force_empty=True)

        for obj in list(del_query):
            obj.delete_from_core()

        super().delete()

    delete.alters_data = True
    delete.queryset_only = True
