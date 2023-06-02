from django.shortcuts import render
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required

@permission_required("dashboard.view_settings" , "/noperm/")
def index(request):
    return render(request, "dashboard/provisioning.html")

@permission_required("dashboard.view_settings" , "/noperm/")
def staking(request):
    return render(request, "dashboard/staking.html")

@permission_required("dashboard.view_settings" , "/noperm/")
def replication(request):
    return render(request, "dashboard/replication.html")