from django.http import *
import sys
from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required

import json
import numpy as np
from django.conf import settings
from django.core import serializers


from django.db.models import Q
from masters.models import Erp
from masters.models import DestinationFile as df
from masters.models import DestinationTools as Tool
from masters.models import Clients 

from django.db import connection


@login_required(login_url='/uac/login/')
def getMISdata(request):
	#No. Of Extractors Processed
	sql ="SELECT A.dest_short, COUNT(B.etl_id) as Nos FROM   uac_destination_file A, uac_etl_logs B WHERE  A.dest_file_id = B.dest_file_id GROUP BY A.dest_short;"
	cursor = connection.cursor()
	cursor.execute(sql)
	records=cursor.fetchall()
	arrMIS= np.array(records)
	extractos=arrMIS[:,0]
	ex_nos=arrMIS[:,1]
	#No. Of Extractors Processed by Client
	sql ="SELECT A.client_short, COUNT(B.etl_id) as Nos FROM   uac_erp_clients A, uac_etl_logs B WHERE  A.client_id = B.client_id GROUP BY A.client_short;"
	cursor = connection.cursor()
	cursor.execute(sql)
	records=cursor.fetchall()
	arrMIS= np.array(records)
	clients=arrMIS[:,0]
	client_nos=arrMIS[:,1]
	#Suceess /Fail Count - Pie Chart
	sql="SELECT CASE status WHEN 200 THEN 'Success' ELSE 'Fail' END Stat,COUNT(etl_id) as nos FROM uac_etl_logs GROUP BY status"
	cursor = connection.cursor()
	cursor.execute(sql)
	records=cursor.fetchall()
	arrMIS= np.array(records)
	status=arrMIS[:,0]
	status_nos=arrMIS[:,1]
	#Type of Execution - Pie Chart
	sql="SELECT exec_type,COUNT(etl_id) as nos FROM uac_etl_logs GROUP BY exec_type"
	cursor = connection.cursor()
	cursor.execute(sql)
	records=cursor.fetchall()
	arrMIS= np.array(records)
	exectype=arrMIS[:,0]
	execnos=arrMIS[:,1]
	return JsonResponse({'Ext': extractos.tolist() ,'ExtNos':ex_nos.tolist(),'Clients': clients.tolist() ,'ClientNos':client_nos.tolist(),'ResultStatus':status.tolist(),'StatusNos':status_nos.tolist(),'ExecType': exectype.tolist(),"ExecNos":execnos.tolist()})
	
