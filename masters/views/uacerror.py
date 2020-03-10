from django.shortcuts import render, render_to_response,redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/uac/login/')
def error_403(request):
	return render(request, 'etl/403.html')	

@login_required(login_url='/uac/login/')
def error_404(request, *args, **kwargs):
	return render(request, 'etl/404.html')	

@login_required(login_url='/uac/login/')
def error_500(request):
	return render(request, 'etl/500.html')