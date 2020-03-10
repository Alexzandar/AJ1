import os
import paramiko
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from masters.models import Clients
from masters.models import DestinationFile as df
from masters.models import DestinationTools as dt
from masters.models import ETLProcessLogs
from masters.models import Erp, ClientsERP
from django.views.generic import View
from rest_framework.decorators import permission_classes
from utils.generic_utils import FileTransform
from utils.utils import ProcessFile
import requests
from masters.models import ClientExtractSettings 

from .serializers import APISerializer
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import json
import calendar
from masters.models import ClientsTools as dv
from utils.authentication import SessionTokenAuthentication




@login_required(login_url='/uac/login/')
def process(request):
    # authentication_classes = (SessionTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    
    clients = Clients.objects.values('client_id', 'client_name')
    dest_file = df.objects.values('dest_file_id', 'dest_file_name')
    dest_tool = dt.objects.values('tool_id', 'tool_name')
    filename_start = ClientExtractSettings.objects.values('settings_id','file_name_start')
    return render(request, 'etl/uac_process.html', {'clients': clients, 'df': dest_file, 'dt': dest_tool, 'filename_start' : filename_start})


@login_required(login_url='/uac/login/')
def cleansing(request):
    host = '103.21.58.16'
    port = 22
    username = 'dairyaty'
    password = 'F9&+5%l7eE6e'
    client, message = create_sftp_client(host, port, username, password)

    if not client:
        return JsonResponse({
            'message': message,
            'status': 400
        })
    process_log = ProcessLogs(client_id=1, dest_file_id=1, tool_id=1, user_id=1)
    process_log.save()
    date = datetime.now().strftime("%Y%m%dT%H%M%S")
    filename = 'new_GL_clean_file' + date + '.txt'
    client.get('testing/in/GL_Balance.txt', filename)
    config_JSON = '{"filename": "GL Balance", "clientid": "2", "clientname": "Kohler", "sourcefile": "GL Balance", "dest_tool": "Cadency", "unique_column": ["CoCode", "Transaction Amount"],"validation_rules": [{"fldreq": "Y", "fldtype": "Integer", "fldname": "CoCode", "fldlen": "6"}, {"fldreq": "Y", "fldtype": "Integer", "fldname": "G/L Account", "fldlen": "6"}, {"fldreq": "Y", "fldtype": "Integer", "fldname": "Segment", "fldlen": "6"}, {"fldreq": "N", "fldtype": "Integer", "fldname": "Profit Centre", "fldlen": "6"}, {"fldreq": "Y", "fldtype": "Integer", "fldname": "Fiscal Year", "fldlen": "6"}, {"fldreq": "Y", "fldtype": "Integer", "fldname": "Period", "fldlen": "2"}], "transform_rules": [{"column": "Fiscal Year", "rules": ["remove_column"], "filename": "GL Balance"}, {"column": "G/L Acc.Description", "rules": ["remove_leading_space"], "filename": "GL Balance"}, {"column": "Profit Center", "rules": ["empty_to_zero"], "filename": "GL Balance"}, {"column": "Transaction Amount", "rules": ["replace_values"], "filename": "GL Balance"}]}'
    config_JSON = '{"transform_rules": [{"column": "date", "rules": ["remove_leading_space"]}, {"column": "fromcurrency", "rules": ["remove_leading_space", "remove_trailing_space"]}], "validation_rules": [{"column": "date", "type": "Text", "length": 0, "required": 1}, {"column": "fromcurrency", "type": "Currency", "length": 0, "required": 1}, {"column": "tocurrency", "type": "Currency", "length": 0, "required": 0}, {"column": "exrate", "type": "Currency", "length": 0, "required": 0}, {"column": "typeid", "type": "Numeric", "length": 0, "required": 0}]}'
    f = FileTransform(filename, config_JSON)
    os.remove(filename)

    if f.validate():
        status_code, message, cleaned_file_name = f.process()
        if status_code == 200:
            process_log.save()
            client.put(cleaned_file_name, 'testing/out/' + filename)
            os.remove(cleaned_file_name)
            return JsonResponse({'message': message, 'status': status_code})
        else:
            process_log.status = "N"
            process_log.save()
            return JsonResponse({'message': message, 'status': status_code})
    else:
        errors = f.validation_errors
        process_log.completed = "N"
        process_log.save()
        return JsonResponse({'message': errors, 'status': 400})

    if not client:
        return JsonResponse({
            'message': message,
            'status': 400
        })


def create_sftp_client(_host, _port, _username, _password, key_file_path=None, key_file_type='RSA'):
    sftp = None
    key = None
    transport = None
    try:
        if key_file_path:
            if key_file_type == 'DSA':
                key = paramiko.DSSKey.from_private_key_file(key_file_path)
            else:
                key = paramiko.RSAKey.from_private_key(key_file_path)
        transport = paramiko.Transport((_host, _port))
        passwrd = ProcessFile.uac_decrypt(_password, ENCRY_KEY)
        transport.connect(None, _username, passwrd, key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp, "Success message!!!"
    except Exception as e:
        print('An error occurred creating SFTP client: %s: %s' % (e.__class__, e))
        if sftp:
            sftp.close()
        if transport:
            transport.close()
        return None, "Unable to establish a secure connection with the server!!!"


import pandas as pd

from rest_framework.views import APIView
from rest_framework.response import Response


class JSONUpload(APIView):
    # authentication_classes = (SessionTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = pd.DataFrame.from_dict(dict(request.data['fileData']))
        config_JSON = '{"filename": "GL Balance", "clientid": "2", "clientname": "Kohler", "sourcefile": "GL Balance", "dest_tool": "Cadency", "unique_column": ["CoCode", "Transaction Amount"],"validation_rules": [{"fldreq": "Y", "fldtype": "Integer", "fldname": "CoCode", "fldlen": "6"}, {"fldreq": "Y", "fldtype": "Integer", "fldname": "G/L Account", "fldlen": "6"}, {"fldreq": "Y", "fldtype": "Integer", "fldname": "Segment", "fldlen": "6"}, {"fldreq": "N", "fldtype": "Integer", "fldname": "Profit Centre", "fldlen": "6"}, {"fldreq": "Y", "fldtype": "Integer", "fldname": "Fiscal Year", "fldlen": "6"}, {"fldreq": "Y", "fldtype": "Integer", "fldname": "Period", "fldlen": "2"}], "transform_rules": [{"column": "Fiscal Year", "rules": ["remove_column"], "filename": "GL Balance"}, {"column": "G/L Acc.Description", "rules": ["remove_leading_space"], "filename": "GL Balance"}, {"column": "Profit Center", "rules": ["empty_to_zero"], "filename": "GL Balance"}, {"column": "Transaction Amount", "rules": ["replace_values"], "filename": "GL Balance"}]}'
        f = FileTransform(json_=config_JSON, df_data=data)
        if f.validate():
            status_code, message, cleaned_file_name = f.process()
            if status_code == 200:
                # process_log.save()
                host = 'uac-cus-ftp1.ttech.cadency.host'
                port = 2200
                username = 'sftpuser'
                password = 'qwerty123'
                client, message = create_sftp_client(host, port, username, password)
                date = datetime.now().strftime("%Y%m%dT%H%M%S")
                filename = 'GL_clean_file' + date + 'api.txt'
                client.put(cleaned_file_name, 'out/' + filename)
                os.remove(cleaned_file_name)
                return JsonResponse({'message': message, 'status': status_code})
            else:
                
                
                return JsonResponse({'message': message, 'status': status_code})
        else:
            errors = f.validation_errors
            return JsonResponse({'message': errors, 'status': 400})
        return Response({'message': 'Processing JSON '})

# @permission_classes((IsAuthenticated,))
class TestClass(View):
    # authentication_classes = (SessionTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    
    '''authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)'''
    # authentication_classes = [SessionTokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        uid=request.user.id
        client_id =  request.GET.get('cid')
        tool_id = 1
        destination_file_id =  request.GET.get('destid')
                
                
        process_files = ProcessFile(client_id, tool_id, destination_file_id, file_start)
        message = process_files.process()
        del process_files
        return JsonResponse({'message': message, 'status': 200})

    def post(self, request):

        # uid=request.user.id
        # user=User.objects.get(id=uid)
        # if user.has_perm('masters.etl_process'):
        s=True
        if s:
            client_id = request.POST.get('client')
            

            tool_id = request.POST.get('tool')

            file_start_settings_id =request.POST.get('file_start')
            erp_id = request.POST.get('erp')

            file_start = ClientExtractSettings.objects.get(settings_id=file_start_settings_id).file_name_start
            destination_file_id = request.POST.get('destfile')

            method = request.POST.get('method')
            uid= 1
            # print(file_start, method, client_id, tool_id, destination_file_id, erp_id, uid)
            process_files = ProcessFile(file_start, method, client_id, tool_id, destination_file_id, erp_id, uid)
            message = process_files.process()
            message ={'message':message, 'status':200}
            return JsonResponse(message)

        else:
            message = [{"message": "User permission denied.","status": 401}]
            message = {"message":message}
            return JsonResponse(message)        



class TestAuthentication(APIView):

    authentication_classes = (SessionTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # def get(self, request):
    #     content = {
    #         'user': str(request.user),  # `django.contrib.auth.User` instance.
    #         'auth': str(request.auth),  # None, '29KVWNcHep'
    #     }
    #     return Response(data=content)

    def post(self, request):
        uid=request.user.id
        d = datetime.utcnow()
        p_id = calendar.timegm(d.utctimetuple())
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        tool = request.data.get('aid')
        destination_file = request.data.get('type')
        system_id = request.data.get('sid')
        config_id=request.data.get('cid')
        # erp =request.data.get('erp')

        serializer = APISerializer(data={'tool': tool, 'destination_file': destination_file})
        
    
        if serializer.is_valid():
            client_id = Clients.objects.get(user_id=request.user).client_id
            method ="API"
            erp_id ="1"
            tool_id = dt.objects.get(tool_short=tool).tool_id
            destination_file_id = df.objects.get(dest_short=destination_file).dest_file_id
            file_start = destination_file + '_' + system_id 
            file_cid =destination_file + '_' + system_id + '_' + config_id
            # print(file_cid)


            data = pd.DataFrame.from_dict(dict(request.data['filedata']))
            file_ = ProcessFile(file_start, method, client_id, serializer.validated_data['tool'], serializer.validated_data['destination_file'], erp_id, uid, file_data=data, extractor=destination_file,sid=system_id, cid=config_id, file_cid=file_cid )
            message = file_.api_process()
            client_short=Clients.objects.get(user_id=request.user).client_short
            status_code = message.get('status')
            d = datetime.utcnow()
            p_id = calendar.timegm(d.utctimetuple())
            message = message.get('message')
            if status_code == 200:

                
                # self.sumo_msg_api =[{"project":"UAC","exec_method":"API","exec_type":method,"user_id":1,"activity":"ETL Process","dest_file":destination_file,"dest_tool" :tool ,"client_id":client_short,"pid":p_id,"p_timestamp":date,"message":message,"rec_file_name": "API","trans_file_name":"API","status": 400}]
                # r = requests.post(settings.END_POINT, data = json.dumps(self.sumo_msg_api))
                return JsonResponse({'message': message, 'status': 200})

                
            else:
                # process_log = ETLProcessLogs(p_timestamp=date,exec_method ="API",exec_type=method,client_id=client_id, dest_file_id=destination_file_id,tool_id=tool_id, settings_id="0",rec_file_name="API",rec_file_checksum="0",
                # trans_file_name="API",trans_file_checksum="0",status=400,response=message, user=uid)
                # process_log.save()
                return JsonResponse({'message': message, 'status': 400})
        else:
            
            # client_short=Clients.objects.get(user_id=request.user).client_short
            # client_id=Clients.objects.get(user_id=request.user).client_id
            # tool_id = dt.objects.get(tool_short=tool).tool_id
            # file_start = destination_file + '_' + system_id 
            
            # destination_file_id = df.objects.get(dest_short=destination_file).dest_file_id
            # setting_id= ClientExtractSettings.objects.get(client_id=client_id, tool_id=tool_id,
            #                                        dest_file_id=destination_file_id, file_name_start=file_start).settings_id
            # file= destination_file + '_' + system_id + '_' + config_id + '_' + date + '.txt'
        
            # self.sumo_msg_api =[{"project":"UAC","exec_method":"API","exec_type":"API","user_id":1,"activity":"ETL Process","dest_file":destination_file,"dest_tool" :tool ,"client_id":client_short,"pid":p_id,"p_timestamp":date,"message":serializer.errors,"rec_file_name": "API","trans_file_name":"API","status": 400}]
            
            # r = requests.post(settings.END_POINT, data = json.dumps(self.sumo_msg_api))
            # process_log = ETLProcessLogs(p_timestamp=date,exec_method ="API",exec_type=method,client_id=client_id, dest_file_id=destination_file_id,tool_id=tool_id, settings_id=settings_id,rec_file_name=file, rec_file_checksum="",
            #     trans_file_name=file,trans_file_checksum="",status=400, user=uid)
            # process_log.save()
            return JsonResponse({'error': serializer.errors, 'status': 400})

# @login_required(login_url='/uac/login/')
# @permission_classes((IsAuthenticated,))
class ETL_define_rule(View):

    # authentication_classes = (SessionTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    
    def get(self, request):

        
        Id =(request.GET.get('Id'))
        typ =(request.GET.get('typ'))
        param1 =(request.GET.get('param1'))
        param2 =(request.GET.get('param2'))

        
        if(typ=='Client'): 
            tool =list(ClientExtractSettings.objects.raw('''SELECT uac_client_settings_master.settings_id,uac_source_erp.erp_id AS id,uac_source_erp.erp_name AS name FROM uac_source_erp LEFT JOIN uac_client_settings_master ON uac_source_erp.erp_id=uac_client_settings_master.erp_id WHERE (uac_client_settings_master.client_id= %s)GROUP by uac_client_settings_master.erp_id''', [Id]))
        elif(typ=='ERP'):
            tool = list(ClientExtractSettings.objects.raw('''SELECT uac_client_settings_master.settings_id, uac_destination_tool.tool_id AS id,uac_destination_tool.tool_name AS name FROM uac_client_settings_master INNER JOIN uac_destination_tool ON uac_client_settings_master.tool_id=uac_destination_tool.tool_id WHERE (uac_client_settings_master.client_id = %s and uac_client_settings_master.erp_id = %s) GROUP by uac_destination_tool.tool_id''',[param1,Id]))
            
        elif(typ=='Tool'):
            tool = list(ClientExtractSettings.objects.raw('''SELECT uac_client_settings_master.settings_id, uac_destination_file.dest_file_id AS id,uac_destination_file.dest_file_name AS name FROM uac_client_settings_master INNER JOIN uac_destination_file ON uac_client_settings_master.dest_file_id=uac_destination_file.dest_file_id WHERE (uac_client_settings_master.client_id = %s and uac_client_settings_master.erp_id = %s)GROUP by uac_destination_file.dest_file_id''',[param1,param2]))
        
        data = []
        for i in tool:
           
            data.append({'name':i.name,'id':i.id})
        return JsonResponse ({'data':data})
# @permission_classes((IsAuthenticated,))
class ETL_file_start(View):
    # authentication_classes = (SessionTokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
    def get(self, request):

        

        client_id =(request.GET.get('extId'))
        tool_id=(request.GET.get('toolId'))
        clt_id=(request.GET.get('clientId'))
        erp_id= (request.GET.get('erpId'))

        tool = ClientExtractSettings.objects.raw('''SELECT * FROM uac_client_settings_master WHERE (client_id = %s and tool_id = %s and dest_file_id = %s and erp_id = %s )''', [clt_id,tool_id,client_id,erp_id])
        data=[]
        for i in tool:
            
            data.append({ 'file_name_start':i.file_name_start,'tool_id':i.settings_id })
            

        return JsonResponse ({'tool':data,'tool_id':i.settings_id})





