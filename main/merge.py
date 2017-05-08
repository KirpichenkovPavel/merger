from collections import namedtuple
from main_remote.models import Student, Employee, Postgraduate
from main.models import Person, Hypostasis, GroupRecord, Group
from itertools import groupby, combinations
from datetime import date
from bulk_update.helper import bulk_update


def get_instance_from_hypostasis(hypostasis):
    """Hyposatsis should have only one not-None id.

     Function returns existing related instance."""
    ids = namedtuple("ids", ["student_id", "employee_id", "postgraduate_id"])
    ids_tuple = ids(student_id=hypostasis.student_id,
                    employee_id=hypostasis.employee_id,
                    postgraduate_id=hypostasis.postgraduate_id)
    if ids_tuple.student_id is not None:
        return Student.objects.get(id=ids_tuple.student_id)
    elif ids_tuple.employee_id is not None:
        return Employee.objects.get(id=ids_tuple.employee_id)
    elif ids_tuple.postgraduate_id is not None:
        return Postgraduate.objects.get(id=ids_tuple.postgraduate_id)
    else:
        raise ValueError("All ids in hypostasis are empty")


def get_names_dict():
    names = {}
    for person in list(Person.objects.all()):
        key = " ".join((person.last_name,
                        person.first_name,
                        person.middle_name,
                        str(person.date_birth.day), "_",
                        str(person.date_birth.month), "_",
                        str(person.date_birth.year)))
        if key not in names:
            names[key] = [person.id]
        else:
            names[key].append(person.id)
    return names


def names_equal(name1, name2):
    """For now compares all parts of names only."""
    return name1 == name2

# Need functions to eigther further merge keys in dict or to make new dict afterwards for another property.


def merge_dict(persons_dict):
    """Search for same names in two lists of hypostases."""

    for person_list in persons_dict.values():
        if len(person_list) > 1:
            first = person_list[0]
            rest = person_list[1:]
            #merge_persons(first, rest)


def form_new_groups():
    """Puts records into new groups if they do not have one yet and can meld with each other

    Each record should have only one group (person).
    """
    def keyF(gr):
        if gr.birth_date is None:
            return date.today()
        else:
            return gr.birth_date
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
            if a.satisfies_new_group_condition(b):
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


# def get_groups_dict():
#     return {group: list(group.grouprecord_set.all()) for group in Group.objects.all()}


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
