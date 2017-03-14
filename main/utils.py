from main.models import Hypostasis, Person
from main_remote.models import Student, Employee, Postgraduate
from main.merge import get_instance_from_hypostasis

def create_hypostasis():
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
    for student in students_list:
        new_hypo = Hypostasis(student_id=student.id)
        new_hypo.save()
    print("\n\n\nMaking hypostasis for employees.\n\n\n")
    for employee in employee_list:
        new_hypo = Hypostasis(employee_id=employee.id)
        new_hypo.save()
    print("\n\n\nMaking hypostasis for postgraduates.\n\n\n")
    for postgraduate in postgraduate_list:
        new_hypo = Hypostasis(postgraduate_id=postgraduate.id)
        new_hypo.save()
a = dict()

def adjust_employee_key():
    """Employee key is a string with leading zeros"""
    def func(x):
        tmp = x.employee_id
        tmp = "0" * (5 - len(tmp)) + tmp
        x.employee_id = tmp
        x.save()
    lst = list(Hypostasis.objects.filter(employee_id__isnull=False))
    list(map(func, lst))


def create_persons(hypo_list):
    """Create a person for each hypostasis in list."""
    for h in hypo_list:
        instance = get_instance_from_hypostasis(h)
        new_person = Person(last_name=instance.last_name,
                            first_name=instance.first_name,
                            middle_name=instance.middle_name,
                            birth_date=instance.date_birth)
        new_person.save()
        h.person_id = new_person.id
        h.save()
        print(h.id)

