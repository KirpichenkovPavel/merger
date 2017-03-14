from django.contrib import admin

# Register your models here.
from polyauth_remote.models import *

admin.site.register(NsiRemotePermissionInst)
admin.site.register(RegistryRemotePermissionInst)

