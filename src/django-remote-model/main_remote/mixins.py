from crequest.middleware import CrequestMiddleware
from django.db.models.query_utils import Q

import main_remote.models
import polyauth_remote
from nsi_client.queries import nsi

__author__ = 'gagarski'


class NamedPersonMixin:
    @property
    def full_name(self):
        return self.red_tape_full_name

    @property
    def short_name(self):
        return self.red_tape_short_name

    @property
    def vocative(self):
        """
        :return: Vocative E. g. "Ivan Ivanovich"
        """
        first_name = "{}".format(self.first_name) if self.first_name else ""
        middle_name = " {}".format(self.middle_name) if self.middle_name else ""
        return first_name + middle_name

    @property
    def red_tape_full_name(self):
        """
        :return: Full name (last name is at the beginning). E. g. "Ivanov Ivan Ivanovich"
        """
        last_name = "{}".format(self.last_name) if self.last_name else ""
        first_name = " {}".format(self.first_name) if self.first_name else ""
        middle_name = " {}".format(self.middle_name) if self.middle_name else ""
        return last_name + first_name + middle_name

    @property
    def red_tape_short_name(self):
        """
        :return: Full name (last name is at the beginning). E. g. "Ivanov I. I."
        """
        last_name = "{}".format(self.last_name) if self.last_name else ""
        first_name = "\xa0{}.".format(self.first_name[0]) if self.first_name else ""
        middle_name = "\xa0{}.".format(self.middle_name[0]) if self.middle_name else ""
        return last_name + first_name + middle_name


class AccessByDivisionMixin:

    division_field = "division"

    @staticmethod
    def get_allowed_divisions():
        request = CrequestMiddleware.get_request()
        if request is None:
            return None
        active_role = request.session.get("active_role")
        if active_role is None:
            return None
        roles = polyauth_remote.models.Role.objects.filter(employee=request.user.employee, role_template__name=active_role)
        main_divisions = {d.division for role in roles for d in role.division_params.all()}
        if main_remote.models.Division.TOP_LEVEL_ID in (md.id for md in main_divisions):
            return None
        child_divisions = {cd for md in main_divisions for cd in nsi.get_division_children(md)}
        return main_divisions | child_divisions

    @classmethod
    def get_allowed_objects(cls):
        divisions = cls.get_allowed_divisions()
        if divisions is None:
            return cls.objects.all()
        else:
            return cls.objects.filter(**{"{}__in".format(cls.division_field): divisions})

    @classmethod
    def get_allowed_objects_filters(cls):
        divisions = cls.get_allowed_divisions()
        if divisions is None:
            return Q()
        else:
            return Q(**{"{}__in".format(cls.division_field): [d.id for d in divisions]})

    def is_allowed(self):
        divisions = self.get_allowed_divisions()
        if divisions is None:
            return True
        else:
            return self._meta.model.objects.\
                filter(**{"{}__in".format(self.division_field): divisions, "id": self.id}).exists()
