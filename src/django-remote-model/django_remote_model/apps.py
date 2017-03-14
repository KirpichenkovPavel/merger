from django.apps.config import AppConfig
from django.db.models.loading import get_models, get_model


class RemoteCoreModelsConfig(AppConfig):

    name = "django_remote_model"

    def ready(self):
        RemoteCoreResultModel = get_model("django_remote_model.RemoteCoreResultModel")
        if not hasattr(RemoteCoreResultModel, "subclasses_result_types"):
            RemoteCoreResultModel.subclasses_result_types = {}
        for model in get_models():
            if issubclass(model, RemoteCoreResultModel):
                if hasattr(model, "TYPE"):
                    RemoteCoreResultModel.subclasses_result_types[model.TYPE] = model
            if hasattr(model, "_calculate_reversed_serialize_model"):
                model._calculate_reversed_serialize_model()
