from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from masters.models import Erp
from masters.models import DestinationTools as Tool
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User 

@login_required(login_url='/uac/login/')
def master_erp(request):
	erpdata = Erp.objects.all().order_by('-erp_id') 
	page = request.GET.get('page', 1)
	paginator = Paginator(erpdata, 15)
	
	try:
		erp = paginator.page(page)
	except PageNotAnInteger:
		erp = paginator.page(1)
	except EmptyPage:
		erp = paginator.page(paginator.num_pages)
		
	return render(request, 'etl/uac_erp.html', {'erps': erp})	

@login_required(login_url='/uac/login/')
@permission_required('masters.new_erp', login_url='/uac/error/')
def new_erp(request):
	uid=request.user.id
	try:
		input = Erp(erp_name=request.POST['erpname'], erp_desc=request.POST['erpdesc'])
		print(input)
		input.save()
		msg = "Record has been saved. "
		messages.success(request, msg)
		status = '200'
		
	except Exception as e:
		msg = "Error Occurred: " + str(e)
		messages.warning(request, msg)
		#messages.add_message(request, "danger", msg)
		status = '400'
	finally:	
		return redirect('/uac/masters/erp')
	
@login_required(login_url='/uac/login/')
@permission_required('masters.delete_erp', login_url='/uac/error/')	
def delete_erp(request, id):
    data = Erp.objects.get(erp_id=id)
    data.delete()
    return redirect('/uac/masters/erp')

@login_required(login_url='/uac/login/')
@permission_required('masters.change_erp', login_url='/uac/error/')	
def update_erp(request):
	 data = Erp.objects.get(erp_id=request.POST['erpid'])
	 data.erp_name = request.POST['editerpname']
	 data.erp_desc = request.POST['editerpdesc']
	 data.save()
	 return redirect('/uac/masters/erp')

@login_required(login_url='/uac/login/')
def search_erp(request):
	erpdata = Erp.objects.filter(Q(erp_name__contains=request.GET['search']) | Q(erp_desc__contains=request.GET['search'])) 

	page = request.GET.get('page', 1)
	paginator = Paginator(erpdata, 15)
	
	try:
		erp = paginator.page(page)
	except PageNotAnInteger:
		erp = paginator.page(1)
	except EmptyPage:
		erp = paginator.page(paginator.num_pages)
	
	
	return render(request, 'etl/uac_erp.html', {'erps': erp})	

@login_required(login_url='/uac/login/')
def custom_error_view(request):
    '''
    Default view for error 403: Inadequate permissions.
    '''
    return render_to_response('etl/403.html')	
