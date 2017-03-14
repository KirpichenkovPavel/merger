# coding=utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.constants import LOOKUP_SEP
from django_remote_model.util.util import nsi_get_query_from_Q
from django.conf import settings
from remote_impl.nsi import NsiImpl
from remote_impl.remote_database_exception import RemoteDatabaseError

import polyauth_remote


import main_remote


class Nsi:
    def __init__(self, server_uri=settings.NSI_SERVER_URI, api_path=settings.NSI_API_PATH):
        self.__server_uri = server_uri
        self.__api_path = api_path

        self.__impl = NsiImpl(server_uri, api_path)

    def bp_authenticate(self, username, password):
        """Checks BP authentication"""
        return self.__impl.bp_authenticate(username, password)

    def paternity_test(self, child, father):
        """
        Checks with NSI query if 'child' department is a sub-department of a 'father' department
        :param child: checked child department
        :param father: checked father department
        :return: true if 'child' is a sub-department of 'father', else otherwise
        """
        return self.__impl.paternity_test(child.id, father.id)

    def get_department_head(self, department):
        """
        Get head of department
        :param department: department
        :return: Employee corresponds to head of department
        """
        empl = self.__impl.get_department_head(department.id)
        if empl is not None:
            return main_remote.models.Employee.get_serializer().deserialize(empl)
        else:
            return None

    def get_division_children(self, division):
        """
        Get head of department
        :param division: division
        :return: json object with child divisions list
        """
        divs = self.__impl.get_division_children(division.id)
        if divs is not None:
            serializer = main_remote.models.Division.get_serializer()
            return [serializer.deserialize(div) for div in divs]
        else:
            return None

    def get_deep_registry_permissions_for_user(self, user):
        """
        Gets a list of instances of LocalPermissionInst class with user permissions got from NSI
        Permissions are expanded with daughter departments permissions by NSI.
        :param user: user
        :return: list of user permissions
        """
        perms = self.__impl.get_deep_registry_permissions_for_employee(user.employee_id)
        if perms is not None:
            to_ret = []
            for perm in perms:
                children = perm["children"]
                children.append(perm["division"])
                for c in children:
                    perm["division"] = c
                    to_ret.append(polyauth_remote.models.RegistryRemotePermissionInst.get_serializer().deserialize(perm))

            return to_ret
        else:
            return []

    def employee_exists(self, employee_id):
        """
        Check if employee with given tabular number exists
        :param employee_id: tabular number
        :return:
        """
        try:
            main_remote.models.Employee.objects.get(id=employee_id)
        except ObjectDoesNotExist:
            return False
        else:
            return True

    def update_user_info(self, user):
        """
        Updates name, surname & others from NSI
        :param user: user to update
        :return:
        """
        user.first_name = user.employee.first_name
        user.middle_name = user.employee.middle_name
        user.last_name = user.employee.last_name
        try:
            info = user.employee.info
            user.email = info.email
        except ObjectDoesNotExist:
            pass
        user.save()

    def get_object_by_id(self, model, id):
        try:
            json_object = self.__impl.get_object_by_id(model.url, id, model)
        except RemoteDatabaseError as e:
            if e.code == RemoteDatabaseError.ENTITY_NOT_FOUND:
                raise model.DoesNotExist("{} with id={} does not exist.".format(model._meta.object_name, id))
            else:
                raise

        return model.get_serializer().deserialize(json_object)

    def get_objects_with_paging(self, model, get_objects_func, limit_low, limit_high):
        page_size = self.__impl.get_page_size()
        page = limit_low // page_size if limit_low is not None else 0
        part_start = limit_low % page_size if limit_low is not None else 0
        part_end = limit_high - page * page_size if limit_high is not None else page_size
        while True:
            try:
                objs = get_objects_func(page=page)
            except RemoteDatabaseError:
                break
            result_part = objs[part_start:part_end]
            if len(result_part) == 0:
                break
            for res in result_part:
                yield model.get_serializer().deserialize(res)
            if len(objs) < page_size:
                break
            page += 1
            part_start = 0
            if limit_high is not None:
                part_end -= page_size
                if part_end <= 0:
                    break

    def create_object(self, obj):
        serializer = obj.get_serializer()
        result_json = self.__impl.create_object(obj.url, serializer.serialize(obj), obj._meta.model)
        result = serializer.deserialize(result_json)
        return result

    def modify_object(self, obj):
        serializer = obj.get_serializer()
        result_json = self.__impl.modify_object(obj.url, serializer.serialize(obj), obj._meta.model)
        result = serializer.deserialize(result_json)
        return result

    def delete_object(self, obj):
        result = self.__impl.delete_object(obj.url, obj.pk, obj._meta.model)
        return result

    def get_invalid_roles(self, role_template_id):
        serializer = polyauth_remote.models.Role.get_serializer()
        roles = self.__impl.get_objects("/roletemplate/{}/invalid".format(role_template_id), model=polyauth_remote.models.Role)
        return [serializer.deserialize(role) for role in roles]

    def get_objects_agg(self, model, query, agg_type, agg_field):
        query = nsi_get_query_from_Q(model, query)
        agg_field = agg_field.split(LOOKUP_SEP)
        field = model.get_reversed_serialize_field(agg_field)
        agg = "{}({})".format(agg_type, ".".join(field))
        return self.__impl.get_objects_agg(model.url, agg, query=query, model=model)

    def get_current_user_nsi_permissions_with_role(self, bp_id=None):
        serializer = polyauth_remote.models.NsiRemotePermissionInst.get_serializer()
        return [serializer.deserialize(perm) for perm in self.__impl.get_current_user_nsi_permissions_with_role(bp_id)]

    def get_nsi_permissions_with_role(self, employee_id, bp_id):
        serializer = polyauth_remote.models.NsiRemotePermissionInst.get_serializer()
        return [serializer.deserialize(perm) for perm in self.__impl.get_nsi_permissions_with_role(employee_id, bp_id)]

    def get_core_permissions_with_role(self, employee_id):
        serializer = polyauth_remote.models.RegistryRemotePermissionInst.get_serializer()
        return [serializer.deserialize(perm) for perm in self.__impl.get_core_permissions_with_role(employee_id)]


nsi = Nsi()
