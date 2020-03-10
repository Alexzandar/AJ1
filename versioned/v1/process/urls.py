from django.urls import path
from django.conf.urls import url
from .views import *

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
    path('process/', TestAuthentication.as_view(), name="Version1"),
    ]
