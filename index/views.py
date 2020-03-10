from django.http import *
from django.shortcuts import render, render_to_response, redirect
import json
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import datetime
from django.db.models import Q
from masters.models import Erp
from masters.models import DestinationFile as df
from masters.models import DestinationTools as dt
from masters.models import Clients
from masters.models import ClientsTools as dv
from masters.models import RulesetMaster
from masters.models import Erp as pd
from masters.models import ClientsERP as db
from masters.models import ETLProcessLogs, SchedulerConfig
from django.core.paginator import Paginator


# @login_required(login_url='/uac/login/')
# def index(request):

@login_required(login_url='/uac/login/')
def index(request):
    clients = Clients.objects.all()
    extract = df.objects.all()
    success = ETLProcessLogs.objects.filter(status=200)
    failed = ETLProcessLogs.objects.filter(status=400)
    scheduler = SchedulerConfig.objects.all()
    count_failed = len(failed)
    count_success = len(success)
    count_client = len(clients)
    count_extract = len(extract)
    count_scheduler = len(scheduler)
    return render(request, 'etl/uac_index.html',
                  {'count': count_client, 'excount': count_extract, 'count_success': count_success,
                   'count_failed': count_failed, 'count_scheduler': count_scheduler})


def client_extract_valuechange(request):
    client_id = (request.GET.get('valueChange'))
    client = Clients.objects.get(client_id=client_id)

    erps = Erp.objects.raw(
        'SELECT uac_source_erp.erp_id,uac_source_erp.erp_name FROM uac_source_erp INNER JOIN uac_clients_erp ON '
        'uac_source_erp.erp_id=uac_clients_erp.erp_id WHERE uac_clients_erp.client_id= %s',
        [client_id])
    erp_data = []
    for i in erps:
        erp_data.append({'erp_name': i.erp_name, 'erp_id': i.erp_id})

    tool = dv.objects.raw(
        'SELECT uac_clients_tools.cl_tool_id,uac_destination_tool.tool_id as tool_id,uac_destination_tool.tool_name '
        'as tool_name FROM uac_clients_tools INNER JOIN uac_destination_tool ON '
        'uac_destination_tool.tool_id=uac_clients_tools.tool_id WHERE uac_clients_tools.client_id= %s',
        [client_id])
    tool_data = []
    for i in tool:
        tool_data.append({'tool_name': i.tool_name, 'tool_id': i.tool_id})

    return JsonResponse({'erps': erp_data, 'tool': tool_data})
