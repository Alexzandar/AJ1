from django.conf.urls import url
from masters.views import erp, tools, destfiles, clients, configs, transrules, charts, users, uacerror

urlpatterns = [
    url(r'^masters/erp', erp.master_erp, name='ERP Master'),
    url(r'^erpsave', erp.new_erp, name='ERP Save'),
    url(r'^erpdelete/(?P<id>\d+)', erp.delete_erp, name='ERP Delete'),
    url(r'^erpupdate/', erp.update_erp, name='ERP Update'),
    url(r'^erpsearch/', erp.search_erp, name='ERP Search'),

    url(r'^masters/tools/$', tools.master_tool, name='Tool Master'),
    url(r'^toolsave/$', tools.new, name='Tool Save'),
    url(r'^tooldelete/(?P<id>\d+)$', tools.delete_tool, name='Tool Delete'),
    url(r'^toolupdate/$', tools.update_tool, name='Tool Update'),
    url(r'^toolsearch/$$', tools.search_tool, name='Tool Search'),

    # Destination Files - Master
    url(r'^masters/destfiles/$', destfiles.master_destfile, name='Destination File Master'),
    url(r'^destfilesave/$', destfiles.new_destfile, name='New Dest. File'),
    url(r'^destfiledelete/(?P<id>\d+)$', destfiles.delete_destfile, name='Tool Delete'),
    url(r'^destfileupdate/$', destfiles.update_destfile, name='DF Update'),
    url(r'^destfilesearch/$', destfiles.search_destfile, name='Dest. File Search'),

    # Clients - Master
    url(r'^masters/clients/$', clients.master_clients, name='Client Master'),
    url(r'^editdetails/$', clients.edit_details, name='Get Edit Client'),
    url(r'^clientdelete/(?P<id>\d+)$', clients.delete_clients, name='Client Delete'),
    url(r'^clientsearch/$', clients.search_clients, name='Client Search'),
    url(r'^getclient/$', clients.get_client, name='Get Client Details'),
    url(r'^getclienterp/$', clients.get_client_erp, name='Get Client ERP'),
    url(r'^clientERPsave/$', clients.client_erp_save, name='Save Client ERP'),
    url(r'^clientupdate/$', clients.client_erp_update, name='Update Client ERP'),
    url(r'^client-check/$', clients.client_check, name='Client Validation'),

    # Transformation Rules - Master
    url(r'^masters/transrules/$', transrules.master_transrules, name='Transformation Rules  Master'),
    url(r'^transrulesave/$', transrules.new_transrules, name='New Transformation Rules '),
    url(r'^transruledel/(?P<id>\d+)$', transrules.delete_transrules, name='Transrule Delete'),
    url(r'^transrulesupdate/$', transrules.update_transrules, name='Edit Transformation Rules '),
    # Define Ruleset
    url(r'^ruleset/$', configs.destschema, name='Define Ruleset'),
    url(r'^schemasave/$', configs.schemasave, name='Save Schema'),
    url(r'^schemaEdit/$', configs.schemaedit, name='Edit Schema'),
    url(r'^getrules/$', configs._getrules, name='Get Master Rules'),
    url(r'^schemaGetDetails/$', configs.schemaGetDetails, name='Get Master Rules'),
    url(r'^destDelete/(?P<id>\d+)$', configs.destdelete, name='Delete All'),
    url(r'^schema-unique/$', configs.schema_unique, name='Unique Schema'),

    # Extractor Settings
    url(r'^extractset/$', configs.extractset, name='Extractor Settings'),
    url(r'^getextracthead/$', configs.getExtractorHeading, name='Get Extractor Heading'),
    url(r'^getrulesetcolumns/$', configs.getRulesetColumns, name='Get columns by ruleset id'),
    url(r'^savesettings/$', configs.saveExtractSettings, name='Save Extractor Settings'),
    url(r'^getsettingslist/$', configs.viewSettingsList, name='View Extractor Settings'),
    url(r'^getmappingslist/$', configs.viewMappingsList, name='View Mapping'),

    # MIS Dashboard Chart Data
    url(r'^getdashboard/$', charts.getMISdata, name='Dashboard Data'),

    # Scheduler
    url(r'^scheduler/$', configs.master_sched, name='Scheduler Configs'),
    url(r'^savescheduler/$', configs.save_sched, name='Save Scheduler Configs'),
    url(r'^removescheduler/(?P<id>\d+)$', configs.remove_sched, name='Delete Scheduler Entry'),
    # url(r'file_start_rule_scheduler/$',configs.file_start_rule_scheduler, name='ajax filestart call'),
    # url(r'^define_rule_scheduler/$', configs.define_rule_scheduler, name='ajax call'),
    url(r'^changestatus/(?P<id>[\d]+)/(?P<actcode>[\w\-]+)/$', configs.changestat_sched, name='Change Status'),

    # User Management
    url(r'^masters/usermanage/$', users.master_users, name='User Management'),
    url(r'^masters/usrtoken/(?P<id>\d+)$', users.getUserToken, name='User Token'),
    url(r'^masters/usrperms/(?P<id>\d+)$', users.getUserPermissions, name='User Permissions'),
    url(r'^masters/updateperms/$', users.updateUserPermissions, name='Update Permissions'),
    url(r'^masters/password/(?P<id>\d+)$', users.resetUserPassword, name='Reset Password'),

    # Error
    url(r'^error/$', uacerror.error_403, name='Error 403'),
]
