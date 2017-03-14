from django.conf import settings

from nsi_client.queries import Nsi

ldap_proxy = Nsi(settings.LDAP_PROXY_SERVER_URI, settings.LDAP_PROXY_API_PATH)
