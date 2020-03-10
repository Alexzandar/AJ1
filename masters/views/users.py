from django.http import *
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.authtoken.models import Token
from django.core import serializers
import json
from urllib.parse import urlparse, parse_qs 
import urllib
from django.db.models import Q
from masters.models import Erp

@login_required(login_url='/uac/login/')
def master_users(request):
	usrdata = User.objects.all()
	# perm = Permission.objects.all()
	perm = Permission.objects.raw('''SELECT * FROM auth_permission INNER JOIN django_content_type ON auth_permission.content_type_id = django_content_type.id WHERE django_content_type.app_label = "masters"''')
	page = request.GET.get('page', 1)
	paginator = Paginator(usrdata, 15)
	
	try:
		usr = paginator.page(page)
	except PageNotAnInteger:
		usr = paginator.page(1)
	except EmptyPage:
		usr = paginator.page(paginator.num_pages)
		
	return render(request, 'etl/uac_userprivileges.html', {'users': usr,'perms':perm})	

@login_required(login_url='/uac/login/')
def getUserToken(request,id):
	ids=request.user.id
	user=User.objects.get(id=ids)
	if user.has_perm('masters.view_client_token'):
		token = Token.objects.filter(user_id=id)
		response ={}
		response =  serializers.serialize('json', token)
		js = {'message':response, 'status':'200'}
		return JsonResponse(js)
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message)	

@login_required(login_url='/uac/login/')
# @permission_required('masters.view_client_permission', login_url='/uac/error/')	
def getUserPermissions(request,id):
	ids=request.user.id
	user=User.objects.get(id=ids)
	if user.has_perm('masters.view_client_permission'):
		perms = Permission.objects.filter(user=id)
		print(perms)
		response ={}
		response =  serializers.serialize('json', perms)
		js = {'message':response, 'status':'200'}
		return JsonResponse(js)
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message) 			

@login_required(login_url='/uac/login/')
def updateUserPermissions(request):
	ids=request.user.id
	user=User.objects.get(id=ids)
	if user.has_perm('masters.manage_client_password'):
		perms = request.POST.getlist('perms[]')
		newperms = list(map(int, perms)) 
		
		client = request.POST.get('selusrid')
		extperms = list(Permission.objects.filter(user=client).values_list('pk',flat=True))
		
		#print('New ',newperms)
		#print('exizting',extperms)
		
		newrecs= list(set(newperms) - set(extperms))
		delrecs= list(set(extperms) - set(newperms))
		uid=User.objects.get(id=client)
		#Removes existing permissions - if any 
		for x in delrecs:
			uid.user_permissions.remove(x)
		
		#Add new Permissions - if any
		for x in newrecs:
			uid.user_permissions.add(x)

		js = {'message':'User Permission has been Updated.', 'status':'200'}
		return JsonResponse(js)
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message) 	

@login_required(login_url='/uac/login/')	
def resetUserPassword(request,id):
	ids=request.user.id
	user=User.objects.get(id=ids)
	if user.has_perm('masters.reset_client_password'):
		user=User.objects.get(id=id)
		password = User.objects.make_random_password()
		# print(password)
		user.set_password(password)
		user.save()
		# response ={password}
		# response =  serializers.serialize('json', password)
		js = {'message':password, 'status':'200'}
		return JsonResponse(js)
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message) 	