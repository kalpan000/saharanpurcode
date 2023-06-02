from ast import Pass
from cmath import inf
from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
import psutil
import subprocess
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
# import pythoncom
import re
from django.http import JsonResponse
try:
    from pexpect import pxssh
except:
    # print("Windows OS PExcept Disabled")
    pxssh = ""
import platform
from .views_nms import runssh
import json
from .models import AddDevice, DeviceCapibility, SNMPDataCollection, SSHServers
from django.views.decorators.csrf import csrf_exempt
import logging
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))

SSH_CONNECTION_DICT = {}

# TUPLES AND NAMED TUPLES ARE DIFFERENT IDIOT. STOP USING THIS AND MOVE TO NAMEDTUPLE 
def tupleToDict(k , v):
    l = len(k)
    d = {}
    temp = ""
    try:
        for i in range(0 , l):
            d[k[i]] = v[i]
    except:
        # print("==" * 50)
        # print ("K {0} V {1}" , len(k) , len(v))
        # print("Out of range") 
        # print(k)
        # print(v)
        # print("==" * 50)
        pass

    return d



class CPU:
    @staticmethod
    def usage():
        cpuCount = psutil.cpu_count()
        labels = []
        for i in range(0 , cpuCount):
            labels.append("CPU " + str(i))

        return {
            "error" : False,
            "data" : {
                "CPUCount" : psutil.cpu_count(),
                "CPUUtilization" : psutil.cpu_percent(interval=1, percpu=True),
                "labels" : labels
            }
        }

    @staticmethod
    def speed():
        l = []
        speed = psutil.cpu_freq(percpu=True)
        CPUCount = 0
        labels = []
        for item in speed:
            l.append((item[0]))
            labels.append("CPU " + str(CPUCount))
            #l.append(tupleToDict(["current" , "min" , "max"] , item))
            CPUCount += 1

        return {
            "error" : False,
            "data" : {
                "CPUCount" : CPUCount,
                "speed" : l,
                "labels" : labels
            }
        }

    @staticmethod
    def stats():
        return {
            "error" : False,
            "data" : {
                "stats" : list(psutil.cpu_stats()) , #tupleToDict(["ctx_switches" , "interrupts" , "soft_interrupts"] , psutil.cpu_stats()),
                "labels" : ["ctx_switches" , "interrupts" , "soft_interrupts" , "syscalls"]
            }
        }
        

class Memory:
    @staticmethod
    def virtualMemory():
        data = psutil.virtual_memory()
        d = {}
        k = ["total" , "used" , "available"]
        l = list(data)
        return {
            "error" : False,
            "data" : {
                "virtual" : [100 , 100 - ((l[1] / l[0]) * 100) , (l[1] / l[0]) * 100 ],
                "labels" : k
            }
        }
        
    
    @staticmethod
    def swapMemory():
        l = list(psutil.swap_memory())
        return {
            "error" : False,
            "data" : {
                "info" : [100 , 100 - ((l[1] / l[0]) * 100) , (l[1] / l[0]) * 100  , l[3] , l[4] , l[5]],
                "labels" : ["total" , "used" , "free" , "percent" , "sin" , "sout"]
            }
        }



class Disk:
    @staticmethod
    def diskStats():
        data = psutil.disk_io_counters(perdisk=True)
        d = {}
        k = ["read_count" , "write_count" , "read_bytes" , "write_bytes" , "read_time" , "write_time"]
        for key in data:
            l = list(data[key])
            d[key] = {
                "read_write_count" : l[0:2],
                "read_write_bytes" : [l[2]/1000000 , l[3]/1000000]
            }
        
        return {
            "error" : False,
            "data" : d,
            "labels" : k,
        }
        
# memory % , data , name , cpu %
class Process:
    @staticmethod
    def memoryInfo():
        l = ["rss" , "vms" , "shared" , "text" , "lib" , "data" , "dirty" , "uss" , "pss" , "swap"]
        output = []
        item = {}
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            #data = proc.memory_full_info()
            # print("=" * 50)
            # print(data)
            # print("=" * 50)
            item["name"] = proc.name()
            item["CPUPercent"] = proc.cpu_percent(interval=1)
            item["CPUNum"] = proc.cpu_num()
            item["memoryInfo"] = tupleToDict(l , proc.memory_full_info())

            output.append(item)
            
        return {
            "error" : False,
            "data" : output
        }


def extractTopData(data , rowsToSkip = 8):
    childLabels = []
    data = data.decode('utf8', errors='strict').strip()
    paragraph = data.split("\n")
    output = []
    
    for i, line in enumerate(paragraph):
        i += 1
        if i < rowsToSkip:
            continue

        lineArr = line.split(" ")
        lineHolder = []
        l = len(lineArr)        
                
        for j , word in enumerate(lineArr):
            if(word != "" and j != 0 and j != l - 1):
                lineHolder.append(word)         
            
        l = len(lineHolder)

        if(l != 0):
            childLabels.append(lineHolder[-1])

            if(l == 12):
                #output.append(lineHolder[1:])
                output.append(lineHolder[8:])
            else:
                #output.append(lineHolder)
                output.append(lineHolder[8:])
                
    i = 0
    cpu = []
    mem = []
            
    for i in range(0 , len(output)):
        cpu.append(output[i][0])
        mem.append(output[i][1])

    return output , cpu , mem , childLabels

class Application:
    @staticmethod
    def processInfo():
#        labels = ["user",  "pr" , "ni" , "virt" , "res" , "shr" , "s" , "cpu" , "mem" , "time" , "command"]
        try:
            labels = ["cpu" , "mem" , "time" , "command"]
            
            data = subprocess.check_output("top n1" , shell=True)

            output , cpu , mem , childLabels = extractTopData(data)

            return {
                "error" : False,
                "data" : {
                    "info" : output,
                    "cpu" : cpu,
                    "memory" : mem,
                    "labels" : childLabels
                },
            }
        except:
            return {
                "error" : True,
                "data" : {
                    "info" : [],
                    "cpu" : [],
                    "memory" : [],
                    "labels" : [],
                }
            }

    def processSSHInfo(sshCon):
    #        labels = ["user",  "pr" , "ni" , "virt" , "res" , "shr" , "s" , "cpu" , "mem" , "time" , "command"]
        try:
            labels = ["cpu" , "mem" , "time" , "command"]
            cmd = "top -b -n 1 | head -n 10"
            stdin, stdout, stderr = sshCon.exec_command(cmd)
            data = stdout.read()
            print("Reached")
            output , cpu , mem , childLabels = extractTopData(data , rowsToSkip=9)
            print("Extracted Data " , output , cpu , mem , childLabels)
            return {
                "error" : False,
                "data" : {
                    "info" : output,
                    "cpu" : cpu,
                    "memory" : mem,
                    "labels" : childLabels
                },
            }
        except:
            return {
                "error" : True,
                "data" : {
                    "info" : [],
                    "cpu" : [],
                    "memory" : [],
                    "labels" : [],
                }
            }



# returns list of list 
#user , PR , NI , VIRT , RES , SHR , S , CPU , MEM , TIME , COMMAND

#print(Application.processInfo())


#print(Disk.diskStats())
# def getWindowService(device, service):
#          # p.stdout.decode().split("\r\n")[3].split(":")[1]
#          cmd = "sc query "+str(service)
#          types=""
#          try:
#              p = subprocess.run(cmd.split(), stdout = subprocess.PIPE, shell=True)
#              code = p.returncode
#              result = p.stdout.decode()
#              if code == 0:
#                  res = result.split("\r\n")[3].split(":")[1].split(" ")[3]
#                  types = result.split("\r\n")[2].split(":")[1].split(" ")[3]
#              elif code == 1060:
#                  res = result.split("\r\n")[2]
#              else:
#                  res = "some error occured"
#              return {"data":res,"type":types}
#          except Exception as NOT_FOUND_SERVICE:
#              return {"data":NOT_FOUND_SERVICE}
# .split("\r\n")[3].split(":")[1].split(" ")[3]
def getWindowService(s, service):
    output = {"packages" : {}}
    for package in service:
        try:
            cmd = "sc query "+str(package)
            stdin, stdout, stderr = s.exec_command(cmd)
            status = stdout.channel.recv_exit_status()
            if (status == 0):
                result = stdout.read().decode('utf-8')
                res = result.split("\r\n")[3].split(":")[1].split(" ")[3]
                # types = result.split("\r\n")[2].split(":")[1].split(" ")[3]
                output["packages"][package] = {
                "name" : str(package),
                "status" : str(res),
                "size" :  "",
                }
            # else:
            #     return status, stderr.read() 
        except Exception as NOT_FOUND_SERVICE:
            return str(NOT_FOUND_SERVICE)
    return output
# getWindowService("192.168.1.15","bali","Akus@123",["AnyDesk"])
def ApplicationData(s, service):
    output = {"packages" : {}}
    data = ""
    for package in service:
        cmd = "dpkg -s " + package
        stdin, stdout, stderr = s.exec_command(cmd)
        data = stdout.read().decode('utf-8')
        if "is not installed" in data:
            output["packages"][package] = False
        else:
            tempdata = {"data":[],"utilization":{}}
            cpu = 0.0
            mem = 0.0

            pscmd = "ps aux | grep " + package
            stdin, stdout, stderr = s.exec_command(pscmd)
            res = stdout.read().decode().split("\n")
            for i in res[:-3]:
                dummy = {}
                test = ''.join(i).split()
                dummy["user"] = test[0]
                dummy["pid"] = test[1]
                dummy["cpu"] = test[2]
                cpu = cpu + float(test[2])
                dummy["mem"] = test[3]
                mem = mem + float(test[3])
                dummy["start"] = test[8]
                dummy["time"] = test[9]
                dummy["cmd"] = ' '.join(test[10:])
                tempdata["data"].append(dummy)
            tempdata["utilization"]["cpu"] = cpu
            tempdata["utilization"]["memory"] = mem            
            
            paragraph = data.split("\n")
            print("*" * 100)
            print(paragraph)
            print("*" * 100)
            output["packages"][package] = {
                "name" : paragraph[1],
                "status" : paragraph[2],
                "size" :  paragraph[5],
                "data" : tempdata
            }
    return output
    # cmd = "ps aux | grep " + service
    # stdin, stdout, stderr = s.exec_command(cmd)
    # res = stdout.read().decode().split("\n")
    # # res = stdout.split("\n")
    # tempdata = {"data":[],"utilization":{}}
    # cpu = 0.0
    # mem = 0.0
    # for i in res[:-3]:
    #     dummy = {}
    #     test = ''.join(i).split()
    #     dummy["user"] = test[0]
    #     dummy["pid"] = test[1]
    #     dummy["cpu"] = test[2]
    #     cpu = cpu + float(test[2])
    #     dummy["mem"] = test[3]
    #     mem = mem + float(test[3])
    #     dummy["start"] = test[8]
    #     dummy["time"] = test[9]
    #     dummy["cmd"] = ' '.join(test[10:])
    #     tempdata["data"].append(dummy)
    # tempdata["utilization"]["cpu"] = cpu
    # tempdata["utilization"]["memory"] = mem
    # # data.append(tempdata)
    # return tempdata
# user, pid, cpu, mem, vsz, rss, tty, stat, start, time, command
@csrf_exempt
def sshLogin(request):
    Host = request.POST["host"].strip() 
    Username = request.POST["username"].strip() 
    Password = request.POST["password"]
    Packages = request.POST["packages"].strip()

    oo = SSHServers(host = Host , username = Username , password = Password , packages = Packages)
    oo.save()


    packages = Packages.split(",")

    
    s = None

    try:
        s = runssh(Host,Username, Password,22)
        # if not s.login(Host , Username , Password):
        #     print("ERROR")
        #     return JsonResponse({"error" : True , "message" : "SSH connection failed. Check entered username and password"})
    # except NameError as nameErr :
    #     s = None
    #     db_logger.exception(nameErr)
    #     return JsonResponse({"error" : True , "message" : "This function is not supported for Windows OS"})

    except Exception as e :
        s = None
        db_logger.exception(e)
        return JsonResponse({"error" : True , "message" : str(e)})

    SSH_CONNECTION_DICT[request.session.session_key] = s
    
    data = False

    if len(packages) == 0: 
        data = False
    else:
        # # if platform.system() == "Windows":
        # if Host == "192.168.1.15" or Host == "192.168.1.75":
        #     data = getWindowService(s, packages)
        #     # data = searchService(s, packages)
        # else:
        #     data = searchPackages(s , packages)
        data = searchPackages(s, packages)

    # hahadata = Application.processSSHInfo(s)
    hahadata = {}
    return JsonResponse({"error" : False , "message" : "Connection Established Successfully" , "data" : data , "hahadata" : hahadata})

def searchService(s , packages):
    output = {"packages" : {}}
    for package in packages:
        for process in s.Win32_Process(name=package):
            output["packages"][package] = {
                "name" : process.ExecutablePath,
                "status" : "Running",
                "size" :  "0",
            }
    return output
def searchPackages(s , packages):
    output = {"packages" : {}}
    data = ""
    for package in packages:
        cmd = "systemctl status " + package
        stdin, stdout, stderr = s.exec_command(cmd)
        data = stdout.read().decode('utf-8').split("\n")[:9]
        if (len(data) > 1):
            details = data[0].strip()
            load = data[1].strip()
            active = data[2].strip()
            pid = data[-3].strip()
            if "dead" in active:
                output["packages"][package] = {
                    "name" : details,
                    "status" : "STOPPED",
                    "is_active" : active,
                    "load" : load,
                    "pid" :pid,
                }
            elif "running" in active:
                output["packages"][package] = {
                    "name" : details,
                    "status" : "RUNNING",
                    "is_active" : active,
                    "load" : load,
                    "pid" :pid,
                }
            elif "failed" in active:
                output["packages"][package] = {
                    "name" : details,
                    "status" : "FAILED",
                    "is_active" : active,
                    "load" : load,
                    "pid" :pid,
                }
            else:
                output["packages"][package] = False
    return output

@csrf_exempt
def getSSHData(request):

    if ((request.session.session_key in SSH_CONNECTION_DICT) and (SSH_CONNECTION_DICT[request.session.session_key] != None)):
        return JsonResponse(Application.processSSHInfo(SSH_CONNECTION_DICT[request.session.session_key]))
    else:
        return JsonResponse({"error" : True , "message" : "SSH Connection Lost / Not Established"})


def getCPUOnly(request):
    data = {
        "CPU" : {
            "usage" : CPU.usage()
        }
    }

    return JsonResponse(data)

def mainFunction(request):
    data = {
        "CPU" : {
            "usage" : CPU.usage(),
            "speed" : "",#CPU.speed(),
            "stats" : CPU.stats()
        },
        "disk" : {
            "stats" : Disk.diskStats()
        },

        "memory" : {
            "swap" : Memory.swapMemory(),
            "virtual" : Memory.virtualMemory()

        },
        "application" : {
            "info" : Application.processInfo()
        }
    }

    return JsonResponse(data)


@login_required(redirect_field_name=None)
@permission_required("dashboard.view_apm" , "/noperm/")
def apm_monitoring(request):
    dc = DeviceCapibility.objects.all()
    type_list = ['Server', 'Blade Chassis', 'vm', 'Network']
    selectOptionDevices = []
    assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
    for device in dc:
        ipa = device.ip
        user = device.user
        pwd = device.pwd
        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            if (ipa == fullIP):
                selectOptionDevices.append({
                    "name" : device.name,
                    "ip" : ipa,
                    "user":user,
                    "pwd":pwd
                })
                break
    data = {
        "snmpdevices" : selectOptionDevices,
    }
    return render(request, 'dashboard/apm.html', data)