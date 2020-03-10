from django.urls import path
from . import views
from django.conf.urls import url


urlpatterns = [
	path('index/', views.index, name='index'),
	url(r'client_extract_valuechange/', views.client_extract_valuechange, name='Tool Master'),
	# url(r'define_rule/', views.define_rule, name='ajax call')


]