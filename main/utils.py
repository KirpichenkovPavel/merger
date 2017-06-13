from main.models import Hypostasis, Person, Group, GroupRecord
from main_remote.models import Student, Employee, Postgraduate
from bulk_update.helper import bulk_update
from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django_remote_model.util.util import shell_authenticate, add_bp_credentials
from time import time
import random


def create_hypostases():
    """Create a new hypostasis for each student, employee and postgraduate. Should be called once."""
    print("\n\n\nStarted fetching students\n\n\n")
    students_list = list(Student.objects.all())
    print("\n\n\nStarted fetching employees\n\n\n")
    employee_list = list(Employee.objects.all())
    print("\n\n\nStarted fetching postgraduates\n\n\n")
    postgraduate_list = list(Postgraduate.objects.all())
    print("\n\n\nMaking hypostases for students.\n\n\n")
    hypostases = []
    for student in students_list:
        hypostases.append(Hypostasis(student_id=student.id))
    print("\n\n\nMaking hypostases for employees.\n\n\n")
    for employee in employee_list:
        hypostases.append(Hypostasis(employee_id=employee.id))
    print("\n\n\nMaking hypostases for postgraduates.\n\n\n")
    for postgraduate in postgraduate_list:
        hypostases.append(Hypostasis(postgraduate_id=postgraduate.id))
    Hypostasis.objects.bulk_create(hypostases)


def create_persons(hypo_list):
    """Create a person for each hypostasis in list."""
    hypostases_to_update = []
    print("Making")
    for h in hypo_list:
        instance = h.non_empty_instance
        new_person = Person(last_name=instance.last_name,
                            first_name=instance.first_name,
                            middle_name=instance.middle_name,
                            birth_date=instance.date_birth)
        new_person.save()
        h.person = new_person
        hypostases_to_update.append(h)
        print(h.id)
    print("Saving")
    bulk_update(hypostases_to_update, update_fields=['person'])


def adjust_employee_key():
    """Employee key is a string with leading zeros"""
    def func(x):
        tmp = x.employee_id
        tmp = "0" * (5 - len(tmp)) + tmp
        x.employee_id = tmp
    lst = list(Hypostasis.objects.filter(employee_id__isnull=False))
    list(map(func, lst))
    bulk_update(lst, update_fields=['employee_id'])


def update_persons_in_groups():
    """Use in case some groups were merged, but person was not appropriately set."""
    group_dict = Group.get_dictionary()
    cntr = 0
    ttl = len(group_dict)
    for group, records in group_dict.items():
        cntr += 1
        print("{} of {}".format(cntr, ttl))
        if group.person is None:
            unique_persons = set()
            for r in records:
                unique_persons.add(r.person)
            if len(unique_persons) == 1:
                group.person = unique_persons.pop()
                group.save()


def create_group_records(no_doubles=False):
    """Creates group records for initial data for test purposes."""
    records = []
    print("\nCreating records\n")
    i = 0
    for hypo in list(Hypostasis.objects.all()):
        if no_doubles:
            if hypo.grouprecord_set.count() > 0:
                continue
        print("{0}".format(i))
        instance = hypo.non_empty_instance
        person = hypo.person
        records.append(GroupRecord(hypostasis=hypo,
                                   person=person,
                                   group=None,
                                   last_name=instance.last_name,
                                   first_name=instance.first_name,
                                   middle_name=instance.middle_name,
                                   birth_date=instance.date_birth))
        i += 1
    print("\nSaving records\n")
    GroupRecord.objects.bulk_create(records)
    print("Done")


def update_group_record_persons():
    start = time()
    grs = list(GroupRecord.objects.all())
    for gr in grs:
        print(gr.id)
        gr.person = gr.hypostasis.person
    update = time()
    bulk_update(grs, update_fields=['person'], batch_size=1000)
    print("{} seconds for update".format(update - start))
    print("{} seconds for save".format(time() - update))


def rand_str(length):
    str = ''
    letters = 'йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ- '
    i = 0
    while i < length:
        str += random.choice(letters)
        i += 1
    return str


def random_records():
    lst = list(GroupRecord.objects.all())
    for r in lst:
        r.last_name = rand_str(random.randint(2,30))
        r.first_name = rand_str(random.randint(2, 30))
        r.middle_name = rand_str(random.randint(2, 30))
    bulk_update(lst)


def drop_from_group():
    print("Droping one record from big groups")
    dct = Group.get_dictionary()
    records = []
    i = 0
    ttl = len(dct)
    for v in dct.values():
        i += 1
        if i % 100 == 0:
            print("{} of {}".format(i, ttl))
        if len(v) > 2:
            v[0].group = None
            records.append(v[0])
    print("Saving")
    bulk_update(records, update_fields=['group'], batch_size=1000)
    print("Done")


def bp_user_auth():
    shell_authenticate(settings.MANAGEMENT_USER_NAME, settings.MANAGEMENT_USER_PASS)
    request = CrequestMiddleware.get_request()
    request = add_bp_credentials(request, settings.MANAGEMENT_BP_NAME, settings.MANAGEMENT_BP_PASS)
    CrequestMiddleware.set_request(request)