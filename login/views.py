from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth import authenticate, login, logout
import datetime
from django.db.models import Q

def login_user(request):
	logout(request)
	username = password = ''
	if request.POST:
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/uac/index/')
		else:
			return render(request, 'etl/uac_login.html',{ 'err_msg' :'Login Error'})
			#return render_to_response('etl/uac_login.html', context_instance=RequestContext(request))
	else:
		return render(request, 'etl/uac_login.html')

			
