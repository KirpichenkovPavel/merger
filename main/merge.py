from main.models import Person, Hypostasis, GroupRecord, Group
from itertools import groupby, combinations
from datetime import date
from bulk_update.helper import bulk_update


def create_new_groups(*, predicate_methods=None):
    """Puts records into new groups if they do not have one yet and can meld with one other

    Each record will have only one group (person) or none if it's alone.
    Predicate methods must contain one or more method names from GroupRecord class.
    Predicate methods must be defined and maintained in Group.PREDICATE_METHODS attribute.
    Call with "satisfies_new_group_condition" to form new groups.
    More flexible methods may appear later.
    """

    def key_function(gr):
        """For sorting by birth date"""
        if gr.birth_date is None:
            return date.today()
        else:
            return gr.birth_date
    if predicate_methods is None:
        predicate_methods = ['satisfies_new_group_condition']
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
        if cntr % 1000 == 0:
            print("{} of {} date groups handled".format(cntr, total))
        new_groups = []
        for record_pair in combinations(same_date_group, 2):
            a = record_pair[0]
            b = record_pair[1]
            if a.check_predicates(predicate_methods, b):
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
    print("Have {0} records to save".format(len(records_to_update)))
    bulk_update(records_to_update, update_fields=['group'])
    print("Have {0} groups to update inconsistency".format(len(groups_to_update)))
    mark_inconsistency(groups_to_update)
    bulk_update(groups_to_update, update_fields=['inconsistent'])
    print("Creation of new groups: done")


def distribute_records_among_existing_groups():
    print("Starting distribution among existing groups")
    print("Extracting records")
    unresolved_records = list(GroupRecord.objects.filter(group__isnull=True))
    print("Making dictionary of groups")
    groups_dict = Group.get_groups_dict()
    records_to_update = []
    groups_to_update = set()
    print("Handling records")
    ttl = len(unresolved_records)
    cntr = 0
    for record in unresolved_records:
        cntr += 1
        if cntr % 1000 == 0:
            print("{} of {} records handled".format(cntr, ttl))
        suitable_group = record.seek_for_group(groups_dict)
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
        bulk_update(list(groups_to_update), update_fields=['inconsistent'])
    print("Distribution among existing groups: done")


def check_group_consistency(group_record_list):
    """Returns True, if all records in list are fully equal"""
    first = group_record_list[0]
    for other in group_record_list[1:]:
        if not first.completely_equal_for_consistency(other):
            return False
    return True


def mark_inconsistency(groups=None, groups_dict=None):
    """Update inconsistency flag of chosen groups"""
    print("Starting procedure of inconsistency marking")
    if groups_dict is None:
        print("Making dictionary of groups")
        groups_dict = Group.get_groups_dict()
    groups_to_update = set()
    print("Iterating through groups")
    if groups is None:
        groups = groups_dict.keys()
    else:
        for group in groups:
            if not isinstance(group, Group):
                raise TypeError("groups must contain Group instances")
    for group in groups:
        records = groups_dict[group]
        if check_group_consistency(records):
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


def merge_consistent_groups(groups_dict=None):
    print("Starting consistent groups merge")
    if groups_dict is None:
        print("Extracting groups")
        groups_dict = Group.get_groups_dict()
    records_for_update = []
    hypostases_for_update = []
    persons_to_delete = set()
    print("Iterating")
    for group, records in groups_dict.items():
        print(group.id)
        if not group.inconsistent and len(records) > 1:
            changed_hypos, unnecessary_persons = records[0].merge_records_by_hypostases(records[1:], save=False)
            hypostases_for_update.extend(changed_hypos) if len(changed_hypos) > 0 else None
            records_for_update.extend(records[1:])
            persons_to_delete = persons_to_delete.union(unnecessary_persons)
    print("Saving")
    bulk_update(records_for_update, update_fields=['person'])
    bulk_update(hypostases_for_update, update_fields=['person'])
    for person in persons_to_delete:
        person.delete()
    print("Consistent groups merge: done")


def full_update():
    """At first compares orphan records with existing groups. Then tries to make new groups from remaining records."""
    print("Starting full update")
    distribute_records_among_existing_groups()
    create_new_groups()
