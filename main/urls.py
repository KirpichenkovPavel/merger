from django.conf.urls import patterns, url
from main import views

urlpatterns = patterns("",
    url(r"^$", views.test_index),
    url(r"^cbv", views.IndexCBV.as_view())
)