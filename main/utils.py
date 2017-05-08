from main.models import Hypostasis, Person, Group, GroupRecord
from main_remote.models import Student, Employee, Postgraduate
from main.merge import get_instance_from_hypostasis
from bulk_update.helper import bulk_update


def create_hypostases():
    """Create a new hypostasis for each student, employee and postgraduate.
    Should be called once.
    """
    print("\n\n\nStarted fetching students\n\n\n")
    students_list = list(Student.objects.all())
    print("\n\n\nStarted fetching employees\n\n\n")
    employee_list = list(Employee.objects.all())
    print("\n\n\nStarted fetching postgraduates\n\n\n")
    postgraduate_list = list(Postgraduate.objects.all())
    print("\n\n\nMaking hypostasis for students.\n\n\n")
    hypostases = []
    for student in students_list:
        hypostases.append(Hypostasis(student_id=student.id))
    print("\n\n\nMaking hypostasis for employees.\n\n\n")
    for employee in employee_list:
        hypostases.append(Hypostasis(employee_id=employee.id))
    print("\n\n\nMaking hypostasis for postgraduates.\n\n\n")
    for postgraduate in postgraduate_list:
        hypostases.append(Hypostasis(postgraduate_id=postgraduate.id))
    Hypostasis.objects.bulk_create(hypostases)


def adjust_employee_key():
    """Employee key is a string with leading zeros"""
    def func(x):
        tmp = x.employee_id
        tmp = "0" * (5 - len(tmp)) + tmp
        x.employee_id = tmp
        # x.save()
    lst = list(Hypostasis.objects.filter(employee_id__isnull=False))
    list(map(func, lst))
    bulk_update(lst, update_fields=['employee_id'])


def create_persons(hypo_list):
    """Create a person for each hypostasis in list."""
    hypostases_to_update = []
    print("Making")
    for h in hypo_list:
        instance = get_instance_from_hypostasis(h)
        new_person = Person(last_name=instance.last_name,
                            first_name=instance.first_name,
                            middle_name=instance.middle_name,
                            birth_date=instance.date_birth)
        new_person.save()
        h.person = new_person
        hypostases_to_update.append(h)
        #h.save()
        print(h.id)
    print("Saving")
    bulk_update(hypostases_to_update, update_fields=['person'])


def create_group_records():
    """Creates group records for initial data for test purposes."""
    records = []
    # groups = []
    # print("\nSaving groups\n")
    # for j in range(Hypostasis.objects.count()):
    #     print("\n{0}\n".format(j))
    #     g = Group()
    #     groups.append(g)
    # Group.objects.bulk_create(groups)
    print("\nCreating records\n")
    i = 0
    #groups = list(Group.objects.all())
    for hypo in list(Hypostasis.objects.all()):
        print("\n{0}\n".format(i))
        instance = hypo.get_non_empty_instance()
        #group = groups.pop()
        records.append(GroupRecord(hypostasis=hypo,
                                   person=hypo.person,
                                   group=None,
                                   last_name=instance.last_name,
                                   first_name=instance.first_name,
                                   middle_name=instance.middle_name,
                                   birth_date=instance.date_birth))
        i += 1
    print("\nSaving records\n")
    GroupRecord.objects.bulk_create(records)


def direct_search():
    """Slower than reverse"""
    result = {}
    records = GroupRecord.objects.filter(group__isnull=False)
    for record in records:
        key = record.group
        try:
            result[key].append(record)
        except KeyError:
            result[key] = [record]
    return result