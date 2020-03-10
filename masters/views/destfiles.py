from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from masters.models import DestinationFile as DestFile
from masters.models import DestinationTools as Tool
from masters.models import RulesetMaster 
from django.db.models import Q
from django.contrib import messages


######  DestinationFiles Master ####
@login_required(login_url='/uac/login/')
def master_destfile(request):
	filedata = DestFile.objects.raw('''SELECT A.dest_file_id ,A.dest_file_name,A.dest_short,B.tool_name FROM uac_destination_file A, uac_destination_tool B WHERE A.tool_id=B.tool_id''')
	page = request.GET.get('page', 1)
	paginator = Paginator(filedata, 15)
	
	try:
		dest = paginator.page(page)
	except PageNotAnInteger:
		dest = paginator.page(1)
	except EmptyPage:
		dest = paginator.page(paginator.num_pages)
	#to populate dest tool combo 
	tooldata = Tool.objects.all()
	
	return render(request, 'etl/uac_dest_files.html', {'destfiles': dest,'tools': tooldata})	

@login_required(login_url='/uac/login/')
@permission_required('masters.new_destination_type', login_url='/uac/error/')
def new_destfile(request):
	uid=request.user.id
	print(uid)
	try:
		input = DestFile(dest_file_name=request.POST['destfilename'], dest_short=request.POST['destshort'],tool_id=request.POST['destfiletool'])
		input.save()
		msg = "Record has been saved. "
		messages.success(request, msg
			)
		status = '200'
	except Exception as e:
		msg = "Error Occurred: " + str(e)
		messages.warning(request, msg)
		
		status = '400'
	finally:	
		return redirect('/uac/masters/destfiles')

@login_required(login_url='/uac/login/')
@permission_required('masters.delete_destination_type', login_url='/uac/error/')	
def delete_destfile(request, id):
    data = DestFile.objects.get(dest_file_id=id)
    rule = RulesetMaster.objects.filter(dest_file_id = id)
    if not rule:
    	data.delete()
    else:
    	msg = "Error Occurred: Ruleset exist, Cannot delete Destination Type"
    	messages.warning(request, msg)

    return redirect('/uac/masters/destfiles')

@login_required(login_url='/uac/login/')
@permission_required('masters.change_destination_type', login_url='/uac/error/')	
def update_destfile(request):

	data = DestFile.objects.get(dest_file_id=(request.POST['dfids']))
	data.dest_file_name = request.POST['editdestfile']
	data.dest_short = request.POST['editdestshort']
	data.tool_id = request.POST['editdftoolid']
	data.user_id=request.user.id
	data.save()
	return redirect('/uac/masters/destfiles')

@login_required(login_url='/uac/login/')
def search_destfile(request):
	fname = request.GET['search']
	qry='%' + fname + '%'

	filedata = DestFile.objects.raw(''' SELECT A.dest_file_id ,A.dest_file_name,B.tool_name FROM uac_destination_file A, uac_destination_tool B 
			WHERE A.tool_id=B.tool_id AND (A.dest_file_name LIKE %s OR B.tool_name LIKE %s OR A.dest_short LIKE %s) ''', [qry,qry,qry])

	page = request.GET.get('page', 1)
	paginator = Paginator(filedata, 15)
	
	try:
		dest = paginator.page(page)
	except PageNotAnInteger:
		dest = paginator.page(1)
	except EmptyPage:
		dest = paginator.page(paginator.num_pages)
	tooldata = Tool.objects.all()	
	return render(request, 'etl/uac_dest_files.html', {'destfiles': dest,'tools': tooldata})