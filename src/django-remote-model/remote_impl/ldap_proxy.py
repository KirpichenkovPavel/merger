from django.conf import settings

from remote_impl.nsi import NsiImpl

ldap_proxy_impl = NsiImpl(settings.LDAP_PROXY_SERVER_URI, settings.LDAP_PROXY_API_PATH)
