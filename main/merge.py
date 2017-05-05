from collections import namedtuple
from main_remote.models import Student, Employee, Postgraduate
from main.models import Person, Hypostasis, GroupRecord, Group
from itertools import groupby, combinations
from datetime import date


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


def compare_record_with_group(record, record_list):
    pass

def form_new_groups():
    """Puts record into new group if it does not have one yet and can meld with another record

    Each record should have only one group (person).
    """
    def keyF(gr):
        if gr.birth_date is None:
            return date.today()
        else:
            return gr.birth_date
    key = keyF
    unresolved_records = list(GroupRecord.objects.filter(group__isnull=True))
    unresolved_records.sort(key=key)
    record_groups = []
    for k, g in groupby(unresolved_records, key=key):
        record_groups.append(list(g))
    for same_date_group in record_groups:
        print(".")
        new_groups = []
        for record_pair in combinations(same_date_group, 2):
            a = record_pair[0]
            b = record_pair[1]
            if a.has_equal_full_name(b) or a.has_equal_first_and_middle_name(b) or a.has_equal_last_and_middle_name(b):
                a_in_group = False
                b_in_group = False
                new_group = None
                # for already_formed in new_groups:
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
                    a.save()
                if not b_in_group:
                    b.group = new_group
                    b.save()
    print("finished\n")

