from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django_remote_model.util.util import shell_authenticate, add_bp_credentials


def bp_user_auth():
    shell_authenticate(settings.MANAGEMENT_USER_NAME, settings.MANAGEMENT_USER_PASS)
    request = CrequestMiddleware.get_request()
    request = add_bp_credentials(request, settings.MANAGEMENT_BP_NAME, settings.MANAGEMENT_BP_PASS)
    CrequestMiddleware.set_request(request)


