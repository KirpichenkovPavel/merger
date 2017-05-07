from django.db import models
from main_remote.models import Student, Employee, Postgraduate
from collections import namedtuple, Counter



class Person(models.Model):
    """Человечище"""

    first_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    birth_date = models.DateField(null=True)

    def __init__(self, *args, **kwargs):

        def replace_none(arg_name):
            if not kwargs[arg_name]:
                kwargs[arg_name] = ""

        for arg in kwargs:
            if arg.endswith("name"):
                replace_none(arg)

        super().__init__(*args, **kwargs)

    def get_actual_instance(self):
        """Get instance (remote object) with the lastest valid_to date in related object."""

        def latest_instance(instance_list):
            """Instance without valid_to date is, probably, actual, otherwise, get one with the latest as actual."""
            res = instance_list[0]
            date = instance_list[0].valid_to
            for instance in instance_list:
                new_date = instance.valid_to
                if new_date is None:
                    return instance
                elif new_date > date:
                    date = new_date
                    res = instance
            return res

        hypos_list = self.hypostasis_set.all()
        instances = [x.get_non_empty_instance() for x in hypos_list]
        return latest_instance(instances)

    def get_actual_hypostasis(self):
        """Get hypostasis with the latest date for this person"""
        instance = self.get_actual_instance()
        for hypostasis in self.hypostasis_set.all():
            if hypostasis.get_non_empty_instance() == instance:
                return hypostasis

    def merge_persons(self, person_list):
        """Merge persons in the list with the first peson."""
        for person in person_list:
            if not isinstance(person, Person):
                raise TypeError("Merge persons: person in collection is not a Person type object.")
            for hypostasis in person.hypostasis_set.all():
                hypostasis.person = self
                hypostasis.save()
            person.delete()

    def fio_date_merge(self):
        pass

    # подумать про добавление учета дат
    # class attr_dict:
    #
    #     def __init__(self, *, attrlist):
    #         self.attr_dict

    def get_attribute_dict(self, attributes):
        """Counts the amount of different variants of attributes in person's hypostases.

        Returns a dict with a Counter for each dispatched attribute. Counters count every attribute independently.
        :param attributes: iterable of attributes from hypostases' related objects. Attributes must be strings.
        """
        attributes = {name: Counter() for name in attributes}
        for attribute in attributes:
            if not isinstance(attribute,str):
                raise TypeError("{0} is not a string.".format(attribute))
            attributes[attribute].update(
                [getattr(x.get_non_empty_instance(), attribute) for x in list(self.hypostasis_set.all())])
        return attributes
        # with dates?
        # attributes = {name: {} for name in attributes}
        # for attribute in attributes:
        #     attributes[attribute].update(
        #         {getattr(x.get_non_empty_instance(), attribute):{} for x in list(self.hypostasis_set.all())})
        # return attributes

    def check_pre_merge(self, person, **kwargs):
        """Check equivalence with another person and return metric."""
        return 100

    def prepare_merge(self, person, group=None):
        """Create pre-merge object for two persons."""
        pass
        # if group is None:
        #     group = PreMergeGroup()
            # PreMerge(primary=self, dependent=person).save()

    @classmethod
    def get_all_attrdicts(cls, *, attributes):
        """Get attribute dict for each person, return list of them"""
        return [(person,person.get_attribute_dict(attributes=attributes)) for person in list(Person.objects.all())]


    def __str__(self):
        return "{0} {1} {2}".format(self.last_name, self.first_name, self.middle_name)


class Hypostasis(models.Model):
    """Одна из сторон деятельности человечища."""

    employee_id = models.CharField(max_length=255, unique=True, null=True)
    student_id = models.IntegerField(unique=True, null=True)
    postgraduate_id = models.IntegerField(unique=True, null=True)
    person = models.ForeignKey(Person, null=True)

    def get_non_empty_instance(self):
        """Hyposatsis should have only one not-None id.

         Function returns existing related instance."""
        ids = namedtuple("ids", ["student_id", "employee_id", "postgraduate_id"])
        ids_tuple = ids(student_id=self.student_id,
                        employee_id=self.employee_id,
                        postgraduate_id=self.postgraduate_id)
        if ids_tuple.student_id is not None:
            if ids_tuple.employee_id is not None or ids_tuple.postgraduate_id is not None:
                raise ValueError("More than one non-empty id in hypostasis.")
            return Student.objects.get(id=ids_tuple.student_id)
        elif ids_tuple.employee_id is not None:
            if ids_tuple.postgraduate_id is not None:
                raise ValueError("More than one non-empty id in hypostasis.")
            return Employee.objects.get(id=ids_tuple.employee_id)
        elif ids_tuple.postgraduate_id is not None:
            return Postgraduate.objects.get(id=ids_tuple.postgraduate_id)
        else:
            raise ValueError("All ids in hypostasis are empty.")

    def __str__(self):
        from main.merge import get_instance_from_hypostasis
        instance = get_instance_from_hypostasis(self)
        st = str(type(instance)).split(".")[-1].split("'")[0] + " " + str(instance)
        return st

    def compare_attribute(self, another_hypostasis, attribute, another_attribute=None):
        """Compare Hypostasis attribute with another from another one"""
        if attribute not in self.__dict__ or \
                                another_attribute is not None and another_attribute not in another_hypostasis.__dict__:
            raise KeyError("No such attribute {}".format(attribute))
        if another_attribute is None:
            another_attribute = attribute
        return getattr(self, attribute) == getattr(another_hypostasis, another_attribute)

        # def compare_last_name(self, another_hypostasis):
        #     """For now checks complete equality."""
        #     return self.get_non_empty_instance().last_name == another_hypostasis.get_non_empty_hypostasis().last_name
        #
        # def compare_first_name(self, another_hypostasis):
        #     """For now checks complete equality."""
        #     return self.get_non_empty_instance().first_name == another_hypostasis.get_non_empty_hypostasis().first_name
        #
        # def compare_middle_name(self, another_hypostasis):
        #     """For now checks complete equality."""
        #     return self.get_non_empty_instance().middle_name == another_hypostasis.get_non_empty_hypostasis().middle_name
        #
        # def compare_birth_date(self, another_hypostasis):
        #     """For now checks complete equality."""
        #     return self.get_non_empty_instance().birth_date == another_hypostasis.get_non_empty_hypostasis().birth_date


# class PreMergeGroup(models.Model):
#     """m2m for persons that may be the same person."""
#
#     keyperson = models.ForeignKey(Person)
#     person = models.ManyToManyField(Person)
class Group(models.Model):
    inconsistent = models.BooleanField(default=False)

    @classmethod
    def mark_inconsitancy(cls):
        #for grp in cls.objects.all():
        pass


class GroupRecord(models.Model):
    """"""

    hypostasis = models.ForeignKey(Hypostasis)
    person = models.ForeignKey(Person)
    group = models.ForeignKey(Group, null=True)
    last_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True)
    birth_date = models.DateField(null=True)

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.last_name, self.first_name, self.middle_name, self.birth_date)

    def compare_attribute(self, another_record, attribute, another_attribute=None):
        if another_attribute is None:
            another_attribute = attribute
        if getattr(self, attribute) == getattr(another_record, another_attribute):
            return True
        else:
            return False

    def compare_attributes(self, another_record, attribute_list):
        for attribute in attribute_list:
            if not self.compare_attribute(another_record=another_record, attribute=attribute):
                return False
        return True

    def completely_equal(self, another_record):
        attributes = ['last_name', 'first_name', 'middle_name', 'birth_date']
        return self.compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_full_name(self, another_record):
        attributes = ['last_name', 'first_name', 'middle_name']
        return self.compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_first_and_middle_name(self, another_record):
        attributes = ['last_name', 'first_name', 'middle_name', 'birth_date']
        return self.compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_dates(self, another_record):
        return self.compare_attribute(another_record=another_record, attribute='birth_date')

    def has_equal_last_and_middle_name(self, another_record):
        attributes = ['last_name', 'middle_name', 'birth_date']
        return self.compare_attributes(another_record=another_record, attribute_list=attributes)

    def satisfies_new_group_condition(self, another_record):
        """No date check, used only in sorted-by-dates groups"""
        return self.has_equal_full_name(another_record) or self.has_equal_last_and_middle_name(another_record) or self.has_equal_first_and_middle_name(another_record)

    def satisfies_existing_group_condition(self, another_record):
        if self.has_equal_dates(another_record):
            if self.satisfies_new_group_condition(another_record):
                return True
        else:
            return False

    def compare_with_group(self, group):
        """ Full check only for inconsistent groups. Otherwise check with random record in group"""
        if not isinstance(group, Group):
            raise TypeError('group must be a Group instance')
        elif self.group is not None:
            raise AttributeError('group record should not have group yet')
        else:
            if group.inconsistent:
                for record_to_compare in group.grouprecord_set.all():
                    if self.satisfies_existing_group_condition(record_to_compare):
                        return True
                    else:
                        return False
            else:
                to_compare = group.grouprecord_set.first()
                return self.satisfies_existing_group_condition(to_compare)

    def merge_with_group(self):
        """Try to find group that has at least one similar record. NEED SAVE IF RETURNED TRUE"""
        for group in Group.objects.all():
            if self.compare_with_group(group=group):
                self.group = group
                #self.save()
                return True
        return False

    def merge_with_group_and_save(self):
        """In mass updates use bulk update instead"""
        if self.merge_with_group():
            self.save()