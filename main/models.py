from django.db import models
from main_remote.models import Student, Employee, Postgraduate
from collections import namedtuple, Counter
from bulk_update.helper import bulk_update
from main.exceptions import HypostasisIntegrityError
from cached_property import cached_property, cached_property_ttl
from merger.local_settings import HYPOSTASIS_CACHE_TTL
from inspect import getmembers, ismethod


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
        """Get instance (remote object) with the latest valid_to date in related object."""

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
        instances = [x.non_empty_instance for x in hypos_list]
        return latest_instance(instances)

    def get_actual_hypostasis(self):
        """Get hypostasis with the latest date for this person"""
        instance = self.get_actual_instance()
        for hypostasis in self.hypostasis_set.all():
            if hypostasis.non_empty_instance == instance:
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

    def check_pre_merge(self, person, **kwargs):
        """Check equivalence with another person and return metric."""
        return 100


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
    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        # from main.merge import get_instance_from_hypostasis
        instance = self.non_empty_instance
        st = str(type(instance)).split(".")[-1].split("'")[0] + " " + str(instance)
        return st

    @cached_property_ttl(ttl=HYPOSTASIS_CACHE_TTL)
    def _instance_type(self):
        """Returns one of the following strings: student, postgraduate or employee

        Raises HypostasisIntegrityError either if all ids are empty or if more than one is not empty
        """

        if self.student_id is not None:
            if self.employee_id is not None or self.postgraduate_id is not None:
                raise HypostasisIntegrityError("More than one non-empty id of related object")
            return "student"
        elif self.postgraduate_id is not None:
            if self.employee_id is not None:
                raise HypostasisIntegrityError("More than one non-empty id of related object")
            return "postgraduate"
        elif self.employee_id is not None:
            return "employee"
        else:
            raise HypostasisIntegrityError("All ids in hypostasis are empty")

    @cached_property_ttl(ttl=HYPOSTASIS_CACHE_TTL)
    def remote_class(self):
        """One of the remote model class objects: Hypostasis, Student or Postgraduate"""
        return eval(self._instance_type.capitalize())

    @cached_property_ttl(ttl=HYPOSTASIS_CACHE_TTL)
    def non_empty_id(self):
        return getattr(self, self._instance_type + "_id")

    @cached_property_ttl(ttl=HYPOSTASIS_CACHE_TTL)
    def non_empty_instance(self):
        """Returns related remote instance"""

        class_name = self.remote_class
        nonempty_id = self.non_empty_id
        return class_name.objects.get(pk=nonempty_id)


class Group(models.Model):
    inconsistent = models.BooleanField(default=False)

    @staticmethod
    def get_groups_dict():
        return {group: list(group.group_record_set.all()) for group in Group.objects.all()}


class GroupRecord(models.Model):
    """"""

    hypostasis = models.ForeignKey(Hypostasis)
    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(Group, null=True, related_name='group_record_set')
    last_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True)
    birth_date = models.DateField(null=True)

    PREDICATE_METHODS = ["completely_equal", "has_equal_full_name", "has_equal_first_and_middle_name", "has_equal_date",
                         "has_equal_last_and_middle_name", "satisfies_new_group_condition",
                         "satisfies_existing_group_condition"]

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.last_name, self.first_name, self.middle_name, self.birth_date)

    def call_method(self, method_name, *args, **kwargs):
        names = [tup[0] for tup in getmembers(self, predicate=ismethod)]
        if method_name not in names:
            raise AttributeError("{} is not a method of GroupRecord".format(method_name))
        else:
            method = getattr(self, method_name)
            return method(*args, **kwargs)

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

    def check_predicates(self, another_record, predicate_methods):
        """Returns True only if all predicates return True"""
        for predicate in predicate_methods:
            if predicate not in GroupRecord.PREDICATE_METHODS:
                raise AttributeError("{} is not an allowed predicate method")
        for predicate in predicate_methods:
            if not self.call_method(predicate, another_record):
                return False
        return True

    def completely_equal(self, another_record):
        attributes = ['last_name', 'first_name', 'middle_name', 'birth_date']
        return self.compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_full_name(self, another_record):
        attributes = ['last_name', 'first_name', 'middle_name']
        return self.compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_first_and_middle_name(self, another_record):
        attributes = ['first_name', 'middle_name']
        return self.compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_date(self, another_record):
        return self.compare_attribute(another_record=another_record, attribute='birth_date')

    def has_equal_last_and_middle_name(self, another_record):
        attributes = ['last_name', 'middle_name']
        return self.compare_attributes(another_record=another_record, attribute_list=attributes)

    def satisfies_new_group_condition(self, another_record):
        """No date check, used only in sorted-by-dates groups"""
        return self.has_equal_full_name(another_record) or self.has_equal_last_and_middle_name(another_record) or self.has_equal_first_and_middle_name(another_record)

    def satisfies_existing_group_condition(self, another_record):
        if self.has_equal_date(another_record):
            if self.satisfies_new_group_condition(another_record):
                return True
        else:
            return False

    def compare_with_list(self, record_list):
        """ Full check with all records in list. Intended for inconsistent groups."""
        if self.group is not None:
            raise AttributeError('group record should not have group yet')
        else:
            for record_to_compare in record_list:
                if self.satisfies_existing_group_condition(record_to_compare):
                    return True
            return False

    def seek_for_group(self, group_dict):
        """In group_dict key must be group and value must be list of records"""
        for group in group_dict:
            if group.inconsistent:
                if self.compare_with_list(group_dict[group]):
                    return group
            else:
                if self.satisfies_existing_group_condition(group_dict[group][0]):
                    return group

    def seek_for_group_and_save(self, group_dict):
        """In mass updates use bulk update instead"""
        suitable_group = self.seek_for_group(group_dict)
        if suitable_group is not None:
            self.group = suitable_group
            self.save()
            return suitable_group

    def find_group_from_base(self):
        """No need to use - no advantages in speed compared to dict variant"""
        for group in list(Group.objects.all()):
            related_records = list(group.grouprecord_set.all())
            if group.inconsistent:
                if self.compare_with_list(related_records):
                    return group
            else:
                if self.satisfies_existing_group_condition(related_records[0]):
                    return group

    def merge_records_by_hypostases(self, other_records, save=True):
        """No checks about group being made assuming this checks are already done more efficiently."""
        hypostases_to_update = []
        if save:
            records_to_update = []
        for record in other_records:
            previous_person = record.hypostasis.person
            if previous_person == self.person:
                continue
            amount = previous_person.hypostasis_set.count()
            record.hypostasis.person = self.person
            hypostases_to_update.append(record.hypostasis)
            record.person = self.person
            if amount < 2:
                previous_person.delete()
            if save:
                records_to_update.append(record)
        if save:
            bulk_update(records_to_update, update_fields=['person'])
            bulk_update(hypostases_to_update, update_fields=['person'])
        else:
            return hypostases_to_update

    def merge_records_by_persons(self, other_records, save=True):
        """This merge also updates related records from other groups if they have reference to the same person.

        May be strange, slow and generally wrong"""
        persons = set()
        hypostases = []
        records = []
        new_group = self.group
        new_person = self.person
        for record in other_records:
            persons.add(record.person)
        if new_person in persons:
            persons.remove(new_person)
        for person in persons:
            hypostases.extend(person.hypostasis_set.all())
            records.extend(person.grouprecord_set.all())
        for record in records:
            record.group = new_group
            record.person = new_person
        for hypostasis in hypostases:
            hypostasis.person = new_person
        bulk_update(hypostases, update_fields=['person'])
        if save:
            bulk_update(records, update_fields=['person', 'group'])
        for person in persons:
            person.delete()