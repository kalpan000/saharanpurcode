from subprocess import PIPE, run
import os
from django.http.response import JsonResponse

def executeThis(cmd):
    cmd = cmd.split(" ")
    p = run(cmd, stdout=PIPE, stderr=PIPE , shell=True)

def shutdownDevice():
    executeThis("shutdown /s")

def restartDevice(request):
    if not request.user.has_perm("dashboard.add_settings"):
        return JsonResponse({"error" : True , "redirectError" : "noperm"})
    os.system("echo hawk123 | sudo -S shutdown -r now")
    return JsonResponse({'data':'System Restarting..'})

def logoffDevice():
    executeThis("shutdown /l")
