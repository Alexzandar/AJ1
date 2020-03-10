from django.http import *
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from masters.models import Clients
from masters.models import ClientsERP
from masters.models import Erp 
from masters.models import DestinationTools as Tool
from masters.models import ClientsTools
from django.db.models import Q
from utils.utils import ProcessFile
from django.conf import settings
import json
from django.core import serializers

######  Source File Master ####
@login_required(login_url='/uac/login/')
def master_clients(request):
	
	clientdata = Clients.objects.all()		
	page = request.GET.get('page', 1)
	paginator = Paginator(clientdata, 5)
	
	try:
		client = paginator.page(page)
	except PageNotAnInteger:
		client = paginator.page(1)
	except EmptyPage:
		client = paginator.page(paginator.num_pages)
	#to populate ERP in  combo 
	erpdata = Erp.objects.all()
	#to populate dest tools in  combo
	tooldata = Tool.objects.all()
	
	return render(request, 'etl/uac_addclients.html', {'clients': client,'erps': erpdata,'tools':tooldata})	

@login_required(login_url='/uac/login/')	
def edit_details(request):
	data = ClientsERP.objects.filter(Q(client_id=request.GET.get('cid')))
	clientdata={}
	clientdata=  serializers.serialize('json', data)	
	tdata = ClientsTools.objects.filter(Q(client_id=request.GET.get('cid')))
	tooldata ={}	
	tooldata =  serializers.serialize('json', tdata)
	return JsonResponse({'clientdata': clientdata,'tooldata':tooldata})
	
	

@login_required(login_url='/uac/login/')
@permission_required('masters.delete_clients', login_url='/uac/error/')	
def delete_clients(request, id):
	ClientsERP.objects.filter(client_id=id).delete()	
	ClientsTools.objects.filter(client_id=id).delete()	
	Clients.objects.filter(client_id=id).delete()	
	return redirect('/uac/masters/clients')
	

@login_required(login_url='/uac/login/')	
def get_client(request):
	
	data = Clients.objects.filter(Q(client_id=request.GET.get('cid')))
	response_data={}
	response_data=  serializers.serialize('json', data)
	return JsonResponse(response_data,safe=False)
	
@login_required(login_url='/uac/login/')	
def get_client_erp(request):	
	data_erp = Erp.objects.values_list('erp_id', 'erp_name')
	data_tool = Tool.objects.values_list('tool_id', 'tool_name')
	js={'erp':list(data_erp),'tool':list(data_tool)}
	return JsonResponse(js,safe=False)
	
	
@login_required(login_url='/uac/login/')	
def client_erp_save(request):	
	json_data = request.GET.get('formdata')
	data = json.loads(json_data)
	msg=''
	cid=''
	status ='400'
	client_name = data['ClientName']	
	short_name = data['ShortName']	
	user_name = data['UserName']
	erp = data['ERP']
	clients_details =  data['Clients']
	client_email = data['Email']
	id=request.user.id
	user=User.objects.get(id=id)
	if user.has_perm('masters.new_client'):
		try:
			data=Clients(
			client_name  = client_name,
			client_short  = short_name,
			user_name = user_name,
			client_email = client_email,
			entry_by = request.user.id)
			data.save()	
			cid=Clients.objects.latest('client_id')			
			

			for x in erp:
				ds=ClientsERP(		
				client_id = cid.client_id,
				erp_id = x,
				user_id =  request.user.id)
				ds.save()		
				
			for key in clients_details:
				ds=ClientsTools(
				client_id = cid.client_id,
				tool_id = key['DestTool'],
				sftp_server = key['Ftp'],
				sftp_user = key['Username'],
				# sftp_pwd =ProcessFile.uac_Encrypt(bytes(key['Password'],'utf-8'), settings.ENCRY_KEY),

				sftp_pwd = key['Password'] ,
				sftp_port = key['SftpPort'],
				sftp_in = key['InFolder'],
				sftp_out = key['OutFolder'],			
				user_id =  request.user.id)
				ds.save()	
			msg ='Records has been Saved !'			
			status='200'

		except Exception as e:
			if str(e) == "UNIQUE constraint failed: uac_erp_clients.client_email":
				msg = "Error Occurred: Email already exist"
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
def client_erp_update(request):	
	json_data = request.GET.get('formdata')
	data = json.loads(json_data)
	msg=''	
	status ='400'
	client_name = data['ClientName']	
	short_name = data['ShortName']	
	user_name = data['UserName']
	erp = data['ERP']
	clients_details =  data['Clients']
	cid =  data['cid']
	email= data['Email']
	id=request.user.id
	user=User.objects.get(id=id)
	if user.has_perm('masters.change_clients'):	
		try:
		
			data=Clients.objects.get(client_id=cid)
			#product.name = 'Name changed again'
			#product.save(update_fields=['name'])
			data.client_name  = client_name
			data.client_short  = short_name
			data.user_name = user_name
			data.client_email = email
			data.save()
			ClientsERP.objects.filter(client_id=cid).delete()	
			ClientsTools.objects.filter(client_id=cid).delete()			
			for x in erp:
				ds=ClientsERP(		
				client_id = cid,
				erp_id = x,
				user_id =  request.user.id)
				ds.save()			
			for key in clients_details:
				ds=ClientsTools(
				client_id = cid,
				tool_id = key['DestTool'],
				sftp_server = key['Ftp'],
				sftp_user = key['Username'],
				sftp_pwd = key['Password'],
				# sftp_pwd =ProcessFile.uac_Encrypt(bytes(key['Password'],'utf-8'), settings.ENCRY_KEY),
				sftp_port = key['SftpPort'],
				sftp_in = key['InFolder'],
				sftp_out = key['OutFolder'],			
				user_id =  request.user.id)
				ds.save()		
			msg ='Records has been Updated !'			
			status='200'
		except Exception as e:
			msg = "Error Occurred: " + str(e)
			status = '400'
		finally:	
			js = {'message':msg,'status':status,'t':client_name}
			return JsonResponse(js)
	else:
            message = {"message": "User permission denied.","status": "400"}
            return JsonResponse(message) 
	
	
@login_required(login_url='/uac/login/')
def search_clients(request):
	fname = request.GET['search']
	qry='%' + fname + '%'
	
	#filedata = list(Clients.objects.raw(''' SELECT A.source_file_id ,A.source_file_name,B.erp_name FROM uac_source_file A, uac_source_erp B WHERE A.erp_id=B.erp_id
	 #AND (A.source_file_name LIKE %s OR B.erp_name LIKE %s) ''', [qry,qry]))
	clientdata = list(Clients.objects.raw('''select uac_erp_clients.client_id,uac_erp_clients.client_name,uac_erp_clients.client_short,
	uac_source_erp.erp_name,uac_destination_tool.tool_name,uac_erp_clients.sftp_server,
	uac_erp_clients.sftp_in,uac_erp_clients.sftp_out from	uac_erp_clients  LEFT JOIN uac_source_erp ON uac_erp_clients.erp_id= uac_source_erp.erp_id 
	LEFT JOIN uac_destination_tool ON uac_erp_clients.tool_id= uac_destination_tool.tool_id 
	WHERE (uac_destination_tool.tool_name LIKE %s OR uac_source_erp.erp_name LIKE %s OR uac_erp_clients.client_short LIKE %s OR uac_erp_clients.client_name LIKE %s) ''', [qry,qry,qry,qry])) 
	 
	page = request.GET.get('page', 1)
	paginator = Paginator(clientdata, 20)
	
	try:
		client = paginator.page(page)
	except PageNotAnInteger:
		client = paginator.page(1)
	except EmptyPage:
		client = paginator.page(paginator.num_pages)

	#to populate ERP in  combo 
	erpdata = Erp.objects.all()
	#to populate dest tools in  combo
	tooldata = Tool.objects.all()
	
	return render(request, 'etl/uac_addclients.html', {'clients': client,'erps': erpdata,'tools':tooldata})	

def client_check(request):
	name = request.POST.get('name')
	item_id = request.POST.get('id',None)
	if (item_id):
		sample = Clients.objects.filter(client_short = name)
		rule_name=sample.exclude(client_id=item_id)
	else:
		rule_name = Clients.objects.filter(client_short = name)
	if rule_name:
		found = True
	else:
		found = False	
	js = {'success' : found}		
	return JsonResponse(js)	