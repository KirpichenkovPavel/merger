from django.contrib import admin
from main_remote.models import Division, BusinessProcess, Organization, Post, \
    Degree, Academic, Employee, Country, City, Topic, CoreResultType, FundingSource, EmployeeInfo, \
    PostgraduateProgram, StudentProgram, MoocPlatform

admin.site.register(BusinessProcess)
admin.site.register(CoreResultType)
admin.site.register(Division)
admin.site.register(Organization)
admin.site.register(Post)
admin.site.register(Degree)
admin.site.register(Academic)
admin.site.register(Employee)
admin.site.register(PostgraduateProgram)
admin.site.register(StudentProgram)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(Topic)
admin.site.register(FundingSource)
admin.site.register(EmployeeInfo)
admin.site.register(MoocPlatform)