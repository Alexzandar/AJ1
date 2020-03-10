from django.http import *
import sys
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required, permission_required

import json
from django.conf import settings
from django.core import serializers
from masters.models import DestinationRules as dr
from masters.models import RulesetDetails 
from django.core.files.storage import FileSystemStorage
import pandas as pd
import numpy as np
from masters.models import RulesetMaster
from masters.models import RulesetDetails
from masters.models import ClientExtractSettings 
from masters.models import ClientExtractorDetails

import datetime
from django.db.models import Q
from masters.models import Erp
from masters.models import DestinationFile as df
from masters.models import DestinationTools as Tool
from masters.models import Clients 
from masters.models import SchedulerConfig
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db import connection
from django.contrib import messages

@login_required(login_url='/uac/login/')
def destschema(request):
	dest_file = df.objects.values('dest_file_id', 'dest_file_name')
	dest_tool= Tool.objects.all()
	#ruledata = RulesetMaster.objects.all()
	#ruledata = list(RulesetMaster.objects.raw('''SELECT * from uac_ruleset_master''')
	ruledata = RulesetMaster.objects.raw('''SELECT RM.ruleset_id, RM.ruleset_name,RM.tool_id, RM.dest_file_id, DT.tool_name,  DF.dest_file_name from uac_ruleset_master AS RM INNER JOIN uac_destination_file AS DF ON RM.dest_file_id = DF.dest_file_id INNER JOIN uac_destination_tool AS DT ON RM.tool_id = DT.tool_id''')

	page = request.GET.get('page', 1)
	paginator = Paginator(ruledata, 20)
	
	try:
		rule = paginator.page(page)
	except PageNotAnInteger:
		rule = paginator.page(1)
	except EmptyPage:
		rule = paginator.page(paginator.num_pages)
		
	return render(request, 'etl/uac_destschema.html',{ 'tool' :dest_tool,'destfile' :dest_file, 'rule':rule})
	

@login_required(login_url='/uac/login/')	
def schemasave(request):
	json_data = request.GET.get('formdata')
	data = json.loads(json_data)
	msg=''
	rid = ''
	status ='400'
	counter = 1
	rule_set_name = data['RuleSetName']
	dest_file = data['DestFile']
	dest_tool = data['DestTool']
	uniq_flds = data['UniqueFields']
	id=request.user.id
	user=User.objects.get(id=id)
	if user.has_perm('masters.new_extractor'):
		try:
			dt=RulesetMaster(
			ruleset_name = rule_set_name,
			tool_id = dest_tool,
			dest_file_id = dest_file,
			uniq_flds = uniq_flds,
			user_id = request.user.id)
			dt.save()
			rid = RulesetMaster.objects.latest('ruleset_id')
			for key in data['DestSchema']:
				ds=RulesetDetails(		
				ruleset_id =rid.ruleset_id,
				tool_id	= dest_tool,
				dest_file_id = dest_file,
				column_id = counter,
				column_name	= key['FieldName'],
				column_type = key['Type'],
				column_length = key['Length'],
				required = key['Required'],
				rules = key['TransRules'],
				ordinal = counter,
				user_id = request.user.id)
				ds.save()
				counter = counter +1
			status='200'
			msg="Record has been saved!"
		except Exception as e:
			if str(e) == "UNIQUE constraint failed: uac_ruleset_master.ruleset_name":
				msg = "Error Occurred: Rule Set name already exist"
				status = '400'
			else:
				msg = "Error Occurred: " + str(e)
				status = '400'
		finally:	
			js = {'message':msg,'status':status}
			return JsonResponse(js)
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message) 		
	
@login_required(login_url='/uac/login/')	
def schemaedit(request):
	json_data = request.GET.get('formdata')
	data = json.loads(json_data)
	msg=''
	rid = ''
	status ='400'
	counter = 1
	rule_set_name = data['RuleSetName']
	dest_file = data['DestFile']
	dest_tool = data['DestTool']
	uniq_flds = data['UniqueFields']
	id = data['ID']
	ids=request.user.id
	user=User.objects.get(id=ids)
	if user.has_perm('masters.change_extractor'):
		try:
			RulesetMaster.objects.filter(ruleset_id=id).delete()	
			RulesetDetails.objects.filter(ruleset_id=id).delete()	
			dt=RulesetMaster(
			ruleset_id = id,
			ruleset_name = rule_set_name,
			tool_id = dest_tool,
			dest_file_id = dest_file,
			uniq_flds = uniq_flds,
			user_id = request.user.id)
			dt.save()		
			for key in data['DestSchema']:
				ds=RulesetDetails(		
				ruleset_id =id,
				tool_id	= dest_tool,
				dest_file_id = dest_file,
				column_id = counter,
				column_name	= key['FieldName'],
				column_type = key['Type'],
				column_length = key['Length'],
				required = key['Required'],
				rules = key['TransRules'],
				ordinal = counter,	
				user_id = request.user.id)
				ds.save()
				counter = counter +1
			status='200'
			msg="Records has been saved!"
		except Exception as e:
			if str(e) == "UNIQUE constraint failed: uac_ruleset_master.ruleset_name":
				msg = "Error Occurred: Rule Set name already exist"
				status = '400'
			else:
				msg = "Error Occurred: " + str(e)
				status = '400'
		finally:	
			js = {'message':msg,'status':status}
			return JsonResponse(js)
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message) 

@login_required(login_url='/uac/login/')
@permission_required('masters.delete_extractor', login_url='/uac/error/')		
def destdelete(request, id):
	RulesetMaster.objects.filter(ruleset_id=id).delete()	
	RulesetDetails.objects.filter(ruleset_id=id).delete()	
	return redirect('/uac/ruleset')

def _getrules(request):
	rules = dr.objects.values_list('rule_id', 'rule_name')
	return JsonResponse(list(rules),safe=False)
	
def schemaGetDetails(request):
	DData = RulesetDetails.objects.filter(Q(ruleset_id=request.GET.get('rid')))
	unq = RulesetMaster.objects.filter(Q(ruleset_id=request.GET.get('rid')))
	DetailData ={}	
	DetailData =  serializers.serialize('json', DData)
	unqData = {}
	unqData = serializers.serialize('json', unq)
	return JsonResponse({'DetailData':DetailData,'unq':unqData})


### EXTRACTOR SETTINGS
def extractset(request):
	clients= Clients.objects.all()
	destfile= df.objects.all()
	erps = Erp.objects.all()
	tools = Tool.objects.all()
	rs=RulesetMaster.objects.all()
	return render(request, 'etl/uac_extractsettings.html',{'erps':erps,'extractor' :destfile, 'clients' :clients,'tools':tools,'rset':rs})

def getExtractorHeading(request):
	if request.method == 'POST' and request.FILES['myfile']:
		myfile = request.FILES['myfile']
		fs = FileSystemStorage()
		filename = fs.save(myfile.name, myfile)
		dir = fs.path(myfile.name)
		uploaded_file_url = fs.url(filename)
		fnam= settings.MEDIA_ROOT + '/' + myfile.name
		data = pd.read_csv(fnam, sep='\t')
		#heading =json.dumps(data.head())
		#----------------------------------
		#Filename without extension
		fn= myfile.name.rsplit('.', 1)[0]
		# split file name to list array
		value = fn.split("_")
		#filename pattern
		key = ["FileName", "System" , "Config" , "TimeStamp"]
		#Make array with filename string and its Key (Name)
		mergeobj = zip(key, value)
		arrayfname = dict(mergeobj)
		#----------------------------------

		heading = list(data.head())
		js = {'message':heading,'fn':fn,'arfname':arrayfname,'status':'200'}
	return JsonResponse(js)
		
		
def getRulesetColumns(request):	
	rset_id=request.GET.get('id')
	rulecolumns= RulesetDetails.objects.filter(ruleset_id=rset_id).values_list('column_name')
	
	js = {'columns':list(rulecolumns),'status':'200','rid':rset_id}
	return JsonResponse(js)

@login_required(login_url='/uac/login/')
def saveExtractSettings(request):	
	json_data = request.GET.get('formdata')
	data = json.loads(json_data)
	
	cid = data['ClientId']
	tid	=  data['ToolID']
	did = data['DestFileId']
	input_prefix = data['FileNameStart']
	#Checks for cofig exists
	msg = ""
	db_found =0
	prefix = ClientExtractSettings.objects.filter(client_id=cid, tool_id=tid,dest_file_id=did).values_list('file_name_start')
	for records in prefix:
		exist_length=len(records[0]) #Length of existing prefix
		if records[0].startswith(input_prefix) or input_prefix.startswith(records[0]):
		#if records[0] == data['FileNameStart']:
			msg = msg + "&emsp;-<b>" + records[0] +  "</b> <br />"
			db_found= db_found + 1
			status = '400'
	
	if db_found > 0:
		warn_msg = "<b>Updation Failed</b><br />Client Settings already saved with following prefix(es) for the selected extractor. <br />This may override given prefix <b>" + input_prefix + "</b><br />"
		js = {'message':warn_msg + msg,'status':status}
		return JsonResponse(js)
	usrid=request.user.id
	user=User.objects.get(id=usrid)
	if user.has_perm('masters.new_client_extractor_setting'):
		try:
			ces=ClientExtractSettings(
			client_id = data['ClientId'],
			erp_id	=  data['ErpId'],
			tool_id	=  data['ToolID'],
			dest_file_id = data['DestFileId'],
			ruleset_id = data['RuleSetId'],
			data_format = data['DataFormat'],
			column_delimiter = data['ColDelimiter'],
			file_name_start = data['FileNameStart'],
			file_name_format = data['FileName'],
			user_id = request.user.id)
			ces.save()
			sid = ClientExtractSettings.objects.latest('settings_id')
			counter = 1 
			for key in data['DestCols']:
				dc=ClientExtractorDetails(		
				settings_id =sid.settings_id,
				source_column =data['SourceCols'][counter-1]['ColumnName'],
				dest_column =  key['ColumnName'],
				dest_column_id	=  counter,
				ordinal = counter,
				user_id = request.user.id)
				dc.save()
				counter = counter + 1
			status='200'
			msg="Client-Extractor Settings has been saved. Ref# " + str(sid.settings_id)
		except Exception as e:
			msg = "Error Occurred: " + str(e)
			status = '400'
		finally:	
			js = {'message':msg ,'status':status}
			return JsonResponse(js)
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message) 		

@login_required(login_url='/uac/login/')
def viewSettingsList(request):
	ids=request.user.id
	user=User.objects.get(id=ids)  
	if user.has_perm('masters.view_client_extractor_setting'):
		sql ="SELECT A.settings_id, B.client_name, C.erp_name, D.tool_name, E.dest_file_name, F.ruleset_name, A.file_name_start FROM   uac_client_settings_master A, uac_erp_clients B, uac_source_erp C, uac_destination_tool D, uac_destination_file E, uac_ruleset_master F WHERE  A.client_id = B.client_id AND A.erp_id = C.erp_id AND A.tool_id = D.tool_id AND A.dest_file_id = E.dest_file_id AND A.ruleset_id = F.ruleset_id;"
		cursor = connection.cursor()
		cursor.execute(sql)
		records=cursor.fetchall()
		return JsonResponse({'message': records ,'status':'200'})
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message) 	
	
def viewMappingsList(request):
	setid=request.GET.get('id')
	maplist= ClientExtractorDetails.objects.filter(settings_id=setid).values_list('source_column','dest_column')
	js = {'columns':list(maplist),'status':'200'}
	return JsonResponse(js)


#Scheduler Configs
###################
def master_sched(request):
	clients= Clients.objects.all()
	destfile= df.objects.all()
	erps = Erp.objects.all()
	tools = Tool.objects.all()
	file_start= ClientExtractSettings.objects.all()
	schedList = SchedulerConfig.objects.raw('''SELECT B.client_name, C.erp_id, C.erp_name, D.tool_name, E.dest_short, A.date_from,A.active,A.scheduler_id,A.file_name_start AS file_name_id,F.file_name_start  FROM   uac_scheduler_config A, uac_erp_clients B,uac_source_erp C, uac_destination_tool D, uac_destination_file E, uac_client_settings_master F WHERE  A.client_id = B.client_id AND A.erp_id = C.erp_id AND A.tool_id = D.tool_id  AND A.dest_file_id = E.dest_file_id AND A.file_name_start=F.settings_id''')
	page = request.GET.get('page', 1)
	paginator = Paginator(schedList, 15)
	
	try:
		sched = paginator.page(page)
	except PageNotAnInteger:
		sched = paginator.page(1)
	except EmptyPage:
		sched = paginator.page(paginator.num_pages)
		
	return render(request, 'etl/uac_scheduler.html',{'file_start':file_start,'schedule' : sched,'erps':erps,'extractor' :destfile, 'clients' :clients,'tools':tools})

@permission_required('masters.new_process_scheduler', login_url='/uac/error/')
def save_sched(request):
	uid=request.user.id
	try:
		input = SchedulerConfig(client_id=request.POST['client'],erp_id=request.POST['erp'],tool_id=request.POST['tool'],dest_file_id=request.POST['extract'],date_from= request.POST['schedtime'],user_id = uid,file_name_start=request.POST['file_start'])
		input.save()
		msg = "Record has been saved. "
		messages.success(request, msg)
		status = '200'
	except Exception as e:
		msg = "Error Occurred: " + str(e)
		messages.warning(request, msg)
		status = '400'
	finally:	
		return redirect('/uac/scheduler')

@permission_required('masters.delete_process_scheduler', login_url='/uac/error/')
def remove_sched(request, id):
	try:
		data = SchedulerConfig.objects.get(scheduler_id=id)
		data.delete()
		msg = "Record has been removed. "
		messages.success(request, msg)
		status = '200'
	except Exception as e:
		msg = "Error Occurred: " + str(e)
		messages.warning(request, msg)
		status = '400'
	finally:
		return redirect('/uac/scheduler')

@permission_required('masters.change_process_scheduler', login_url='/uac/error/')
def changestat_sched(request, id, actcode):
	try:
		data = SchedulerConfig.objects.get(scheduler_id=id)
		if actcode == 'Y':
			data.active = 'N'
		else:
			data.active = 'Y'
		data.save()	
		msg = "Record has been updated."
		messages.success(request, msg)
		status = '200'
	except Exception as e:
		msg = "Error Occurred: " + str(e)
		messages.warning(request, msg)
		status = '400'
	finally:
		return redirect('/uac/scheduler')

def schema_unique(request):
	# print(request.POST.get('name'))
	name = request.POST.get('name')
	item_id = request.POST.get('id',None)
	if (item_id):
		sample = RulesetMaster.objects.filter(ruleset_name = name)
		rule_name=sample.exclude(ruleset_id=item_id)
	else:
		rule_name = RulesetMaster.objects.filter(ruleset_name = name)
	if rule_name:
		found = True
	else:
		found = False	
	js = {'success' : found}		
	return JsonResponse(js)