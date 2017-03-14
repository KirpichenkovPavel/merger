from django.contrib.auth.models import AbstractUser
from django.db import models
from django_remote_model.models import RemoteOneToOneField, RemoteForeignKey
from main_remote.models import Employee
from main_remote.mixins import NamedPersonMixin


class PolyUser(AbstractUser, NamedPersonMixin):
    """
    Polyana user. A django user with tabular number field.
    """
    # TODO: !!! null=True and default=None should be removed (when we will know how to get tab_no from LDAP) !!!
    employee = RemoteForeignKey(Employee, verbose_name="сотрудник", related_name="users", null=True)
    middle_name = models.CharField("отчество", max_length=30, blank=True)
    is_fake = models.BooleanField("является служебным", default=False)
    expiration_date = models.DateTimeField("срок действия", null=True, blank=True, default=None)

    # TODO: remove or make the same as employee
    def get_full_name(self):
        return "{} {} {}".format(self.first_name, self.middle_name, self.last_name)

    def get_short_name(self):
        first_name = "{}. ".format(self.first_name[0]) if self.first_name else ""
        middle_name = "{}. ".format(self.middle_name[0]) if self.middle_name else ""
        return first_name + middle_name + self.last_name

    def get_first_and_second_name(self):
        first_name = self.first_name if self.first_name is not None else ""
        middle_name = self.middle_name if self.middle_name is not None else ""
        space = " " if first_name and middle_name else ""
        return first_name + space + middle_name

    def __str__(self):
        return self.red_tape_full_name or self.username
