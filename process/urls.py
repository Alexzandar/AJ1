from django.conf.urls import url
from django.urls import include, re_path
from rest_framework.authtoken import views as drf_views

from process import views

urlpatterns = [
    url(r'^etl-process/$', views.JSONUpload.as_view(), name='test-api'),
    url(r'^process/start/$', views.process, name='Process Starts Here'),
    url(r'^process/startetl/$', views.cleansing, name='ETL Process here'),
    url(r'^process/test/$', views.TestClass.as_view(), name="test"),
    url(r'^api/process/$', views.TestAuthentication.as_view(), name="test-auth"),
    url(r'^api/v1/process/$', views.TestAuthentication.as_view(), name="Version1"),

    url(r'^process/file_start_rule/$', views.ETL_file_start.as_view(), name='ETL_filestart'),
    url(r'^process/define_rule/$', views.ETL_define_rule.as_view(), name='ETL_Filter'),
]

urlpatterns += [
    url(r'^api-token-auth/', drf_views.obtain_auth_token)
]
