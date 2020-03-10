from django.db import models
from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.models import User, Permission
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.template import loader
from django.conf import settings
import datetime
class Erp(models.Model):
    erp_id = models.AutoField(primary_key=True)
    erp_name = models.CharField(max_length=20)
    erp_desc = models.CharField(max_length=50)

    class Meta:
        db_table = "uac_source_erp"
        default_permissions = ()
        permissions = [
            ('new_erp', 'Add ERP'),
            ('change_erp', 'Change ERP'),
            ('delete_erp', 'Delete ERP'),
        ]


class DestinationTools(models.Model):
    tool_id = models.AutoField(primary_key=True)
    tool_name = models.CharField(max_length=20)
    tool_short = models.CharField(max_length=10, unique=True)
    tool_desc = models.CharField(max_length=50)

    class Meta:
        db_table = "uac_destination_tool"
        default_permissions = ()
        permissions = [
            ('new_dest_tool', 'Add Destination Tool'),
            ('change_dest_tool', 'Change Destination Tool'),
            ('delete_dest_tool', 'Delete Destination Tool'),    
        ]


class DestinationFile(models.Model):
    dest_file_id = models.AutoField(primary_key=True)
    dest_file_name = models.CharField(max_length=30)
    dest_short = models.CharField(max_length=10, unique=True, default='NA')
    tool_id = models.IntegerField()
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uac_destination_file"
        unique_together = (('dest_short'),)
        default_permissions = ()
        permissions = [
            ('new_destination_type', 'Add Destination Type'),
            ('change_destination_type', 'Change Destination Type'),
            ('delete_destination_type', 'Delete Destination Type'),
        ]

class Clients(models.Model):
    client_id = models.AutoField(primary_key=True)
    client_name = models.CharField(max_length=50)
    client_short = models.CharField(max_length=6, default='NA')
    client_email = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_by= models.IntegerField()
    entry_date = models.DateTimeField(auto_now=True)
    user_name = models.CharField(max_length=50, unique=True)
    class Meta:
        unique_together = (('client_name'),)
        unique_together = (('client_short'),)
        db_table = "uac_erp_clients"
        default_permissions = ()
        permissions = [
            ('new_client', 'Add Client'),
            ('change_client', 'Change Client'),
            ('delete_client', 'Delete Client'),
            ('view_client_permission', 'View Client Permission'),
            ('view_client_token', 'View Client API Token'),
            ('reset_client_password', 'Reset Client Password'),
            ('manage_client_permission', 'Manage Client Permisison'),
            ('etl_process', 'Process ETL'),        ]    

# modified
class ClientsERP(models.Model):
    cl_erp_id = models.AutoField(primary_key=True)
    client_id = models.IntegerField()
    erp_id = models.IntegerField()
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uac_clients_erp"
        unique_together = (('client_id', 'erp_id'),)
        default_permissions = ()

class ClientsTools(models.Model):
    cl_tool_id = models.AutoField(primary_key=True)
    client_id = models.IntegerField()
    tool_id = models.IntegerField()
    sftp_server = models.CharField(max_length=50)
    sftp_user = models.CharField(max_length=20)
    sftp_pwd = models.CharField(max_length=20)
    sftp_port = models.CharField(max_length=3)
    sftp_in = models.CharField(max_length=60)
    sftp_out = models.CharField(max_length=60)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uac_clients_tools"
        unique_together = (('client_id', 'tool_id'),)
        default_permissions = ()
        
class RulesetMaster(models.Model):
    ruleset_id = models.AutoField(primary_key=True)
    ruleset_name = models.CharField(max_length=40, unique = True)
    tool_id = models.IntegerField()
    dest_file_id = models.IntegerField()
    uniq_flds = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uac_ruleset_master"
        default_permissions = ()
        permissions = [
            ('new_extractor', 'Add Extractor'),
            ('change_extractor', 'Change Extractor'),
            ('delete_extractor', 'Delete Extractor'),
        ]

        
class RulesetDetails(models.Model):
    rule_schema_id = models.AutoField(primary_key=True)
    ruleset_id = models.IntegerField()
    tool_id = models.IntegerField()
    dest_file_id = models.IntegerField()
    column_id = models.IntegerField()
    column_name = models.CharField(max_length=40)
    column_type = models.CharField(max_length=30)
    column_length = models.IntegerField()
    required = models.IntegerField()
    rules = models.CharField(max_length=150)
    ordinal = models.IntegerField()
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uac_ruleset_details"
        default_permissions = ()
        
class DestinationRules(models.Model):
    rule_id = models.AutoField(primary_key=True)
    rule_name = models.CharField(max_length=20)
    regexp = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "uac_dest_rules"
        default_permissions = ()
        permissions = [
            ('new_transformation_rule', 'Add Transformation Rule'),
            ('change_transformation_rule', 'Change Transformation Rule'),
            ('delete_transformation_rule', 'Delete Transformation Rule'),
        ]


class ClientExtractSettings(models.Model):
    settings_id = models.AutoField(primary_key=True)
    client_id = models.IntegerField()
    erp_id = models.IntegerField()
    tool_id = models.IntegerField()
    dest_file_id = models.IntegerField()
    ruleset_id = models.IntegerField()
    data_format = models.CharField(max_length=10)
    column_delimiter = models.CharField(max_length=10)
    file_name_start = models.CharField(max_length=5)
    file_name_format = models.CharField(max_length=50)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uac_client_settings_master"
        default_permissions = ()
        permissions = [
            ('view_client_extractor_setting', 'View Client Extractor Setting'),
            ('new_client_extractor_setting', 'Add Client Extractor Setting'),
        ]


class ClientExtractorDetails(models.Model):
    detail_id = models.AutoField(primary_key=True)
    settings_id = models.IntegerField()
    source_column = models.CharField(max_length=50)
    dest_column = models.CharField(max_length=50)
    dest_column_id = models.IntegerField()
    ordinal = models.IntegerField()
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uac_client_settings_details"
        default_permissions = ()
        
#scheduler configs
class SchedulerConfig(models.Model):
    scheduler_id = models.AutoField(primary_key=True)
    client_id = models.IntegerField()
    erp_id = models.IntegerField()
    tool_id = models.IntegerField()
    dest_file_id = models.IntegerField()
    date_from = models.DateTimeField(blank=True, null=True,default=datetime.date.today)
    file_name_start = models.CharField(max_length=5, default='NA')
    active = models.CharField(max_length=1, default='Y')
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    entry_date = models.DateField(auto_now=True)


    class Meta:
        db_table = "uac_scheduler_config"
        default_permissions = ()
        permissions = [
            ('new_process_scheduler', 'Add Process Scheduler'),
            ('change_process_scheduler', 'Change Process Scheduler'),
            ('delete_process_scheduler', 'Delete Process Scheduler'),
        ]


        
class ETLProcessLogs(models.Model):
    etl_id = models.AutoField(primary_key=True)
    p_timestamp = models.CharField(max_length=15)
    exec_method = models.CharField(max_length=10)
    exec_type = models.CharField(max_length=10)
    client_id = models.IntegerField()
    dest_file_id = models.IntegerField()
    tool_id = models.IntegerField()
    settings_id = models.IntegerField()
    rec_file_name = models.CharField(max_length=50)
    rec_file_checksum = models.CharField(max_length=50)
    trans_file_name = models.CharField(max_length=50)
    trans_file_checksum = models.CharField(max_length=50)
    status = models.IntegerField()
    response = models.TextField(blank = True)
    user = models.IntegerField()
    entry_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "uac_etl_logs"
        default_permissions = ()

@receiver(post_save, sender=Clients)
def create_django_user(sender, instance=None, created=False, **kwargs):
    if created:
        user_objects = get_user_model().objects
        password = user_objects.make_random_password()
        print(password)
        
        user = user_objects.create_user(username=instance.user_name, password=password, first_name=instance.client_name, email=instance.client_email)
        instance.user = user
        instance.save()
        html_message = loader.render_to_string(
                'etl/uac_email.html',
                {'app_name': settings.APP_NAME,'user': user,'password':password,
                    'login_url': settings.BASE_URL}
            )

        send_mail('User Account Created', '', settings.APP_NAME+' <do_not_reply@domain.com>', [
                      user.email], fail_silently=True, html_message=html_message)
        
                # self.sftp.put(cleaned_file_name, self.sftp_out + '/' + file_)

@receiver(post_save, sender=Clients)
def create_update_user(sender, instance=None, **kwargs):
    user_objects = get_user_model().objects
    ids=instance.user_id
    user=User.objects.get(id=ids)
    user.username=instance.user_name 
    user.email=instance.client_email
    user.first_name=instance.client_name
    user.save()   
    # html_message = loader.render_to_string(
    #             'etl/uac_email.html',
    #             {'app_name': settings.APP_NAME,'user': user,
    #                 'login_url': settings.BASE_URL}
    #         )

    # send_mail('User Account Created', '', settings.APP_NAME+' <do_not_reply@domain.com>', [
    #             user.email], fail_silently=True, html_message=html_message)
                # self.sftp.put(cleaned_file_name, self.sftp_out + '/' + file_)             

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_delete, sender=Clients)
def delete_django_user(sender, instance, **kwargs):

    try:
        user_objects = get_user_model().objects
        user = user_objects.get(username = instance.user_name)
        user.django_user = None
        user.delete()
    except:
        pass

@receiver(post_delete, sender=User)
def delete_auth_token(sender, instance, **kwargs):

    try:
        Token.objects.delete(user=instance)

    except:
        pass
        