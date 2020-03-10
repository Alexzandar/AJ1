from datetime import datetime
import sqlite3
import requests
import json
from requests.auth import HTTPBasicAuth


conn = sqlite3.connect('../dbuac_v15.sqlite3')
cursor = conn.cursor()

now = datetime.now()

dt=now.strftime("%Y-%m-%d")
#cursor.execute("SELECT * FROM uac_clients_tools WHERE client_id=(?) AND tool_id=(?)",(ClientId,ToolId,))


#### Read Scheduler Config File


# cursor.execute("SELECT client_id, dest_file_id, tool_id, erp_id, file_name_start FROM uac_scheduler_config WHERE date_from <=(?) AND active='Y'",(dt,))
cursor.execute("SELECT S.client_id, S.dest_file_id, S.tool_id, S.erp_id, S.file_name_start,M.file_name_start FROM uac_scheduler_config  S INNER JOIN uac_client_settings_master M  on S.file_name_start=M.settings_id WHERE S.date_from <=(?) AND S.active='Y'",(dt,))
records=cursor.fetchall()
# endpoint_url='http://uac-ny1-dev1.ttech.cadency.host/uac/process/test/'
endpoint_url='http://localhost:8000/uac/process/test/'

for Arr in records:		
	# print(Arr[0],Arr[1], Arr[2])
	r = requests.post(url = endpoint_url,data= {'client':Arr[0],'file_start':Arr[4],'destfile':Arr[1],'tool':Arr[2],'erp':Arr[3],'method':'SCHEDULER'})
	s =json.dumps(r.text)
	# print(r.text)