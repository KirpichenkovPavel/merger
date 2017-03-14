import pprint
import crequest
from crequest.middleware import CrequestMiddleware
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http.request import HttpRequest
from django_auth_ldap.backend import LDAPBackend, logger
import ldap
from main_remote.models import Employee
from nsi_client.queries import nsi
from django_auth_ldap.backend import _LDAPUser
from polyauthentication.exceptions import EmployeeIDConflict, NoEmployeeID, NoUserInNSI
from django.db import transaction
from polyauthentication.models import PolyUser
from django_remote_model.util.util import shell_authenticate, add_bp_credentials
from django.conf import settings

class PolyauthenticationBackend(LDAPBackend):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = True

    _nsi_client = nsi

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def authenticate(self, username, password):
        if len(password) == 0 and not self.settings.PERMIT_EMPTY_PASSWORD:
            logger.debug('Rejecting empty password for %s' % username)
            return None
        # Getting user from LDAP
        ldap_user = _PolyauthenticationLDAPUser(self, username=username)
        if not ldap_user.ldap_authenticate(password):
            return None
        attrs = ldap_user.attrs
        employee_id = None
        if attrs is not None and len(attrs.get("employeeID")) > 0:
            employee_id = attrs.get("employeeID")[0]
        if employee_id is None:
            raise NoEmployeeID("Current user has no employee ID")

        request = CrequestMiddleware.get_request()
        if request is None:
            shell_authenticate(username, password)
        else:
            fake_user = PolyUser(username=username)
            request.user = fake_user
            request.session["password"] = password
        auth_bp = getattr(settings, "AUTHENTICATION_BP", {})
        bp_username = auth_bp.get("username", "")
        bp_password = auth_bp.get("password", "")
        if bp_username and bp_password:
            add_bp_credentials(request, bp_username, bp_password)
        try:
            employee = Employee.objects.get(id=employee_id)
        except ObjectDoesNotExist:
            raise NoUserInNSI("User does not exist in NSI")

        user = ldap_user.add_user_to_db()
        if user is not None:
            nsi.update_user_info(user)
        return user


class _PolyauthenticationLDAPUser(_LDAPUser):
    def ldap_authenticate(self, password):
        """
        Searches LDAP user and populates his attributes
        """
        try:
            self._authenticate_user_dn(password)
            self._check_requirements()
        except self.AuthenticationFailed as e:
            logger.debug(u"Authentication failed for %s: %s" % (self._username, e))
            return False
        except ldap.LDAPError as e:
            logger.warning(u"Caught LDAPError while authenticating %s: %s",
                           self._username, pprint.pformat(e))
            return False
        except Exception:
            logger.exception(u"Caught Exception while authenticating %s",
                             self._username)
            raise
        return True

    def add_user_to_db(self):
        """
        Creating user id DB
        """
        user = None

        try:
            self._get_or_create_user()
            user = self._user
        except self.AuthenticationFailed as e:
            logger.debug(u"Authentication failed for %s: %s" % (self._username, e))
        except ldap.LDAPError as e:
            logger.warning(u"Caught LDAPError while authenticating %s: %s",
                           self._username, pprint.pformat(e))
        except Exception:
            logger.exception(u"Caught Exception while authenticating %s",
                             self._username)
            raise

        return user
