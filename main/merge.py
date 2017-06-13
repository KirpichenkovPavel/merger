from main.models import Person, Hypostasis, GroupRecord, Group
from itertools import groupby, combinations
from datetime import date
from bulk_update.helper import bulk_update
from time import time


def create_new_groups(*args, **kwargs):
    """Puts records into new groups if they do not have one yet and can meld with one other

    Each record will have only one group (person) or none if it's alone.
    Predicate methods must contain one or more method names from GroupRecord class.
    Predicate methods must be defined and maintained in GroupRecord model.
    Call with "satisfies_new_group_condition" to form new groups.
    """

    def key_function(gr):
        """For sorting by birth date"""
        if gr.birth_date is None:
            return date.today()
        else:
            return gr.birth_date

    predicate_methods = kwargs.get('predicate_methods', ['satisfies_new_group_condition', 'not_forbidden'])
    if len(predicate_methods) == 0:
        raise AttributeError("Predicate methods must contain at least one method")
    print("Starting creation of new groups")
    print("Extracting records")
    key = key_function
    unresolved_records = list(GroupRecord.objects.filter(group__isnull=True))
    unresolved_records.sort(key=key)
    record_groups = []
    print("Sorting")
    for k, g in groupby(unresolved_records, key=key):
        record_groups.append(list(g))
    records_to_update = []
    groups_to_update = []
    print("Iterating through groups")
    cntr = 0
    total = len(record_groups)
    for same_date_group in record_groups:
        cntr += 1
        if cntr % 100 == 0:
            print("{} of {} date groups handled".format(cntr, total))
        new_groups = []
        for record_pair in combinations(same_date_group, 2):
            a = record_pair[0]
            b = record_pair[1]
            if a.check_predicates(predicate_methods=predicate_methods, another_record=b, **kwargs):
                a_in_group = False
                b_in_group = False
                new_group = None
                if a.group is not None and a.group in new_groups:
                    a_in_group = True
                    new_group = a.group
                if b.group is not None and b.group in new_groups:
                    b_in_group = True
                    new_group = b.group
                if new_group is None:
                    new_group = Group()
                    new_groups.append(new_group)
                    new_group.save()
                if not a_in_group:
                    a.group = new_group
                    records_to_update.append(a)
                if not b_in_group:
                    b.group = new_group
                    records_to_update.append(b)
        groups_to_update.extend(new_groups)
        for group in new_groups:
            for record in same_date_group:
                if record.group == group and record.birth_date is not None:
                    group.birth_date = record.birth_date
        bulk_update(new_groups, update_fields=['birth_date'])
    print("Have {0} records to save".format(len(records_to_update)))
    bulk_update(records_to_update, update_fields=['group'])
    print("Have {0} groups to update inconsistency".format(len(groups_to_update)))
    mark_inconsistency(groups_to_update)
    print("Creation of new groups: done")


def distribute_records_among_existing_groups(**kwargs):
    print("Starting distribution among existing groups")
    print("Extracting records")
    unresolved_records = list(GroupRecord.objects.filter(group__isnull=True))
    print("Making dictionary of groups")
    group_dict = Group.get_dictionary()
    if len(group_dict) == 0:
        print("No groups found. Finishing")
        return
    records_to_update = []
    groups_to_update = set()
    print("Handling records")
    ttl = len(unresolved_records)
    cntr = 0
    now = time()
    for record in unresolved_records:
        cntr += 1
        if cntr % 100 == 0:
            print("{} of {} records handled {}".format(cntr, ttl, time() - now))
            now = time()
        suitable_group = record.seek_for_group(group_dict, **kwargs)
        if suitable_group is not None:
            record.group = suitable_group
            records_to_update.append(record)
            groups_to_update.add(suitable_group)
    print("Have {0} records to update".format(len(records_to_update)))
    if len(records_to_update) > 0:
        bulk_update(records_to_update, update_fields=['group'])
    print("Have {0} groups to update".format(len(groups_to_update)))
    if len(groups_to_update) > 0:
        mark_inconsistency(groups=list(groups_to_update))
    print("Distribution among existing groups: done")


def mark_inconsistency(groups=None, group_dict=None):
    """Update inconsistency flag of chosen groups"""

    def check_group_consistency(group_record_list):
        """Returns True, if all records in list are fully equal"""
        first = group_record_list[0]
        for other in group_record_list[1:]:
            if not first.completely_equal_for_consistency(another_record=other):
                return False
        return True

    print("Starting procedure of inconsistency marking")
    if group_dict is None:
        print("Making dictionary of groups")
        group_dict = Group.get_dictionary()
    groups_to_update = set()
    print("Iterating through groups")
    if groups is None:
        groups = group_dict.keys()
    else:
        for group in groups:
            if not isinstance(group, Group):
                raise TypeError("groups must contain Group instances")
    for group in groups:
        records = group_dict[group]
        if check_group_consistency(group_record_list=records):
            if group.inconsistent:
                group.inconsistent = False
                groups_to_update.add(group)
        else:
            if not group.inconsistent:
                group.inconsistent = True
                groups_to_update.add(group)
    print("In-memory changes done")
    print("{} groups will be changed".format(len(groups_to_update)))
    bulk_update(list(groups_to_update), update_fields=['inconsistent'])
    print("Inconsistency marking: done")


def merge_consistent_groups(group_dict=None):
    print("Starting consistent groups merge")
    if group_dict is None:
        print("Extracting groups")
        group_dict = Group.get_dictionary()
    records_for_update = []
    hypostases_for_update = []
    groups_for_update = []
    persons_to_delete = set()

    print("Iterating")
    for group, records in group_dict.items():
        print(group.id)
        if not group.inconsistent and len(records) > 1:
            changed_records, changed_hypostases, unnecessary_persons = \
                records[0].merge_records_by_hypostases(records[1:], save=False)
            group.person = records[0].person
            groups_for_update.append(group)
            hypostases_for_update.extend(changed_hypostases)
            records_for_update.extend(changed_records)
            persons_to_delete = persons_to_delete.union(unnecessary_persons)
    print("Saving")
    bulk_update(records_for_update, update_fields=['person'])
    bulk_update(hypostases_for_update, update_fields=['person'])
    bulk_update(list(group_dict.keys()), update_fields=['person'])
    for person in persons_to_delete:
        person.delete()
    print("Consistent groups merge: done")


def full_update():
    """At first compares orphan records with existing groups. Then tries to make new groups from remaining records."""
    print("Starting full update")
    start = time()
    distribute_records_among_existing_groups()
    distribute = time()
    create_new_groups()
    end = time()
    print("{} seconds for distribution\n{} seconds for creation".format(distribute - start, end - distribute))
