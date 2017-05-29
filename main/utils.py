from main.models import Hypostasis, Person, Group, GroupRecord
from main_remote.models import Student, Employee, Postgraduate
from bulk_update.helper import bulk_update
from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django_remote_model.util.util import shell_authenticate, add_bp_credentials
from difflib import SequenceMatcher
import jellyfish as jf


def bp_user_auth():
    shell_authenticate(settings.MANAGEMENT_USER_NAME, settings.MANAGEMENT_USER_PASS)
    request = CrequestMiddleware.get_request()
    request = add_bp_credentials(request, settings.MANAGEMENT_BP_NAME, settings.MANAGEMENT_BP_PASS)
    CrequestMiddleware.set_request(request)


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
        instance = h.non_empty_instance
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
    grs = list(GroupRecord.objects.all())
    for gr in grs:
        print(gr.id)
        gr.person = gr.hypostasis.person
    bulk_update(grs, update_fields=['person'])


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


def show_metrics(gd):
    for group, records in gd.items():
        if group.inconsistent:
            if records[0].first_name != records[1].first_name:
                name1 = records[0].first_name
                name2 = records[1].first_name
            else:
                name1 = records[0].last_name
                name2 = records[1].last_name
            print("{0} {1} l:{2} j:{3} j-w:{4}".format(name1,
                                                       name2,
                                                       jf.levenshtein_distance(name1, name2),
                                                       jf.jaro_distance(name1, name2),
                                                       jf.jaro_winkler(name1, name2)))


def show_close_records(tolerance):
    print(tolerance)
    gd = Group.get_groups_dict()
    for g, grs in gd.items():
        if g.inconsistent:
            for gr in grs[1:]:
                if grs[0].close_by_jaro_winkler(gr, 'last_name', tolerance) or \
                        grs[0].close_by_jaro_winkler(gr, 'first_name', tolerance):
                    print("{} {}".format(grs[0], gr))


def calc_xtra():
    ps = list(Person.objects.all().prefetch_related('hypostasis_set'))
    cnt = 0
    item = 0
    for p in ps:
        print(item)
        item += 1
        cnt += p.hypostasis_set.count() - 1
    print(cnt)


def gr_update_persons():
    lst = list(GroupRecord.objects.all())
    i = 0
    ttl = len(lst)
    for gr in lst:
        print("{} of {} records".format(i, ttl))
        gr.person = gr.hypostasis.person
        i += 1
    print("Saving")
    bulk_update(lst, update_fields=['person'])
    print("Done")
