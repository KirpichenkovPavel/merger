from django.db import models
from main_remote.models import Student, Employee, Postgraduate
from collections import Counter
from bulk_update.helper import bulk_update
from main.exceptions import HypostasisIntegrityError
from cached_property import cached_property, cached_property_ttl
from merger.local_settings import HYPOSTASIS_CACHE_TTL
from inspect import getmembers, ismethod
from jellyfish import jaro_winkler, levenshtein_distance
from itertools import combinations
from main.decorators import check_forbidden_records
from django.utils.decorators import method_decorator


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
        """Merge persons in the list with the first peson. OUT OF DATE. DOES NOT CONSIDER GROUP RECORDS"""
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
            if not isinstance(attribute, str):
                raise TypeError("{0} is not a string.".format(attribute))
            attributes[attribute].update(
                [getattr(x.get_non_empty_instance(), attribute) for x in list(self.hypostasis_set.all())])
        return attributes

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
        return {group: list(group.grouprecord_set.all()) for group in Group.objects.all()}

    def update_consistency(self):
        records = list(self.group_record_set.all())
        if len(records) > 1:
            first = records[0]
            others = records[1:]
            for record in others:
                if not first.completely_equal(record):
                    self.inconsistent = True
                    self.save()
                    return
            self.inconsistent = False
            self.save()

    def unmake(self):
        """Split all records in group and delete it"""
        records = list(self.grouprecord_set.all())
        for rec1, rec2 in combinations(records, 2):
            rec1.forbidden_group_records.add(rec2)
            rec2.forbidden_group_records.add(rec1)
        bulk_update(records, update_fields=['forbidden_group_records'])
        self.delete()


class GroupRecord(models.Model):
    """Записи для предварительного объединения в группы

    Объединение ведется по указанным в записях группам.
    Если группа не указана, для записи пока не найдено группы.
    Запись не может одновременно находиться в нескольких группах. Возможно, есть случаи, когда это будет неверно,
    но с концептуальной точки зрения запись может относиться только к одному человеку.
    Объединение в Person проводится на основании сформированных групп, после объединения записи не удаляются.
    Объединение заключается в перекидывании ссылок на персону в записи и связанной ипостаси.
    Каждой записи соответствует ипостась, необходимо поддержание целостности: ссылки на персону в записи и ипостаси
    должны совпадать, данные в записи и в связанной с ипостасью сущности должны быть одинаковыми.
    """
    hypostasis = models.ForeignKey(Hypostasis, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(Group, null=True, on_delete=models.SET_NULL)
    last_name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True)
    birth_date = models.DateField(null=True)
    forbidden_groups = models.ManyToManyField(Group, related_name='forbidden_group_record_set')
    forbidden_group_records = models.ManyToManyField("self")

    PREDICATE_METHODS = ["completely_equal", "has_equal_full_name", "has_equal_first_and_middle_name", "has_equal_date",
                         "has_equal_last_and_middle_name", "satisfies_new_group_condition", "has_equal_last_name",
                         "has_equal_first_name", "has_equal_middle_name", "satisfies_existing_group_condition",
                         "close_by_fuzzy_metric", "forbidden"]

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.last_name, self.first_name, self.middle_name, self.birth_date)

    def _call_method(self, method_name, *args, **kwargs):
        names = [tup[0] for tup in getmembers(self, predicate=ismethod)]
        if method_name not in names:
            raise AttributeError("{} is not a method of GroupRecord".format(method_name))
        else:
            method = getattr(self, method_name)
            return method(*args, **kwargs)

    def _compare_attribute(self, another_record, attribute, another_attribute=None):
        if another_attribute is None:
            another_attribute = attribute
        if getattr(self, attribute) == getattr(another_record, another_attribute):
            return True
        else:
            return False

    def _compare_attributes(self, another_record, attribute_list):
        for attribute in attribute_list:
            if not self._compare_attribute(another_record=another_record, attribute=attribute):
                return False
        return True

    def check_predicates(self, predicate_methods, *args, **kwargs):
        """Returns True only if all predicates return True"""
        for predicate in predicate_methods:
            if predicate not in GroupRecord.PREDICATE_METHODS:
                raise AttributeError("{} is not an allowed predicate method")
        for predicate in predicate_methods:
            if not self._call_method(predicate, *args, **kwargs):
                return False
        return True

    def completely_equal(self, another_record):
        attributes = ['last_name', 'first_name', 'middle_name', 'birth_date']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_full_name(self, another_record):
        attributes = ['last_name', 'first_name', 'middle_name']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_last_name(self, another_record):
        return self._compare_attribute(another_record=another_record, attribute='last_name')

    def has_equal_first_name(self, another_record):
        return self._compare_attribute(another_record=another_record, attribute='first_name')

    def has_equal_middle_name(self, another_record):
        return self._compare_attribute(another_record=another_record, attribute='middle_name')

    def has_equal_date(self, another_record):
        return self._compare_attribute(another_record=another_record, attribute='birth_date')

    def has_equal_first_and_middle_name(self, another_record):
        attributes = ['first_name', 'middle_name']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes)

    def has_equal_last_and_middle_name(self, another_record):
        attributes = ['last_name', 'middle_name']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes)

    def close_by_fuzzy_metric(self, another_record, attribute, tolerance=0.86):
        """Checks that all attributes except chosen are equal and the chosen one is close enough"""
        attributes = ['last_name', 'first_name', 'middle_name']
        if attribute not in attributes:
            raise AttributeError('{} is a wrong attribute'.format(attribute))
        else:
            attributes.remove(attribute)
            attributes.append('birth_date')
            if self._compare_attributes(another_record, attributes):
                str1 = getattr(self, attribute)
                str2 = getattr(another_record, attribute)
                if str1 is None or str2 is None:
                    return True
                elif (levenshtein_distance(str1, str2) == 1) or (jaro_winkler(str1, str2) > tolerance):
                    return True
            return False

    def forbidden(self, another_record):
        return another_record in self.forbidden_group_records.all()

    def satisfies_new_group_condition(self, another_record):
        """No date check, used only in sorted-by-dates groups"""
        return self.close_by_fuzzy_metric(another_record, 'first_name') or \
                self.close_by_fuzzy_metric(another_record, 'last_name') or \
                self.close_by_fuzzy_metric(another_record, 'middle_name')

    def satisfies_existing_group_condition(self, another_record):
        return self.check_predicates(['has_equal_dates', 'satisfies_new_group_condition'], another_record)
        # if self.has_equal_date(another_record):
        #     if self.satisfies_new_group_condition(another_record):
        #         return True
        # else:
        #     return False

    def compare_with_list(self, record_list):
        """ Full check with all records in list. Intended for inconsistent groups."""
        if self.group is not None:
            raise AttributeError('Group record should not have group yet')
        else:
            for record_to_compare in record_list:
                if self.forbidden(record_to_compare):
                    return False
                elif self.satisfies_existing_group_condition(record_to_compare):
                    return True
            return False

    def seek_for_group(self, group_dict):
        """In group_dict key must be group and value must be list of records"""
        for group in group_dict:
            if group in self.forbidden_groups.all():
                continue
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

    # def find_group_from_base(self):
    #     """No need to use - no advantages in speed compared to dict variant"""
    #     for group in list(Group.objects.all()):
    #         related_records = list(group.grouprecord_set.all())
    #         if group.inconsistent:
    #             if self.compare_with_list(related_records):
    #                 return group
    #         else:
    #             if self.satisfies_existing_group_condition(related_records[0]):
    #                 return group

    def merge_records_by_hypostases(self, other_records, save=True):
        """Unite all records and related hypostases around this record's person.

        This record's person becomes the person referensed by other records and their related hypostases.
        All empty persons (not referenced by any hypostases) are removed.
        No checks about group being made assuming this checks are already done more efficiently, when
        this group was created."""
        hypostases_to_update = []
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

    def make_new_group(self, predicate_methods=None):
        """Seek for record to merge. Make new group if record exists. Return new Group or None"""
        if predicate_methods is None:
            predicate_methods = ['has_equal_date', 'satisfies_new_group_condition']
        for record in GroupRecord.objects.filter(group__isnull=True):
            if self.check_predicates(predicate_methods, record):
                g = Group()
                g.save()
                record.group = g
                self.group = g
                record.save()
                self.save()
                return g

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

    def remove_from_group(self, group_dict=None):
        """Add group to forbidden and check for new groups"""
        if group_dict is None:
            group_dict = Group.get_groups_dict()
        if self.group is not None:
            self.forbidden_groups.add(self.group)
            self.group = None
            self.save(update_fields=['group', 'forbidden_groups'])
            if self.seek_for_group_and_save(group_dict) is None:
                self.make_new_group(predicate_methods=['has_equal_date', 'satisfies_new_group_condition'])

    def remove_record_from_forbidden(self, another_record):
        """Remove another record from this record's forbidden records list and vice versa"""
        if not isinstance(another_record, GroupRecord):
            raise TypeError('{} is not a GroupRecord instance'.format(another_record))
        if another_record in self.forbidden_group_records.all():
            self.forbidden_group_records.remove(another_record)
            another_record.forbidden_group_records.remove(self)
            self.save()
            another_record.save()
        else:
            raise AttributeError('GroupRecord {} is not forbidden for this record'.format(another_record))

    def remove_group_from_forbidden(self, group):
        """Remove group from this record's restricted groups list"""
        if not isinstance(group, Group):
            raise AttributeError('{} is not a Group instance'.format(group))
        if group in self.forbidden_groups.all():
            self.forbidden_groups.remove(group)
            self.save()
