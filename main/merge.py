from main.models import Person, Hypostasis, GroupRecord, Group
from itertools import groupby, combinations
from datetime import date
from bulk_update.helper import bulk_update


# def get_names_dict():
#     names = {}
#     for person in list(Person.objects.all()):
#         key = " ".join((person.last_name,
#                         person.first_name,
#                         person.middle_name,
#                         str(person.date_birth.day), "_",
#                         str(person.date_birth.month), "_",
#                         str(person.date_birth.year)))
#         if key not in names:
#             names[key] = [person.id]
#         else:
#             names[key].append(person.id)
#     return names


def form_new_groups(*, predicate_methods=['satisfies_new_group_condition']):
    """Puts records into new groups if they do not have one yet and can meld with each other

    Each record will have only one group (person) or none if it's alone.
    Predicate methods must contain one or more method names from GroupRecord class.
    Predicate methods must be defined and maintained in Group.PREDICATE_METHODS attribute.
    Call with "satisfies_new_group_condition" to form new groups.
    More flexible methods may appear later.
    """

    def keyF(gr):
        """For sorting by birth date"""
        if gr.birth_date is None:
            return date.today()
        else:
            return gr.birth_date

    if len(predicate_methods) == 0:
        raise AttributeError("Predicate methods must contain at least one method")
    key = keyF
    print("Extracting records")
    unresolved_records = list(GroupRecord.objects.filter(group__isnull=True))
    unresolved_records.sort(key=key)
    record_groups = []
    for k, g in groupby(unresolved_records, key=key):
        record_groups.append(list(g))
    records_to_update = []
    for same_date_group in record_groups:
        new_groups = []
        for record_pair in combinations(same_date_group, 2):
            a = record_pair[0]
            b = record_pair[1]
            #if a.satisfies_new_group_condition(b):
            if a.check_predicates(b, predicate_methods):
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
    print("Have {0} items to save".format(len(records_to_update)))
    bulk_update(records_to_update, update_fields=['group'])
    print("Done")


def distribute_records_to_existing_groups():
    print("Extracting records")
    unresolved_records = list(GroupRecord.objects.filter(group__isnull=True))
    print("Making groups dict")
    groups_dict = Group.get_groups_dict()
    records_to_update = []
    print("Handling records")
    for record in unresolved_records:
        print(record.id)
        suitable_group = record.seek_for_group(groups_dict)
        if suitable_group is not None:
            record.group = suitable_group
            records_to_update.append(record)
    print("Have {0} records to update".format(len(records_to_update)))
    if len(records_to_update) > 0:
        bulk_update(records_to_update, update_fields=['group'])
    print("Done")


def check_group_consistency(group_record_list):
    """Returns True, if all records in list are fully equal"""
    first = group_record_list[0]
    for other in group_record_list[1:]:
        if not first.completely_equal(other):
            return False
    return True


def mark_inconsistency():
    """Update all groups consistency flag"""
    print("Extracting groups")
    groups_dict = Group.get_groups_dict()
    groups_to_update = []
    print("Iterating through groups")
    for group in groups_dict.keys():
        records = groups_dict[group]
        if check_group_consistency(records):
            if group.inconsistent:
                group.inconsistent = False
                groups_to_update.append(group)
        else:
            if not group.inconsistent:
                group.inconsistent = True
                groups_to_update.append(group)
    print("In-memory changes done")
    print("{} groups will be changed".format(len(groups_to_update)))
    bulk_update(groups_to_update, update_fields=['inconsistent'])
    print("Done")


def merge_consistent_groups():
    print("Making dict")
    groups_dict = Group.get_groups_dict()
    records_to_update = []
    hypostases_to_update = []
    print("Iterating")
    for group, records in groups_dict.items():
        print(group.id)
        if not group.inconsistent and len(records) > 1:
            changed_hypos = records[0].merge_records_by_hypostases(records[1:], save=False)
            hypostases_to_update.extend(changed_hypos) if len(changed_hypos) > 0 else None
            records_to_update.extend(records[1:])
    print("Saving")
    bulk_update(records_to_update, update_fields=['person'])
    bulk_update(hypostases_to_update, update_fields=['person'])
    print("Done")
