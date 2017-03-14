from django.db import models
from django_remote_model.models import RemoteForeignKey, RemoteNSIModel, RemoteManyToManyField, \
    NoneEmptyRemoteSerializeCharField, RemoteLdapProxyModel
from django_remote_model.serializers import ListSerializer
from main_remote.models import BusinessProcess, Division, Employee, NSI_CATALOGUES, CoreResultType


class NsiRemotePermissionInst(RemoteNSIModel):
    """
    NSI permission instance of type 'NsiRemotePermission' for a user from a business process
    to access catalogue of type 'catalogue_type'
    """

    PT_RD = "RD"
    PT_WR = "WR"

    PERMISSION_TYPES = (
        (PT_RD, "чтение"),
        (PT_WR, "запись")
    )

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "назначение удаленного права в НСИ"
        verbose_name_plural = "назначения удаленных прав в НСИ"
        app_label = "polyauth_remote"

    user = RemoteForeignKey(Employee, verbose_name="сотрудник",
                            related_name="nsi_permissions")
    type = models.CharField("право", choices=PERMISSION_TYPES, max_length=2)
    business_process = RemoteForeignKey(BusinessProcess, verbose_name="бизнес-процесс", related_name="+")
    catalogue = models.CharField("каталог", choices=NSI_CATALOGUES + (("ALL", "*"),), max_length=50)

    url = "/businessprocess/permission"

    serialize_model = {
        "id": "id",
        "employee": {
            "id": "user"
        },
        "permissionType": "type",
        "businessProcess": {
            "id": "business_process"
        },
        "entity": "catalogue"
    }

    query_names = {
        "user": ("employee", "exact"),
        "business_process": ("businessProcess", "exact"),
        "type": ("permissionType", "exact"),
        "catalogue": ("entity", "exact")
    }

    allow_save = True
    allow_delete = True

    def __str__(self):
        return "{} has {} permission for {} with {}".format(self.user,
                                                            self.type,
                                                            self.catalogue,
                                                            self.business_process)


class LdapProxyPermissionInst(RemoteLdapProxyModel):
    PT_LOGIN = "LOGIN"
    PT_NOT_LOGIN = "NOT_LOGIN"
    PT_LOGIN_AS = "LOGIN_AS"
    PT_ADMIN = "ADMIN"

    PERMISSION_TYPES = (
        (PT_LOGIN, "вход"),
        (PT_NOT_LOGIN, "запрет входа"),
        (PT_LOGIN_AS, "вход под чужим именем"),
        (PT_ADMIN, "администрирование")
    )

    user = RemoteForeignKey(Employee, verbose_name="сотрудник",
                            related_name="ldap_proxy_permissions")
    type = models.CharField("право", choices=PERMISSION_TYPES, max_length=32)

    url = "/permission"

    serialize_model = {
        "id": "id",
        "employeeId": "user",
        "type": "type"
    }

    custom_reverse_serialize = {
        "user": ("employeeId",)
    }

    allow_save = True
    allow_delete = True

    def __str__(self):
        return "{} has {} permission".format(self.user, self.type)


class RegistryRemotePermissionInst(RemoteNSIModel):
    """
    Registry permission instance for a user to access
    specific division result types
    """

    PT_ALL = "ALL"
    PT_READ = "READ"
    PT_WRITE = "WRITE"
    PT_VERIFY = "VERIFY"
    PT_ADMIN = "ADMIN"
    PT_REPORT = "REPORT"
    PT_CREATE = "CREATE"

    PERMISSION_TYPES = (
        (PT_ALL, "*"),
        (PT_READ, "Чтение"),
        (PT_WRITE, "Изменение"),
        (PT_VERIFY, "Верификация"),
        (PT_ADMIN, "Администрирование"),
        (PT_REPORT, "Построение отчётов"),
        (PT_CREATE, "Создание")
    )

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "назначение удаленного права в Реестре"
        verbose_name_plural = "назначения удаленных прав в Реестре"
        app_label = "polyauth_remote"

    user = RemoteForeignKey(Employee, verbose_name="сотрудник",
                            related_name="registry_permissions")
    type = models.CharField("право", choices=PERMISSION_TYPES, max_length=255)
    result_type = \
        RemoteForeignKey(CoreResultType, verbose_name="тип результата", related_name="+")
    division = RemoteForeignKey(Division, verbose_name="подразделение", related_name="+")

    url = "/permission"

    serialize_model = {
        "id": "id",
        "employee": {
            "id": "user"
        },
        "permissionType": "type",
        "resultType": "result_type",
        "division": {
            "id": "division"
        }
    }

    query_names = {
        "user": ("employee", "exact"),
        "division": ("division", "exact"),
        "type": ("permissiontype", "exact"),
        "result_type": ("resulttype", "exact")
    }

    custom_reverse_serialize = {
        "result_type": ("resultType",)
    }

    allow_save = True
    allow_delete = True

    def __str__(self):
        return "{} has {} permission for {} in {}".format(self.user,
                                                          self.type,
                                                          self.result_type,
                                                          self.division)


class PermissionTemplate(RemoteNSIModel):
    employee = RemoteForeignKey(Employee, verbose_name="сотрудник", null=True, blank=True, related_name="+")
    employee_text = NoneEmptyRemoteSerializeCharField("шаблон сотрудника", max_length=300)
    permission_type = models.CharField("тип права РРД", max_length=300)
    result_type = models.CharField("тип результата", max_length=300)
    division = RemoteForeignKey(Division, verbose_name="подразделение", null=True, blank=True, related_name="+")
    division_text = NoneEmptyRemoteSerializeCharField("шаблон подразделения", max_length=300)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "шаблон права РРД"
        verbose_name_plural = "шаблоны прав РРД"
        app_label = "main_remote"

    serialize_model = {
        "employee": {
            "reference": {
                "id": "employee"
            },
            "text": "employee_text"
        },
        "permissionTypeName": "permission_type",
        "resultTypeName": "result_type",
        "division": {
            "reference": {
                "id": "division"
            },
            "text": "division_text"
        }
    }


class NsiPermissionTemplate(RemoteNSIModel):
    employee = RemoteForeignKey(Employee, verbose_name="сотрудник", null=True, blank=True, related_name="+")
    employee_text = NoneEmptyRemoteSerializeCharField("шаблон сотрудника", max_length=300)
    permission_type = models.CharField("тип права НСИ", max_length=300)
    business_process = RemoteForeignKey(BusinessProcess, verbose_name="бизнес-процесс", null=True,
                                        blank=True, related_name="+")
    business_process_text = NoneEmptyRemoteSerializeCharField("шаблон бизнес-процесса", max_length=300)
    entity = models.CharField(verbose_name="каталог НСИ", max_length=300)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "шаблон права НСИ"
        verbose_name_plural = "шаблоны прав НСИ"
        app_label = "main_remote"

    serialize_model = {
        "employee": {
            "reference": {
                "id": "employee"
            },
            "text": "employee_text"
        },
        "nsiPermissionTypeName": "permission_type",
        "businessProcess": {
            "reference": {
                "id": "business_process"
            },
            "text": "business_process_text"
        },
        "entity": "entity"
    }


class RoleTemplate(RemoteNSIModel):
    name = models.CharField("имя", max_length=300)
    permission_templates = RemoteManyToManyField(PermissionTemplate, verbose_name="шаблоны прав РРД",
                                                 related_name="+", remote_m2m_list=True)
    nsi_permission_templates = RemoteManyToManyField(NsiPermissionTemplate, verbose_name="шаблоны прав НСИ",
                                                     related_name="+", remote_m2m_list=True)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "шаблон роли"
        verbose_name_plural = "шаблоны роли"
        app_label = "main_remote"

    url = "/roletemplate"

    serialize_model = {
        "id": "id",
        "name": "name",
        "permissionTemplates": ("permission_templates", ListSerializer(PermissionTemplate)),
        "nsiPermissionTemplates": ("nsi_permission_templates", ListSerializer(NsiPermissionTemplate))
    }

    allow_save = True
    allow_delete = True

    def __str__(self):
        return self.name


class EmployeeParam(RemoteNSIModel):
    key = models.CharField("шаблон сотрудника", max_length=300)
    employee = RemoteForeignKey(Employee, verbose_name="сотрудник", related_name="+")

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "значение шаблона сотрудника"
        verbose_name_plural = "значения шаблонов сотрудников"
        app_label = "main_remote"


class EmployeeParamsSerializer:
    @staticmethod
    def serialize(local_field):
        return {ep.key: {"id": ep.employee_id} for ep in local_field.all()}

    @staticmethod
    def deserialize(remote_field):
        return [EmployeeParam(key=k, employee_id=e["id"]) for k, e in remote_field.items()]


class PermissionTypeParam(RemoteNSIModel):
    key = models.CharField("шаблон права РРД", max_length=300)
    permission_type = models.CharField("право", choices=RegistryRemotePermissionInst.PERMISSION_TYPES, max_length=255)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "значение шаблона права РРД"
        verbose_name_plural = "значения шаблонов прав РРД"
        app_label = "main_remote"


class PermissionTypeParamsSerializer:
    @staticmethod
    def serialize(local_field):
        return {ptp.key: ptp.permission_type for ptp in local_field.all()}

    @staticmethod
    def deserialize(remote_field):
        return [PermissionTypeParam(key=k, permission_type=pt) for k, pt in remote_field.items()]


class ResultTypeParam(RemoteNSIModel):
    key = models.CharField("шаблон типа результата", max_length=300)
    result_type = RemoteForeignKey(CoreResultType, verbose_name="тип результата", related_name="+")

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "значение шаблона типа результата"
        verbose_name_plural = "значения шаблонов типов результата"
        app_label = "main_remote"


class ResultTypeParamsSerializer:
    @staticmethod
    def serialize(local_field):
        return {rtp.key: rtp.result_type.name for rtp in local_field.all()}

    @staticmethod
    def deserialize(remote_field):
        return [ResultTypeParam(key=k, result_type_id=rt) for k, rt in remote_field.items()]


class DivisionParam(RemoteNSIModel):
    key = models.CharField("шаблон подразделения", max_length=300)
    division = RemoteForeignKey(Division, verbose_name="подразделение", related_name="+")

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "значение шаблона подразделения"
        verbose_name_plural = "значения шаблонов подразделений"
        app_label = "main_remote"


class DivisionParamsSerializer:
    @staticmethod
    def serialize(local_field):
        return {dp.key: {"id": dp.division_id} for dp in local_field.all()}

    @staticmethod
    def deserialize(remote_field):
        return [DivisionParam(key=k, division_id=d["id"]) for k, d in remote_field.items()]


class NsiPermissionTypeParam(RemoteNSIModel):
    key = models.CharField("шаблон права НСИ", max_length=300)
    permission_type = models.CharField("право НСИ", choices=NsiRemotePermissionInst.PERMISSION_TYPES, max_length=255)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "значение шаблона права НСИ"
        verbose_name_plural = "значения шаблонов прав НСИ"
        app_label = "main_remote"


class NsiPermissionTypeParamsSerializer:
    @staticmethod
    def serialize(local_field):
        return {ptp.key: ptp.permission_type for ptp in local_field.all()}

    @staticmethod
    def deserialize(remote_field):
        return [NsiPermissionTypeParam(key=k, permission_type=pt) for k, pt in remote_field.items()]


class BusinessProcessParam(RemoteNSIModel):
    key = models.CharField("шаблон бизнес-процесса", max_length=300)
    business_process = RemoteForeignKey(BusinessProcess, verbose_name="бизнес-процесс", related_name="+")

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "значение шаблона бизнес-процесса"
        verbose_name_plural = "значения шаблонов бизнес-процессов"
        app_label = "main_remote"


class BusinessProcessParamsSerializer:
    @staticmethod
    def serialize(local_field):
        return {bp.key: {"id": bp.business_process_id} for bp in local_field.all()}

    @staticmethod
    def deserialize(remote_field):
        return [BusinessProcessParam(key=k, business_process_id=bp["id"]) for k, bp in remote_field.items()]


class EntityParam(RemoteNSIModel):
    key = models.CharField("шаблон каталога НСИ", max_length=300)
    entity = models.CharField("каталог НСИ", choices=NSI_CATALOGUES, max_length=255)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "значение шаблона каталога НСИ"
        verbose_name_plural = "значения шаблонов каталогов НСИ"
        app_label = "main_remote"


class EntityParamsSerializer:
    @staticmethod
    def serialize(local_field):
        return {e.key: e.entity for e in local_field.all()}

    @staticmethod
    def deserialize(remote_field):
        return [EntityParam(key=k, entity=e) for k, e in remote_field.items()]


class Role(RemoteNSIModel):
    employee = RemoteForeignKey(Employee, verbose_name="сотрудник", related_name="+")
    role_template = RemoteForeignKey(RoleTemplate, verbose_name="шаблон роли", null=True, blank=True)
    employee_params = RemoteManyToManyField(EmployeeParam, verbose_name="значения шаблонов сотрудников",
                                            related_name="+", remote_m2m_list=True)
    permission_type_params = RemoteManyToManyField(PermissionTypeParam, verbose_name="значения шаблонов прав РРД",
                                                   related_name="+", remote_m2m_list=True)
    result_type_params = RemoteManyToManyField(ResultTypeParam, verbose_name="значения шаблонов типов результата",
                                               related_name="+", remote_m2m_list=True)
    division_params = RemoteManyToManyField(DivisionParam, verbose_name="значения шаблонов подразделений",
                                            related_name="+", remote_m2m_list=True)
    nsi_permission_type_params = RemoteManyToManyField(NsiPermissionTypeParam, verbose_name="значения шаблонов прав НСИ",
                                                       related_name="+", remote_m2m_list=True)

    business_process_params = RemoteManyToManyField(BusinessProcessParam, verbose_name="значения шаблонов бизнес-процессов",
                                                    related_name="+", remote_m2m_list=True)
    entity_params = RemoteManyToManyField(EntityParam, verbose_name="значения шаблонов каталогов НСИ",
                                          related_name="+", remote_m2m_list=True)

    class Meta(RemoteNSIModel.Meta):
        verbose_name = "роль"
        verbose_name_plural = "роли"
        app_label = "main_remote"

    url = "/role"

    serialize_model = {
        "id": "id",
        "employee": {
            "id": "employee"
        },
        "roleTemplate": {
            "id": "role_template"
        },
        "roleParams": {
            "employeeParams": ("employee_params", EmployeeParamsSerializer),
            "permissionTypeParams": ("permission_type_params", PermissionTypeParamsSerializer),
            "resultTypeParams": ("result_type_params", ResultTypeParamsSerializer),
            "divisionParams": ("division_params", DivisionParamsSerializer),
            "nsiPermissionTypeParams": ("nsi_permission_type_params", NsiPermissionTypeParamsSerializer),
            "businessProcessParams": ("business_process_params", BusinessProcessParamsSerializer),
            "entityParams": ("entity_params", EntityParamsSerializer)
        }
    }

    query_names = {
        "employee": ("employee", "exact")
    }

    allow_save = True
    allow_delete = True

    @property
    def name(self):
        if self.role_template:
            return self.role_template.name
        return None