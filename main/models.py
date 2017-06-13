from django.db import models
from main_remote.models import Student, Employee, Postgraduate
from bulk_update.helper import bulk_update
from main.exceptions import HypostasisIntegrityError, GroupError
from cached_property import cached_property_ttl
from inspect import getmembers, ismethod
from jellyfish import jaro_winkler, levenshtein_distance
from itertools import combinations
from main.decorators import predicate


class Person(models.Model):
    """Person as a unique object"""

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

    def __str__(self):
        return "{0} {1} {2}".format(self.last_name, self.first_name, self.middle_name)


class Hypostasis(models.Model):
    """One part of the person's activity: student, employee or postgraduate."""

    employee_id = models.CharField(max_length=255, unique=True, null=True)
    student_id = models.IntegerField(unique=True, null=True)
    postgraduate_id = models.IntegerField(unique=True, null=True)
    person = models.ForeignKey(Person, null=True, on_delete=models.SET_NULL)

    HYPOSTASIS_CACHE_TTL = 300

    def __str__(self):
        instance = self.non_empty_instance
        st = str(type(instance)).split(".")[-1].split("'")[0] + " " + str(instance)
        return st

    @cached_property_ttl(ttl=HYPOSTASIS_CACHE_TTL)
    def _instance_type(self):
        """Returns one of the following strings: student, postgraduate or employee.

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

        remote_model = self.remote_class
        nonempty_id = self.non_empty_id
        return remote_model.objects.get(pk=nonempty_id)

    def handle_as_new(self, group_dict=None):
        remote_instance = self.non_empty_instance
        last_name = remote_instance.last_name
        first_name = remote_instance.first_name
        middle_name = remote_instance.middle_name
        birth_date = remote_instance.date_birth
        if self.person is None:
            person = Person(last_name=last_name,
                            first_name=first_name,
                            middle_name=middle_name,
                            birth_date=birth_date)
            person.save()
            self.person = person
            self.save()
        else:
            person = self.person
        num_of_records = self.grouprecord_set.count()
        if num_of_records == 0:
            record = GroupRecord(last_name=last_name,
                                 first_name=first_name,
                                 middle_name=middle_name,
                                 birth_date=birth_date,
                                 person=person,
                                 hypostasis=self,
                                 group=None)
            record.save()
        elif num_of_records > 1:
            raise HypostasisIntegrityError("No more than one record should reference hypostasis. Found: {}". \
                                           format(num_of_records))
        else:
            record = self.grouprecord_set.get()
        group = record.seek_for_group_and_save(group_dict=group_dict)
        if not group:
            group = record.seek_to_make_new_group(predicate_methods=['has_equal_date',
                                                                     'satisfies_new_group_condition',
                                                                     'not_forbidden'])
        if group is not None:
            group.update_consistency()


class Group(models.Model):
    inconsistent = models.BooleanField(default=False)
    birth_date = models.DateField(null=True)
    person = models.ForeignKey(Person, null=True, on_delete=models.CASCADE)

    @staticmethod
    def get_dictionary():
        return {group: list(group.grouprecord_set.all()) for group in Group.objects.all()}

    def update_consistency(self):
        records = list(self.grouprecord_set.all())
        if len(records) > 1:
            first = records.pop(0)
            for record in records:
                if not first.completely_equal_for_consistency(another_record=record):
                    self.inconsistent = True
                    self.save()
                    return
            self.inconsistent = False
            self.save()

    @property
    def is_merged(self):
        if self.person is None:
            return False
        else:
            for record in self.grouprecord_set.all():
                if record.person != self.person:
                    return False
            return True

    def unmake(self, search=True, group_dict=None, **kwargs):
        """Split all records in this group and delete it. Can't be done for partially merged groups."""
        if self.person is not None:
            raise GroupError("Can't split group, if its part was previously merged")
        records = list(self.grouprecord_set.all()) if not group_dict else group_dict[self]
        for rec1, rec2 in combinations(records, 2):
            rec1.forbidden_group_records.add(rec2)
            rec2.forbidden_group_records.add(rec1)
        if group_dict:
            group_dict.pop(self)
        if search:
            if group_dict is None:
                group_dict = Group.get_dictionary()
            for record in records:
                record.group = None
                new_group = record.seek_for_group(group_dict=group_dict, **kwargs)
                if new_group:
                    record.group = new_group
                else:
                    new_group = record.seek_to_make_new_group(**kwargs)
                    if new_group:
                        record.group = new_group
                if new_group:
                    group_dict[new_group].append(record)
        bulk_update(records)
        self.delete()

    def merge(self):
        """Unite all records in this group so they and their related hypostases reference one person."""
        records = list(self.grouprecord_set.all())
        if self.person is None:
            first = records.pop(0)
        else:
            first = list(filter(lambda item: item.person == self.person, records))[0]
            records.remove(first)
        if len(records) > 0:
            first.merge_records_by_hypostases(records, save=True)
            self.person = first.person
            self.save()


class GroupRecord(models.Model):
    """ Records for pre-merge groups

    Records reference group they belong to.
    No reference to group means either absence of search or no matching records with this one.
    Record may belong to up to one group.
    Created groups may be joined, but neither groups nor records will be deleted in this process.
    To merge records in group is to make them reference the same person, same for their hypostases.
    Record must duplicate data in related hypostasis (reference to person) and its remote instance (other fields).
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
    # Set of method names, shared among instances. Used in _call_predicate as a cache.
    __predicate_methods = set()

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.last_name, self.first_name, self.middle_name, self.birth_date)

    def _call_predicate(self, method_name, **kwargs):
        """Executes method with chosen name if it is a predicate method. Decorate with @predicate to use method here."""
        if method_name in self.__predicate_methods:
            # Method name has been checked already.
            return getattr(self, method_name)(**kwargs)
        else:
            names = [tup[0] for tup in getmembers(self, predicate=ismethod)]
            if method_name not in names:
                raise AttributeError("{} is not a method of GroupRecord".format(method_name))
            else:
                method = getattr(self, method_name)
                if getattr(method, "_is_a_predicate_method", False):
                    self.__predicate_methods.add(method_name)
                    return method(**kwargs)
                else:
                    raise AttributeError("{} is not an allowed predicate method".format(method_name))

    def _compare_attribute(self, another_record, attribute, another_attribute=None, empty_values_work=True):
        if another_attribute is None:
            another_attribute = attribute
        a1 = getattr(self, attribute)
        a2 = getattr(another_record, another_attribute)
        if empty_values_work:
            if a1 is None or a2 is None:
                return True
            if isinstance(a1, str) and isinstance(a2, str):
                if len(a1) == 0 or len(a2) == 0:
                    return True
        if a1 == a2:
            return True
        else:
            return False

    def _compare_attributes(self, another_record, attribute_list, empty_values_work=True):
        for attribute in attribute_list:
            if not self._compare_attribute(another_record=another_record, attribute=attribute,
                                           empty_values_work=empty_values_work):
                return False
        return True

    def check_predicates(self, **kwargs):
        """Returns True only if all predicates return True

        Keywords are used in predicates to change their default behavior.
        Because of that different predicates must name independent arguments differently.
        Look at the required method to know if it uses any arguments.
        The only obligatory argument is "predicate_methods", which must be an iterable of method names.
        """
        predicate_methods = kwargs.get('predicate_methods', None)
        if predicate_methods is None:
            raise AttributeError('You must pass names of predicates as a keyword argument method_names (iterable)')
        for predicate_name in predicate_methods:
            if not self._call_predicate(predicate_name, **kwargs):
                return False
        return True

    @predicate
    def completely_equal_for_search(self, *, another_record, **kwargs):
        attributes = ['last_name', 'first_name', 'middle_name', 'birth_date']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes)

    @predicate
    def completely_equal_for_consistency(self, *, another_record, **kwargs):
        attributes = ['last_name', 'first_name', 'middle_name', 'birth_date']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes,
                                        empty_values_work=False)

    @predicate
    def has_equal_full_name(self, *, another_record, **kwargs):
        attributes = ['last_name', 'first_name', 'middle_name']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes)

    @predicate
    def has_equal_last_name(self, *, another_record, **kwargs):
        return self._compare_attribute(another_record=another_record, attribute='last_name')

    @predicate
    def has_equal_first_name(self, *, another_record, **kwargs):
        return self._compare_attribute(another_record=another_record, attribute='first_name')

    @predicate
    def has_equal_middle_name(self, *, another_record, **kwargs):
        return self._compare_attribute(another_record=another_record, attribute='middle_name')

    @predicate
    def has_equal_date(self, *, another_record, **kwargs):
        return self._compare_attribute(another_record=another_record, attribute='birth_date')

    @predicate
    def has_equal_first_and_middle_name(self, *, another_record, **kwargs):
        attributes = ['first_name', 'middle_name']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes)

    @predicate
    def has_equal_last_and_middle_name(self, *, another_record, **kwargs):
        attributes = ['last_name', 'middle_name']
        return self._compare_attributes(another_record=another_record, attribute_list=attributes)

    @predicate
    def close_by_fuzzy_metric(self, *, another_record,  attribute, tolerance=None, **kwargs):
        """Checks that all attributes except chosen are equal and the chosen one is close enough"""
        default_tolerance = 0.86
        attributes = ['last_name', 'first_name', 'middle_name']
        if attribute not in attributes:
            raise AttributeError('{} is a wrong attribute'.format(attribute))
        else:
            if tolerance is None:
                tolerance = default_tolerance
            attributes.remove(attribute)
            if self._compare_attributes(another_record, attributes):
                str1 = getattr(self, attribute)
                str2 = getattr(another_record, attribute)
                if str1 is None or str2 is None:
                    return True
                elif (levenshtein_distance(str1, str2) == 1) or (jaro_winkler(str1, str2) > tolerance):
                    return True
            return False

    @predicate
    def not_forbidden(self, *, another_record, **kwargs):
        return another_record not in self.forbidden_group_records.all()

    @predicate
    def satisfies_new_group_condition(self, *, another_record, tolerance=None, **kwargs):
        """No date check, use only in groups with equal date"""
        return self.close_by_fuzzy_metric(another_record=another_record, attribute='first_name', tolerance=tolerance) or \
               self.close_by_fuzzy_metric(another_record=another_record, attribute='last_name', tolerance=tolerance) or \
               self.close_by_fuzzy_metric(another_record=another_record, attribute='middle_name', tolerance=tolerance)

    @predicate
    def satisfies_existing_group_condition(self, *, another_record, tolerance=None, **kwargs):
        if self.has_equal_date(another_record=another_record):
            return self.satisfies_new_group_condition(another_recsord=another_record, tolerance=tolerance)

    def compare_with_list(self, record_list, **kwargs):
        """ Full check with all records in list. Intended for inconsistent groups."""
        if self.group is not None:
            raise AttributeError('Group record should not have a group yet')
        else:
            predicate_methods = kwargs.pop('predicate_methods', ['satisfies_new_group_condition', 'not_forbidden'])
            for record_to_compare in record_list:
                if self.check_predicates(predicate_methods=predicate_methods, another_record=record_to_compare,
                                         **kwargs):
                    return True
            return False

    def seek_for_group(self, group_dict, **kwargs):
        """In group_dict key must be a group and value must be a list of records"""

        def filter_function(item):
            d1 = item.birth_date
            d2 = self.birth_date
            return d1 == d2 if (d1 is not None and d2 is not None) else True

        predicate_methods = kwargs.pop('predicate_methods', ['satisfies_new_group_condition', 'not_forbidden'])
        filtered_keys = list(filter(filter_function, group_dict.keys()))
        for group in filtered_keys:
            if group in self.forbidden_groups.all():
                continue
            if len(group_dict[group]) < 2:
                raise GroupError("Group (id={}) with less than 2 records is incorrect".format(group.id))
            if group.inconsistent:
                if self.compare_with_list(record_list=group_dict[group], predicate_methods=predicate_methods, **kwargs):
                    return group
            else:
                if self.check_predicates(predicate_methods=predicate_methods,
                                         another_record=group_dict[group][0],
                                         **kwargs):
                    return group

    def seek_for_group_and_save(self, group_dict, **kwargs):
        """In mass updates use bulk update instead"""
        predicate_methods = kwargs.get('predicate_methods', ['satisfies_new_group_condition', 'not_forbidden'])
        suitable_group = self.seek_for_group(group_dict=group_dict, predicate_methods=predicate_methods, **kwargs)
        if suitable_group is not None:
            if self.group:
                group_dict[self.group].remove(self)
            self.group = suitable_group
            self.save()
            group_dict[suitable_group].append(self)
            return suitable_group

    def seek_to_make_new_group(self, group_dict=None, **kwargs):
        """Seek for record to merge. Make a new group if record exists. Return the new Group or None"""
        predicate_methods = kwargs.pop('predicate_methods',
                                       ['has_equal_date', 'satisfies_new_group_condition', 'not_forbidden'])
        group = None
        for record in GroupRecord.objects.filter(group__isnull=True):
            if self.check_predicates(predicate_methods=predicate_methods, another_record=record, **kwargs) \
                            and record != self:
                if not group:
                    group = Group(birth_date=self.birth_date)
                    group.save()
                    self.group = group
                    self.save()
                    if group_dict:
                        group_dict[group] = [self]
                record.group = group
                record.save()
                if group_dict:
                    group_dict[group].append(record)
        return group

    def merge_records_by_hypostases(self, other_records, save=True):
        """Unite all records and related hypostases around this record's person.

        This record's person becomes the person referensed by other records and their related hypostases.
        All empty persons (not referenced by any hypostases) are removed.
        No checks about group being made assuming this checks were done more efficiently, when
        this group was created."""
        hypostases_for_update = []
        records_for_update = []
        persons_to_delete = set()
        for record in other_records:
            previous_person = record.person
            if previous_person == self.person:
                continue
            persons_to_delete.add(previous_person)
            record.hypostasis.person = self.person
            record.person = self.person
            hypostases_for_update.append(record.hypostasis)
            records_for_update.append(record)
        if self.person in persons_to_delete:
            persons_to_delete.remove(self.person)
        for person in list(persons_to_delete):
            for hypostasis in person.hypostasis_set.all():
                if hypostasis not in hypostases_for_update:
                    persons_to_delete.remove(person)
        if save:
            bulk_update(records_for_update, update_fields=['person'])
            bulk_update(hypostases_for_update, update_fields=['person'])
            for person in persons_to_delete:
                person.delete()
        else:
            return records_for_update, hypostases_for_update, persons_to_delete

    def merge_records_by_persons(self, other_records, save=True):
        """This merge also updates related records from the other groups if they have reference to the same person."""
        persons_to_delete = set()
        hypostases_for_update = []
        records_for_update = []
        new_group = self.group
        new_person = self.person
        for record in other_records:
            persons_to_delete.add(record.person)
        if new_person in persons_to_delete:
            persons_to_delete.remove(new_person)
        for person in persons_to_delete:
            hypostases_for_update.extend(person.hypostasis_set.all())
            records_for_update.extend(person.grouprecord_set.all())
        for record in records_for_update:
            record.group = new_group
            record.person = new_person
        for hypostasis in hypostases_for_update:
            hypostasis.person = new_person
        if save:
            bulk_update(hypostases_for_update, update_fields=['person'])
            bulk_update(records_for_update, update_fields=['person', 'group'])
            for person in persons_to_delete:
                person.delete()
        else:
            return records_for_update, hypostases_for_update, persons_to_delete

    def remove_from_group(self, search=True, group_dict=None):
        """Add group to the forbidden and check for new groups"""
        if self.group is not None:
            if self.group.grouprecord_set.count() == 2:
                raise GroupError("Group can't contain less than 2 records. Delete the whole group instead.")
            if self.person == self.group.person:
                raise GroupError("Can't remove merged person from group")
            if search and group_dict is None:
                group_dict = Group.get_dictionary()
            self.forbidden_groups.add(self.group)
            forbidden_group = self.group
            self.group = None
            self.save()
            if forbidden_group.inconsistent:
                forbidden_group.update_consistency()
            if search:
                group_dict[forbidden_group].remove(self)
                new_group = self.seek_for_group_and_save(group_dict)
                if new_group:
                    new_group.update_consistency()
                else:
                    new_group = self.seek_to_make_new_group(
                        predicate_methods=['has_equal_date', 'satisfies_new_group_condition', 'not_forbidden'])
                    if new_group:
                        new_group.update_consistency()

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
        else:
            raise AttributeError('The group is not forbidden for this record')
