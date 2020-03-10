from django.http import *
from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from masters.models import Erp
from masters.models import DestinationTools as Tool
from django.db.models import Q
from django.contrib import messages

######  TOOLS  ####
@login_required(login_url='/uac/login/')
def master_tool(request):
	tooldata = Tool.objects.all().order_by('-tool_id') 
	page = request.GET.get('page', 1)
	paginator = Paginator(tooldata, 15)
	
	try:
		tool = paginator.page(page)
	except PageNotAnInteger:
		tool = paginator.page(1)
	except EmptyPage:
		tool = paginator.page(paginator.num_pages)
		
	return render(request, 'etl/uac_dest_tools.html', {'tools': tool})	

@login_required(login_url='/uac/login/')
@permission_required('masters.new_dest_tool', login_url='/uac/error/')	
def new(request):
	uid=request.user.id
	try:
		input = Tool(tool_name=request.POST['toolname'], tool_short=request.POST['toolshort'], tool_desc=request.POST['tooldesc'])
		print(input)
		input.save()
		msg = "Record has been saved. "
		messages.success(request, msg)
		
		status = '200'
		

	except Exception as e:
		msg = "Error Occurred: " + str(e)
		messages.warning(request, msg)
		
		status = '400'
	finally:	
		return redirect('/uac/masters/tools')

@login_required(login_url='/uac/login/')
@permission_required('masters.delete_dest_tool', login_url='/uac/error/')	
def delete_tool(request, id):
    data = Tool.objects.get(tool_id=id)
    data.delete()
    # print("**********************************************8")
    return redirect('/uac/masters/tools')

@login_required(login_url='/uac/login/')
@permission_required('masters.change_dest_tool', login_url='/uac/error/')		
def update_tool(request):

	 data = Tool.objects.get(tool_id=request.POST['toolid'])
	 data.tool_name = request.POST['edittoolname']
	 data.tool_short = request.POST['edittoolshort']
	 data.tool_desc = request.POST['edittooldesc']
	 data.save()
	 return redirect('/uac/masters/tools')

@login_required(login_url='/uac/login/')
def search_tool(request):
	tooldata = Tool.objects.filter(Q(tool_name__contains=request.GET['search']) | Q(tool_desc__contains=request.GET['search'])| Q(tool_short__contains=request.GET['search'])) 

	page = request.GET.get('page', 1)
	paginator = Paginator(tooldata, 15)
	
	try:
		tool = paginator.page(page)
	except PageNotAnInteger:
		tool = paginator.page(1)
	except EmptyPage:
		tool = paginator.page(paginator.num_pages)
		
	return render(request, 'etl/uac_dest_tools.html', {'tools': tool})