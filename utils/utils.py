import os
import json
import stat
import fnmatch
import logging
import paramiko
import hashlib
import numpy as np
import pandas as pd
from django.core.mail import send_mail
from django.template import loader
# from Crypto import Random
# from Crypto.Cipher import AES
from datetime import datetime
from django.db import connection
from django.conf import settings
from rest_framework.views import APIView
from .generic_utils import FileTransform
from masters.models import ClientsTools, ClientExtractSettings, ClientExtractorDetails, DestinationRules, RulesetDetails, RulesetMaster
from masters.models import Clients, DestinationTools, DestinationFile, ETLProcessLogs
import requests
import calendar
# from Crypto import Random
# from Crypto.Cipher import AES

cursor = connection.cursor()


class ProcessFile(object):
    sftp = None
    sftp_host = None
    sftp_user = None
    sftp_password = None
    sftp_port = None
    sftp_in = None
    sftp_out = None
    sftp_key = None

    set_id = None
    rule_set_id = None
    file_type = None
    # file_start = None
    delimiter = None

    source_columns = []
    destination_columns = []
    source_columns_wo_blank = []
    source_columns_required = []
    blank_columns = []
    db_rules = []
    mandatory_source_columns = []

    def __init__(self,file_start, method, client_id, tool_id, destination_file_id,erp_id, uid, file_cid=None, file_data=None, extractor=None, sid=None,cid=None):
        
        self.sftp = None
        self.sftp_host = None
        self.sftp_user = None
        self.sftp_password = None
        self.sftp_port = None
        self.sftp_in = None
        self.sftp_out = None
        self.sftp_key = None

        self.set_id = None
        self.rule_set_id = None
        self.file_type = None
        self.delimiter = None
        
        self.source_columns = []
        self.destination_columns = []
        self.source_columns_wo_blank = []
        self.source_columns_required = []
        self.blank_columns = []
        self.db_rules = []
        self.file_start = file_start
        self.erp_id = erp_id
        self.client_id = client_id
        self.tool_id = tool_id
        self.destination_file_id = destination_file_id
        self.file_data = file_data
        self.file_ = ''
        self.method = method
        self.extractor = extractor
        self.sid = sid
        self.cid = cid
        self.uid= uid
        self.file_cid= file_cid
        self.separator = '\t'
        self.config_JSON = {}
        self.source_destination_map = {}

        self.files_to_be_processed = []
        self.messages = []
        self.sumo_msg = []
        self.sumo_msg_api=[]
        

    def process(self):
        try:
            self.check_connected()
        except:
            return[{"message": "Unable to connect internet", "status":401}]

        try:
            self.get_sftp_credentials()
        except:
            return [{"message":"Unable to fetch SFTP credentials.","filename":"FILE","status":401}]
        try:
            self.establish_sftp_connection()
        except:
            return [{"message":"Unable to establish a secure SFTP connection.","filename":"FILE","status":401}]   
        try:
            self.get_current_extractor()
        except:
            return [{"message":"Unable to fetch Client Extractor settings.","filename":"FILE","status":401}]
        try:
            self.get_required_IN_folder()
        except:
            return [{"message":"Unable to find the IN folder.","filename":"FILE","status":401}]
        try:
            self.get_required_OUT_folder()
        except:
            return [{"message":"Unable to find the OUT folder.","filename":"FILE","status":401}]                
        try:
            self.get_required_files()
        except:
            return [{"message":"Unable to read the files from SFTP location","filename":"FILE","status":401}]
        try:
            self.get_extractor_details()
        except:
            return [{"message":"Unable to fetch Client Extractor Details.","filename":"FILE","status":401}]
            
        if not self.destination_columns:
            return [{"message":"Destination columns not configured.","filename":"FILE","status":401}]
            
        self.build_columns_list()
        self.build_configuration()

        if not self.files_to_be_processed:
            return [{"message":"Unable to find any files with the given specification. Please check the configurations.","status":401}]
            
            
        
        d = datetime.utcnow()
        p_id = calendar.timegm(d.utctimetuple())
        
        for file_ in self.files_to_be_processed:
            
            date1 = datetime.now().strftime("%Y%m%d%H%M%S")
            
            local_file = 'TMP_' + file_
            remote_file = self.sftp_in + '/' + file_
            self.sftp.get(remote_file, local_file)
            # self.validate_checksum()
            # md5_checksum= self.md5(local_file)
 
            client1 = Clients.objects.get(client_id=self.client_id).client_short
            tool1 = DestinationTools.objects.get(tool_id=self.tool_id).tool_short
            destfile1 = DestinationFile.objects.get(dest_file_id=self.destination_file_id).dest_short
            client_ext_settings = ClientExtractSettings.objects.get(client_id=self.client_id, tool_id=self.tool_id,dest_file_id=self.destination_file_id, erp_id=self.erp_id, file_name_start=self.file_start).settings_id
            data = pd.read_csv(local_file, sep=self.separator, dtype=str)
            missing_source_columns = [column_name for column_name in self.source_columns_wo_blank if column_name not in list(data.columns)]
            if missing_source_columns:
                data[[str(i) for i in missing_source_columns]] = pd.DataFrame(
                    [[np.nan for i in missing_source_columns]])
        
            data = data[self.source_columns_wo_blank]
            data.columns = self.source_columns_required
            data = data.reindex(columns=[*data.columns.tolist(), *self.blank_columns])
            # missing columns
            missing_columns = list(set(self.destination_columns) - set(data.columns))
            if missing_columns:
                data[missing_columns] = pd.DataFrame([['' for i in range(len(missing_columns))]], index=data.index)
            data = data[self.destination_columns]

            local_processed_file = 'processed_' + file_

            f = FileTransform(json_=json.dumps(self.config_JSON), df_data=data, output_file=local_processed_file)
            if f.validate():
                client_email= Clients.objects.get(client_id=self.client_id).client_email
                print(client_email)
                status_code, message, cleaned_file_name = f.process()
                if status_code == 200:
                    self.sftp.put(cleaned_file_name, self.sftp_out + '/' + file_)
                    
                    self.sumo_msg =[{"project":"UAC","exec_method":"File","exec_type":self.method,"settings_id":client_ext_settings,"user_id":self.uid,"activity":"ETL Process","dest_file":destfile1,"dest_tool":tool1,"client_id":client1,"pid":p_id,"p_timestamp":date1,"message": message, "rec_file_name": file_,"trans_file_name":file_, "status": status_code}]
                    self.messages.append({"message": message, "filename": file_, "status": status_code})
                    process_log = ETLProcessLogs(p_timestamp=date1,exec_method ="File",exec_type=self.method,client_id=self.client_id,dest_file_id=self.destination_file_id,tool_id=self.tool_id, settings_id=client_ext_settings,rec_file_name=file_,rec_file_checksum="",
                        trans_file_name=file_,trans_file_checksum="",status=200,response=message, user=self.uid)
                    
                   
                    os.remove(cleaned_file_name)
                else:
                    # print("##########################")
                    self.sumo_msg =[{"project":"UAC","exec_method":"File","exec_type":self.method,"settings_id":client_ext_settings,"user_id":self.uid,"activity":"ETL Process","dest_file":destfile1,"dest_tool":tool1,"client_id":client1,"pid":p_id,"p_timestamp":date1,"message": message, "rec_file_name": file_,"trans_file_name":file_, "status": status_code}]
                    # send_mail('UAC Process Notification', '', settings.APP_NAME+' <do_not_reply@domain.com>', [
                    #   client_email], fail_silently=True)
                    print(file_)
                    client_name =client1 = Clients.objects.get(client_id=self.client_id).client_name
                    html_message = loader.render_to_string(
                        'etl/uac_process_email.html',
                        {'app_name': settings.APP_NAME,'message': message,'user_name':client_name,'file':file_,
                        'login_url': settings.BASE_URL}
                    )

        
                    send_mail('UAC Process Failed', '', settings.APP_NAME+' <do_not_reply@domain.com>', [
                      client_email], fail_silently=True, html_message=html_message)
                    self.messages.append({"message": message, "filename": file_, "status": status_code})
                    process_log = ETLProcessLogs(p_timestamp=date1,exec_method ="File",exec_type=self.method,client_id=self.client_id,dest_file_id=self.destination_file_id,tool_id=self.tool_id, settings_id=client_ext_settings,rec_file_name=file_,rec_file_checksum="",
                        trans_file_name=file_,trans_file_checksum="",status=400,response=message, user=self.uid)
                              
            else:
                

                errors = f.validation_errors
                print(errors)
                print(file_)
                client_name = Clients.objects.get(client_id=self.client_id).client_name
                client_email = Clients.objects.get(client_id=self.client_id).client_email
                html_message = loader.render_to_string(
                        'etl/uac_process_email.html',
                        {'app_name': settings.APP_NAME,'message': errors,'username':client_name,'file':file_,
                        'login_url': settings.BASE_URL}
                    )

        
                send_mail('UAC Process Warning', '', settings.APP_NAME+' <do_not_reply@domain.com>', [
                      client_email], fail_silently=True, html_message=html_message)
                self.sumo_msg =[{"project":"UAC","exec_method":"File","exec_type":self.method,"settings_id":client_ext_settings,"user_id":self.uid,"activity":"ETL Process","dest_file":destfile1,"dest_tool":tool1,"client_id":client1,"pid":p_id,"p_timestamp":date1,"message": errors, "rec_file_name": file_, "trans_file_name":file_,"status": 400}]
                
                self.messages.append({"message": errors, "filename": file_, "status": 400})
                process_log = ETLProcessLogs(p_timestamp=date1,exec_method ="File",exec_type=self.method,client_id=self.client_id,dest_file_id=self.destination_file_id,tool_id=self.tool_id, settings_id=client_ext_settings,rec_file_name=file_,rec_file_checksum="",
                trans_file_name=file_,trans_file_checksum="",status=400,response=errors, user=self.uid)
                
            r = requests.post( settings.END_POINT, data = json.dumps(self.sumo_msg)) 
            
                        
            os.remove(local_file)
            process_log.save()
        return self.messages
            

    def api_process(self):
        # try:
        #     self.check_connected()
        # except:
        #     return[{"message": "Unable to connect internet", "status":401}]

        try:
            self.get_sftp_credentials()
        except:
            
            return {"message":"Unable to fetch SFTP credentials.","filename":"API","status":401}
        try:
            self.establish_sftp_connection()
        except:
            return {"message":"Unable to establish a secure SFTP connection.","filename":"API","status":401}
        try:
            self.get_current_extractor_api()
        except:
            return {"message": "Unable to fetch Client Extractor settings.","filename":"API", "status": 401}
        try:
            self.get_required_IN_folder()
        except:
            return {"message":"Unable to find the IN folder.","filename":"API","status":401}
        try:
            self.get_required_OUT_folder()
        except:
            return {"message":"Unable to find the OUT folder.","filename":"API","status":401}
        
        try:
            self.get_extractor_details()
        except:
            return {"message": "Unable to fetch Client Extractor Details.","filename":"API", "status": 401}
        if not self.destination_columns:
            return {"message": "Destination columns not configured.","filename":"API", "status": 401}
        self.build_columns_list()
        self.build_configuration()
        # print(self.file_cid)
        client1 = Clients.objects.get(client_id=self.client_id).client_short
        tool1 = DestinationTools.objects.get(tool_id=self.tool_id).tool_short
        client_ext_settings = ClientExtractSettings.objects.get(client_id=self.client_id, tool_id=self.tool_id,dest_file_id=self.destination_file_id, file_name_start=self.file_start).settings_id
        data = pd.DataFrame.from_dict(self.file_data)
        d = datetime.utcnow()

        p_id = calendar.timegm(d.utctimetuple())
        missing_source_columns = [column_name for column_name in self.source_columns_wo_blank if
                                  column_name not in list(data.columns)]
        if missing_source_columns:
            data[[str(i) for i in missing_source_columns]] = pd.DataFrame([[np.nan for i in missing_source_columns]])

        data = data[self.source_columns_wo_blank]
        data.columns = self.source_columns_required
        data = data.reindex(columns=[*data.columns.tolist(), *self.blank_columns])
        # missing columns
        missing_columns = list(set(self.destination_columns) - set(data.columns))
        if missing_columns:
            data[missing_columns] = pd.DataFrame([['' for i in range(len(missing_columns))]], index=data.index)
        data = data[self.destination_columns]

        f = FileTransform(json_=json.dumps(self.config_JSON), df_data=data)
        if f.validate():
            date = datetime.now().strftime("%Y%m%d%H%M%S")
            self.file_ += self.extractor + '_' + self.sid + '_' + self.cid + '_' + date + '.txt'
            status_code, message, cleaned_file_name = f.process()
            if status_code == 200:
                self.sftp.put(cleaned_file_name, self.sftp_out + '/' + self.file_)
                self.sumo_msg_api =[{"project":"UAC","exec_method":"API","exec_type":"API","user_id":1,"activity":"ETL Process","dest_file":self.extractor,"dest_tool":tool1,"client_id":client1,"pid":p_id,"p_timestamp":date,"message": message, "rec_file_name": self.file_ ,"trans_file_name":self.file_ , "status": status_code}]
                

                r = requests.post(settings.END_POINT, data = json.dumps(self.sumo_msg_api))
    
                os.remove(cleaned_file_name)
                process_log = ETLProcessLogs(p_timestamp=date,exec_method ="API",exec_type=self.method,client_id=self.client_id,dest_file_id=self.destination_file_id,tool_id=self.tool_id, settings_id=client_ext_settings,rec_file_name=self.file_,rec_file_checksum="",
                trans_file_name=self.file_,trans_file_checksum="",status=200, response=message, user=self.uid)
                process_log.save()
                return {"message": message, "filename": self.file_, "status": status_code}
            else:

                self.sumo_msg_api =[{"project":"UAC","exec_method":"API","exec_type":"API","user_id":self.uid,"activity":"ETL Process","dest_file":self.extractor,"dest_tool":tool1,"client_id":client1,"pid":p_id,"p_timestamp":date,"message": message, "rec_file_name": self.file_ ,"trans_file_name":self.file_, "status": status_code}]
                r = requests.post(settings.END_POINT, data = json.dumps(self.sumo_msg_api))
                process_log = ETLProcessLogs(p_timestamp=date,exec_method ="API",exec_type=self.method,client_id=self.client_id,dest_file_id=self.destination_file_id,tool_id=self.tool_id, settings_id=client_ext_settings,rec_file_name=self.file_,rec_file_checksum="",
                trans_file_name=self.file_,trans_file_checksum="",status=400, response=message, user=self.uid)
                process_log.save()
                return {"message": message, "filename": self.file_, "status":400}
        else:
            errors = f.validation_errors
            date = datetime.now().strftime("%Y%m%d%H%M%S")
            process_log = ETLProcessLogs(p_timestamp=date,exec_method ="API",exec_type=self.method,client_id=self.client_id,dest_file_id=self.destination_file_id,tool_id=self.tool_id, settings_id=client_ext_settings,rec_file_name=self.file_,rec_file_checksum="",
                trans_file_name=self.file_,trans_file_checksum="",status=400, response=errors, user=self.uid)
            self.sumo_msg_api =[{"project":"UAC","exec_method":"API","exec_type":"API","user_id":self.uid,"activity":"ETL Process","dest_file":self.extractor,"dest_tool":tool1,"client_id":client1,"pid":p_id,"p_timestamp":date,"message": message, "rec_file_name": self.file_ ,"trans_file_name":self.file_, "status": status_code}]
            r = requests.post(settings.END_POINT, data = json.dumps(self.sumo_msg_api))
            process_log.save()
            return {"message": errors, "filename": self.file_, "status": 400}

    def check_connected(self):

        url='http://www.google.com/'
        timeout=5
        _ = requests.get(url, timeout=timeout)
           


    def get_sftp_credentials(self):
        
        sftp_details = ClientsTools.objects.get(client_id=self.client_id, tool_id=self.tool_id)
        self.sftp_host = sftp_details.sftp_server
        self.sftp_user = sftp_details.sftp_user
        self.sftp_password = sftp_details.sftp_pwd
        self.sftp_port = int(sftp_details.sftp_port)
        self.sftp_in = sftp_details.sftp_in
        self.sftp_out = sftp_details.sftp_out

    def establish_sftp_connection(self):

        transport = paramiko.Transport((self.sftp_host, self.sftp_port))
        transport.connect(None, self.sftp_user, self.sftp_password, self.sftp_key)
        self.sftp = paramiko.SFTPClient.from_transport(transport)
        # except Exception as e:
        #     print("SFTP Connection Error Occurred : " + str(e))




    @staticmethod
    def rules_lookup(rules, _ids):
        rules_id = [x[0] for x in rules]
        rules_name = [x[1] for x in rules]
        s = []
        for _id in _ids:
            s.append(rules_name[rules_id.index(int(_id))])
        return s

    def get_current_extractor(self):
        current_extractor = ClientExtractSettings.objects.get(client_id=self.client_id, tool_id=self.tool_id,
                                                   dest_file_id=self.destination_file_id, file_name_start=self.file_start, erp_id=self.erp_id)
        self.set_id = current_extractor.settings_id
        self.rule_set_id = current_extractor.ruleset_id
        self.file_type = current_extractor.data_format
        self.file_start = self.file_start
        self.erp_id = self.erp_id
        
        delimiter = current_extractor.column_delimiter
        self.separator = "|" if delimiter == "pipe" else "," if delimiter == "comma" else '\t'

    def get_current_extractor_api(self):

        try:         
            print("aaaaaaaaaa")   
            print(self.file_cid)                                                                                                                                       
            current_extractor = ClientExtractSettings.objects.get(client_id=self.client_id, tool_id=self.tool_id, dest_file_id=self.destination_file_id, file_name_start=self.file_cid, erp_id=self.erp_id)
            self.set_id = current_extractor.settings_id
            self.rule_set_id = current_extractor.ruleset_id
            self.file_type = current_extractor.data_format
            self.file_start = self.file_cid
            self.erp_id = self.erp_id
            delimiter = current_extractor.column_delimiter
            self.separator = "|" if delimiter == "pipe" else "," if delimiter == "comma" else '\t'

            
        except ClientExtractSettings.DoesNotExist:
        

            
            try:
                print("bbbbbbbbbbbb")
                print(self.file_start)
                current_extractor = ClientExtractSettings.objects.get(client_id=self.client_id, tool_id=self.tool_id, dest_file_id=self.destination_file_id, file_name_start=self.file_start,erp_id=self.erp_id)

                self.set_id = current_extractor.settings_id
                self.rule_set_id = current_extractor.ruleset_id
                self.file_type = current_extractor.data_format
                self.file_start = self.file_start
                self.erp_id=self.erp_id
                delimiter = current_extractor.column_delimiter
                self.separator = "|" if delimiter == "pipe" else "," if delimiter == "comma" else '\t'

            except ClientExtractSettings.DoesNotExist:
                print("cccccccccccccc")
                print(self.extractor)

                current_extractor1 = ClientExtractSettings.objects.get(client_id=self.client_id, tool_id=self.tool_id, dest_file_id=self.destination_file_id, file_name_start=self.extractor, erp_id=self.erp_id)
                self.set_id = current_extractor1.settings_id
                self.rule_set_id = current_extractor1.ruleset_id
                self.file_type = current_extractor1.data_format
                self.file_start = self.extractor
                self.erp_id=self.erp_id
                delimiter = current_extractor1.column_delimiter
                self.separator = "|" if delimiter == "pipe" else "," if delimiter == "comma" else '\t'


    def get_extractor_details(self):
        extractor_details = ClientExtractorDetails.objects.filter(settings_id=self.set_id).order_by('ordinal')
        required_list = [(x.detail_id, x.source_column, x.dest_column) for x in extractor_details]
        self.source_columns = [x[1] for x in required_list]
        self.destination_columns = [x[2] for x in required_list]

    
    def get_required_IN_folder(self):
        in_folder =self.sftp.listdir_attr(self.sftp_in)
        

    def get_required_OUT_folder(self):
        out_folder =self.sftp.listdir_attr(self.sftp_out)       


    def get_required_files(self):
        """
        get files to be processed from the SFTP server.
        """
        file_match = self.file_start + '*.' + self.file_type
        for file_ in self.sftp.listdir_attr(self.sftp_in):
            # checks for whether folder/regular file
            if stat.S_ISREG(file_.st_mode):
                if fnmatch.fnmatch(file_.filename, file_match):
                    self.files_to_be_processed.append(file_.filename)

    def build_columns_list(self):
        """
        build column list to be included in the output file.
        """
        for i, x in enumerate(self.source_columns):
            if x != '[BLANK]':
                self.source_destination_map[x] = self.destination_columns[i]
                self.source_columns_wo_blank.append(x)
                self.source_columns_required.append(self.destination_columns[i])
            else:
                self.blank_columns.append(self.destination_columns[i])

    # def validate_checksum(self):


    #     local_file_data = open(local_file, "rb").read()
    #     remote_file_data = sftp.open(in_folder +'/'+ Extractor).read()
    #     md1 = hashlib.md5(local_file_data).hexdigest()
    #     md2 = hashlib.md5(remote_file_data).hexdigest()
    #     valid_checksum = False
    #     if md1 == md2:
    #         valid_checksum = True
                    
    #         return True

    def build_configuration(self):
        rules = self.get_rules()
        rule_set = self.get_required_rule_set()
        unique_columns = self.get_unique_columns()
        transformation_rules = []
        for rule_ in rule_set:
            if rule_[1]:
                transformation_rules.append(
                    {'column': rule_[0], 'rules': self.rules_lookup(rules, rule_[1].split(','))})

        self.config_JSON['transform_rules'] = transformation_rules

        validation_rules = []
        for rule_ in rule_set:
            if rule_[0] not in [i.get('column') for i in validation_rules]:
                validation_rules.append(
                    {'column': rule_[0], 'type': rule_[2], 'length': rule_[3], 'required': True if rule_[4] else False})

        self.config_JSON['validation_rules'] = validation_rules

        if unique_columns:
            self.config_JSON['unique_column'] = unique_columns

    @staticmethod
    def get_rules():
        return [(i.rule_id, i.rule_name) for i in DestinationRules.objects.all()]

    def get_required_rule_set(self):
        return [(i.column_name, i.rules, i.column_type, i.column_length, i.required) for i in
                RulesetDetails.objects.filter(ruleset_id=self.rule_set_id)]

    def get_unique_columns(self):
        unique_columns = []
        columns = RulesetMaster.objects.get(ruleset_id=self.rule_set_id).uniq_flds
        if columns:
            unique_columns = [i.strip() for i in columns.split(',')]
        return unique_columns

    

    # @staticmethod
    # def md5(fname):
    #     hash_md5 = hashlib.md5()
    #     with open(fname, "rb") as f:
    #         for chunk in iter(lambda: f.read(4096), b""):
    #             hash_md5.update(chunk)
    #     return hash_md5.hexdigest()

    # @staticmethod
    # def uac_Encrypt(message, key, key_size=256):
    #     s=b"\0" * (AES.block_size - len(message) % AES.block_size)
    #     message2 =message+  s
    #     iv = Random.new().read(AES.block_size)
    #     cipher = AES.new(key, AES.MODE_CBC, iv)
    #     return iv + cipher.encrypt(message2)
        
    # @staticmethod
    # def uac_decrypt(ciphertext, key):
    #     iv = ciphertext[:AES.block_size]
    #     cipher = AES.new(key, AES.MODE_CBC, iv)
    #     plaintext = cipher.decrypt(ciphertext[AES.block_size:])
    #     return plaintext.rstrip(b"\0")




  