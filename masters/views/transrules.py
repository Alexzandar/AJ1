from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from masters.models import DestinationRules as dr
from django.db.models import Q

######  Source File Master ####
@login_required(login_url='/uac/login/')
def master_transrules(request):
	filedata = dr.objects.raw('''SELECT * FROM uac_dest_rules''')
	page = request.GET.get('page', 1)
	paginator = Paginator(filedata, 15)
	
	try:
		src = paginator.page(page)
	except PageNotAnInteger:
		src = paginator.page(1)
	except EmptyPage:
		src = paginator.page(paginator.num_pages)

		
	return render(request, 'etl/uac_transrules.html', {'transrules': src})	

@login_required(login_url='/uac/login/')
@permission_required('masters.new_transformation_rule', login_url='/uac/error/')
def new_transrules(request):
	uid=request.user.id
	input = dr(rule_name=request.POST['rulename'], regexp=request.POST['ruleregx'])
	input.save()
	return redirect('/uac/masters/transrules')

@login_required(login_url='/uac/login/')
@permission_required('masters.delete_transformation_rule', login_url='/uac/error/')	
def delete_transrules(request, id):
    data = dr.objects.get(rule_id=id)
    data.delete()
    return redirect('/uac/masters/transrules')

@login_required(login_url='/uac/login/')
@permission_required('masters.change_transformation_rule', login_url='/uac/error/')	
def update_transrules(request):

	 data = dr.objects.get(rule_id=request.POST['trid'])
	 data.rule_name= request.POST['editrulename']
	 data.regexp = request.POST['editregex']
	 data.save()
	 return redirect('/uac/masters/transrules')

@login_required(login_url='/uac/login/')
def search_sourcefile(request):
	fname = request.GET['search']
	qry='%' + fname + '%'

	filedata = list(dr.objects.raw(''' SELECT A.source_file_id ,A.source_file_name,B.erp_name FROM uac_source_file A, uac_source_erp B WHERE A.erp_id=B.erp_id
	 AND (A.source_file_name LIKE %s OR B.erp_name LIKE %s) ''', [qry,qry]))

	page = request.GET.get('page', 1)
	paginator = Paginator(filedata, 15)
	
	try:
		src = paginator.page(page)
	except PageNotAnInteger:
		src = paginator.page(1)
	except EmptyPage:
		src = paginator.page(paginator.num_pages)
	#to populate ERP in  combo 
	erpdata = Erp.objects.all()	
	return render(request, 'etl/uac_source_files.html', {'sourcefiles': src,'erps': erpdata})	
