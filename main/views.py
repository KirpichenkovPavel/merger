from django.shortcuts import render
from main.util import bp_user_auth
from main.models import GroupRecord
from main_remote.models import Student, Employee, Postgraduate
from django.views.generic import View, ListView


class IndexCBV(View):

    def get(self, request):
        bp_user_auth()
        stud_list = list(Student.objects.all()[:20])
        context = {"person_list": stud_list}
        return render(request, "main/index.html", context)


def test_index(request):
    bp_user_auth()
    stud_list = list(Student.objects.all()[:20])
    context = {"person_list": stud_list}
    return render(request, "main/index.html", context)
