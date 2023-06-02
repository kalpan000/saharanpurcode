from os import error, stat
import platform
from subprocess import run, PIPE, Popen
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import DeviceCapibility, TerminalLog
import paramiko
from threading import Timer
import datefinder
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
import subprocess
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

@permission_required("dashboard.view_settings" , "/noperm/")
def terminal(request):
    return render(request, 'terminal/index.html')

#ping ping -c 1 8.8.8.8
def runssh(host,username, password, port=22):
    # try:
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.load_system_host_keys()
    sshClient.connect(host, port, username, password)
    return sshClient

@csrf_exempt
def getUserCmd(request, timeout=5):

    if not request.user.has_perm("dashboard.add_settings"):
        return JsonResponse({"error" : True , "redirectError" : "noperm"})
        
    cmd = request.POST["cmd"]
    cmd = cmd.split(" ")
    if platform.system() == "Windows":
        p = run(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        status = p.returncode
        res = ""
        if status == 1:
            res = "Sorry cmd will not execute as device is on PoC"
        elif status == 0:
            res = "Sorry cmd will not execute as device is on PoC"
        else:
            res = "Something went wrong"
    else:
        try:
            status = 1
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            res = ""
            o, e = p.communicate()
            if o:
                status = 0
            res = "Sorry cmd will not execute as device is on PoC"
        except Exception as err:
            res = str(err)
    # stdout, stderr = p.communicate()
    TerminalLog.objects.create(cmd=' '.join(cmd),output= res, device="Localhost",user = request.user)
    return JsonResponse({
        "status":status,
        "res":res
    })
def terminalogs(request):
    return render(request, 'terminal/logs.html')

def get_syslog():
    return subprocess.check_output("cat /var/log/syslog".split(" ") , stderr= subprocess.STDOUT).decode("utf-8").split("\n")[-1000 : ]
    
def get_kernlog():
    return subprocess.check_output("cat /var/log/kern.log".split(" ") , stderr= subprocess.STDOUT).decode("utf-8").split("\n")[-1000 : ]

def get_authlog():
    return subprocess.check_output("cat /var/log/auth.log".split(" ") , stderr= subprocess.STDOUT).decode("utf-8").split("\n")[-1000 : ]

def get_logs(request):
    type = "sys"
    logList = []
    if type == "sys":
        logList = get_syslog()
    elif type == "kernal":
        logList = get_kernlog()
    else:
        logList = get_authlog()


    output = []

    for i in logList:
        dates = list(datefinder.find_dates(i))
        if len(dates) > 0:
            output.append({
                "date" : dates[0].strftime("%m/%d/%Y, %H:%M:%S"),
                "log" : i
            })
        else:
            output.append({
                "date" : "",
                "log" : i
            })


    data = {
        "data" : output
    }
    
    return JsonResponse(data)

def syslogs(request):
    return render(request, 'dashboard/syslogs.html')
@csrf_exempt
def send_log(request):
    try:
        ip = request.POST.get("ip","")
        obj = DeviceCapibility.objects.get(ip = ip)
        type = request.POST.get("type" , "sys")
        output = []
        try:
            host = obj.ip
            user = obj.user
            pwd = obj.pwd
            if type == "sys":
                cmd = "head -1000 /var/log/messages"
                type = "System"
            elif type == "kernal":
                cmd = "head -1000 /var/log/kern.log"
                type = "Kernal"
            else:
                cmd = "head -1000 /var/log/auth.log"
                type = "Auth"

            sshclient = runssh(host,user, pwd,22)
            _, stdout, stderr = sshclient.exec_command(cmd)
            status = stdout.channel.recv_exit_status()   
            if (status == 0):
                res = stdout.read().decode('utf-8').split("\n")
                for i in res:
                    try:
                        dates = list(datefinder.find_dates(i))
                    except:
                        dates = []
                    if len(dates) > 0:
                        output.append({
                            "date" : dates[0].strftime("%m/%d/%Y, %H:%M:%S"),
                            "log" : i
                        })
                    else:
                        output.append({
                            "date" : "",
                            "log" : i
                        })
                html_message = render_to_string('email/logs.html', {'logs': output, 'type':type})
                plain_message = strip_tags(html_message)
                email_from = settings.EMAIL_HOST_USER
                email_to = [request.user.email,] 
                try:
                    send_mail(subject=type+" Logs",message=plain_message, html_message=html_message, from_email=email_from, recipient_list=email_to)
                except Exception as err:
                    return JsonResponse({"err":True, "data":str(err)})
                return JsonResponse({"err":False, "data":"Logs Sent Successfully to your email"})
            else:
                res = str(stderr.read().decode('utf-8'))
            return JsonResponse({"err":False,"data":output})
        except Exception as err:
            return JsonResponse({"err":True,"data":str(err)})
    except Exception as err:
        return JsonResponse({"err":True, "data":"Method Not Allowed"})
@csrf_exempt
def fetchsyslog(request):
    try:
        ip = request.POST.get("ip","")
        obj = DeviceCapibility.objects.get(ip = ip)
        type = request.POST.get("type" , "sys")
        output = []
        try:
            host = obj.ip
            user = obj.user
            pwd = obj.pwd
            if type == "sys":
                cmd = "head -1000 /var/log/syslog"
            elif type == "kernal":
                cmd = "head -1000 /var/log/kern.log"
            else:
                cmd = "head -1000 /var/log/auth.log"

            sshclient = runssh(host,user, pwd,22)
            _, stdout, stderr = sshclient.exec_command(cmd)
            status = stdout.channel.recv_exit_status()   
            if (status == 0):
                res = stdout.read().decode('utf-8').split("\n")
                for i in res:
                    try:
                        dates = list(datefinder.find_dates(i))
                    except:
                        dates = []
                    if len(dates) > 0:
                        output.append({
                            "date" : dates[0].strftime("%m/%d/%Y, %H:%M:%S"),
                            "log" : i
                        })
                    else:
                        output.append({
                            "date" : "",
                            "log" : i
                        })
            else:
                res = str(stderr.read().decode('utf-8'))
            return JsonResponse({"err":False,"data":output})
        except Exception as err:
            return JsonResponse({"err":True,"data":str(err)})
    except Exception as err:
        return JsonResponse({"err":True, "data":"Method Not Allowed"})

def terminalLogsdata(request):
    logs = TerminalLog.objects.all().values()
    return JsonResponse({'data':list(logs)})
@csrf_exempt
def sshCommand(request):
    try:
        host = request.POST["host"]
        input = request.POST.get("input",None)
        cmd = request.POST["cmd"]
        user = request.POST["user"]
        pwd = request.POST["pwd"]
        print(host,input, cmd, user, pwd)
        # status, res = runssh(host=host,input=input, username=user, password=pwd,command=cmd,port=22)
        sshclient = runssh(host,user, pwd,22)
        stdin, stdout, stderr = sshclient.exec_command(cmd)
        status = stdout.channel.recv_exit_status()
        if (input):
            stdin.write(input)
            stdin.flush()
        status = stdout.channel.recv_exit_status()    
        if (status == 0):
            res = stdout.read().decode('utf-8')
        else:
            res = str(stderr.read().decode('utf-8'))  
        TerminalLog.objects.create(cmd=cmd,output=res, device=str(host),user=request.user)
        return JsonResponse({"status":status,"res":res})
    except Exception as err:
        return JsonResponse({"status":-1,"res":str(err)})
