from django.db import models
from django_remote_model.query import RemoteNSIQuerySet, RemoteCoreResultTypeQuerySet, RemoteCoreQuerySet, \
    RemoteLdapProxyQuerySet


class RemoteManager(models.Manager):

    use_for_related_fields = True

    def get_queryset(self):
        pass


class RemoteNSIManager(RemoteManager):

    def get_queryset(self):
        return RemoteNSIQuerySet(self.model)


class RemoteLdapProxyManager(RemoteManager):

    def get_queryset(self):
        return RemoteLdapProxyQuerySet(self.model)


class RemoteNSIFilteredManager(RemoteNSIManager):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.qfilters = args
        self.filters = kwargs

    def get_queryset(self):
        return super().get_queryset().filter(*self.qfilters, **self.filters)


class RemoteCoreResultTypeManager(RemoteManager):

    def get_queryset(self):
        return RemoteCoreResultTypeQuerySet(self.model)


class RemoteCoreManager(models.Manager):

    def get_queryset(self):
        return RemoteCoreQuerySet(self.model)


class FakeManager(models.Manager):

    use_for_related_fields = True

    def __init__(self, model, values):
        self.model = model
        self.fake_model = hasattr(model, "url") and model.url == ""
        self.values = values

    def get_queryset(self):
        qs = RemoteNSIQuerySet(model=self.model)
        qs._result_cache = self.values
        qs.query.filterable = False
        return qs

    def add(self, *objs):
        self.values.extend(objs)
    add.alters_data = True

    def remove(self, *objs):
        for o in objs:
            self.values.remove(o)
    remove.alters_data = True

    def clear(self):
        self.values.clear()
    clear.alters_data = True

    def create(self, **kwargs):
        if self.fake_model:
            obj = self.model(**kwargs)
            self.values.append(obj)
            return obj
        else:
            return None
    create.alters_data = True