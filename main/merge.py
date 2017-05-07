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
    bulk_save_items = []
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
                    bulk_save_items.append(a)
                    #a.save()
                if not b_in_group:
                    b.group = new_group
                    bulk_save_items.append(b)
                    #b.save()
    print("Have {0} items to save".format(len(bulk_save_items)))
    bulk_update(bulk_save_items)
    print("Done")


def distribute_into_existing_groups():
    unresolved_records = list(GroupRecord.objects.filter(group__isnull=True))
    records_to_update = []
    for record in unresolved_records:
        print(record.id)
        if record.merge_with_group():
            records_to_update.append(record)
    print("Have {0} records to update".format(len(records_to_update)))
    if len(records_to_update) > 0:
        bulk_update(records_to_update)
    print("Done")


def get_groups_dict():
    return {group: list(group.grouprecord_set.all()) for group in Group.objects.all()}


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
    groups_dict = get_groups_dict()
    groups_to_save = []
    print("Iterating through groups")
    for group in get_groups_dict().keys():
        records = groups_dict[group]
        if check_group_consistency(records):
            if group.inconsistent:
                group.inconsistent = False
                groups_to_save.append(group)
        else:
            if not group.inconsistent:
                group.inconsistent = True
                groups_to_save.append(group)
    print("In-memory changes done")
    print("{} groups will be changed".format(len(groups_to_save)))
    bulk_update(groups_to_save)
    print("Done")