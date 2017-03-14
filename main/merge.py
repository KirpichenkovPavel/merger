from collections import namedtuple
from main_remote.models import Student, Employee, Postgraduate
from main.models import Person, Hypostasis


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
            merge_persons(first, rest)

