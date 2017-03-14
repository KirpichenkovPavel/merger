from django_remote_model.models import RemoteModel


class RemoteRouter:
    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if isinstance(obj1, RemoteModel) or isinstance(obj2, RemoteModel):
            return True
        return None

    def allow_migrate(self, db, model):
        return None