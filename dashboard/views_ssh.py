from django.http import JsonResponse
from django.shortcuts import render
from .views_nms import runssh
import json
from .utils import cpu, memory, storage, systeminfo, uptime, network, loadavg, cpu_temp, fan_rate
from time import strftime, localtime
from django.views.decorators.csrf import csrf_exempt
from .models import DeviceCapibility
import logging


try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))

def individualDashboard(request, ip):
    data = {}
    device = DeviceCapibility.objects.get(ip = ip)
    data["username"] = device.user
    data["password"] = device.pwd
    data["ip"] = ip
    data["port"] = 22
    return render(request,"dashboard/sshdashboard.html",{"data":data})
def getchasis(data):
    try:
        return (data.split("\n")[2].split(":")[1]).strip()
    except:
        return ""
def sshData(host, user, pwd, port):
    sshclient = runssh(host, user, pwd, port)
    output = {}
    output["time"] = strftime("%H:%M:%S", localtime())
    command = ['cat /proc/stat', 'cat /proc/meminfo', 'df', 'uname -a', 'cat /proc/uptime', 'cat /proc/net/dev', 'cat /proc/loadavg', 'sensors', 'hostnamectl']
    func = [cpu, memory, storage, systeminfo, uptime, network, loadavg, cpu_temp, getchasis]
    output["fan_rate"] = fan_rate()
    for cmd, fun in zip(command, func):
        _, stdout, _ = sshclient.exec_command(cmd)
        output[fun.__name__] = fun(stdout.read().decode('utf-8'))
    _, stdout, _ = sshclient.exec_command("lshw -numeric -C display -json")
    try:
        output["GPU"] = json.loads(stdout.read().decode('utf-8')) 
    except Exception as err:
        output["GPU"] = 0
    # if output["memory"]["used%"] > threshold.usedRam:
    #     generateAlert(host, "Memory Usage", output["memory"]["used%"], "High memory usage in "+host, "high")
    # if output["cpu"]["used"] > threshold.cpu_threshold:
    #     generateAlert(host, "CPU Usage", output["cpu"]["used"], "High CPU Usage in "+host, "high")
    return output

@csrf_exempt
def index(request):
    try:
        host = request.POST["host"]
        user = request.POST["username"]
        pwd = request.POST["password"]
        port = int(request.POST["port"])
        output = sshData(host, user, pwd, port)
        return JsonResponse({"error":False, "data":output})
    except Exception as err:
        db_logger.exception(err)
        # print(str(err))
        return JsonResponse({"error":True , "data":str(err)})