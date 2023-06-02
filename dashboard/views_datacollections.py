from dashboard.views import basicInfo, iowatInfo, usage_analytics, running_process, get_cpu_temp, networkspeed
from dashboard.views_apm import CPU
from dashboard.models import ApplianceDataCollection, DashboardDataCollection, SNMPDataCollection, WebsiteLinks, Notif, TestModal, DeviceCapibility, DeviceSetting
from dashboard.views_network import insertData as snmpDeviceRecording 
import requests, time
import json
from dashboard.viewsSNMP import getDetails as GetSNMPData
import threading
from celery import shared_task

@shared_task(name = "collect_Data")
def collectData():
    # print("--Collecting Data of Appliance-->")
    cpuPercentage,usedRam,AvailRam,totalRam,usedSMemory,availSMemory,totalStorage,usedStorage,freeStorage = basicInfo()
    # total_users, web_websites, dc, notification, camera = usage_analytics()
    temperature = get_cpu_temp()
    # process = running_process()   
    iowait = iowatInfo()
    # #Appliance Data
    # insert('cpuPercentage',cpuPercentage, ApplianceDataCollection)
    # checkHeat(40, 60,  cpuPercentage, "CPU Usage")

    # insert('usedRam',usedRam, ApplianceDataCollection)
    # insert('AvailRam',AvailRam, ApplianceDataCollection)
    # insert('totalRam',totalRam, ApplianceDataCollection)
    # checkHeat(40, 60,(usedRam/totalRam)*100, "RAM Usage") # U = 2, A = 5, T = 7

    # insert('usedSMemory',usedSMemory, ApplianceDataCollection)
    # insert('availSMemory',availSMemory, ApplianceDataCollection)
    # checkHeat(40, 60,(usedSMemory/(availSMemory+usedSMemory))*100, "SWAP Memory Usage")

    # insert('totalStorage',totalStorage, ApplianceDataCollection)
    # insert('usedStorage',usedStorage, ApplianceDataCollection)
    # insert('freeStorage',freeStorage, ApplianceDataCollection)
    # checkHeat(40, 60, (usedStorage/totalStorage)*100, "Storage")

    # insert('temperature',temperature, ApplianceDataCollection)
    # checkHeat(25, 40, temperature, "CPU Temerature")

    # insert('process',process, ApplianceDataCollection)
    # insert('iowat',iowat, ApplianceDataCollection)
    # checkHeat(40, 60, iowat, "IOWAT Usage")
    # print("--End Collecting Data of Appliance-->\n")
    # print("--Collecting Data of Dashboard-->")
    # #Dashboard Data
    # insert('total_users',total_users, DashboardDataCollection)
    # insert('web_websites',web_websites, DashboardDataCollection)
    # insert('dc',dc, DashboardDataCollection)
    # insert('notification',notification, DashboardDataCollection)
    # insert('camera',camera, DashboardDataCollection)
    # print("--End Collecting Data of Appliance-->\n")
    #swap
    try:
        threshold = DeviceSetting.objects.get(id=1)
    except:
        threshold = DeviceSetting.objects.update_or_create(id = 1)
    swap = [usedSMemory,availSMemory]
    swap = map(str, swap) 
    swap = ",".join(swap)
    insert("swap", swap, TestModal)
    #checkHeat
    checkHeat("appliance", 40, threshold.cpu_threshold,  cpuPercentage, "CPU Usage")
    #storage
    storage = [usedStorage,freeStorage]
    storage = map(str, storage) 
    storage = ",".join(storage)
    insert("storage",storage,TestModal)
    #checkHeat
    checkHeat("appliance", 40, threshold.usedRam,(usedRam/totalRam)*100, "RAM Usage") # U = 2, A = 5, T = 7
    #iowait
    insert("iowait",iowait,TestModal)
    #checkHeat
    checkHeat("appliance", 40, threshold.usedSMemory,(usedSMemory/(availSMemory+usedSMemory))*100, "SWAP Memory Usage")
    #cpuUtil
    cpuUtil = cpuPercentage
    insert("cpuUtil",cpuUtil,TestModal)
    #checkHeat
    checkHeat("appliance", 40, threshold.usedStorage, (usedStorage/totalStorage)*100, "Storage")
    #ram
    ramdata = [usedRam, AvailRam]
    ramdata = map(str, ramdata) 
    ramdata = ",".join(ramdata)
    # print(ramdata)
    insert("ram",ramdata,TestModal)
    #checkHeat
    checkHeat("appliance", 25, threshold.temperature, temperature, "CPU Temerature")
    # #Core Util
    BYTES, PKTS = networkspeed()
    PKTS = map(str, PKTS) 
    PKTS = ",".join(PKTS)
    insert("network",PKTS,TestModal)
    #checkHeat
    checkHeat("appliance", 40, threshold.iowait, iowait, "IOWAT Usage")

    data = CPU.usage()["data"]["CPUUtilization"]
    # mapping 
    data = map(str, data) 
    data = ",".join(data)
    insert("cpu",data,TestModal)

    #web Monitoring Data
    WemMonitoring()

    #CheckIfGetMaxValue
    obj = DeviceCapibility.objects.filter(is_snmp=True)
    for details in obj:
        try:
            response = GetSNMPData(request = None , host = details.ip , communityStr = details.commString)
            # print("Response: ",response)
            if response != False:
                snmpDeviceRecording(response , details.ip)
            else:
                generateAlert("SNMP", 'medium', details.ip + " is down (SNMP) ", details.ip, str(err))
        except Exception as err:
            print("Exception")
            generateAlert("SNMP", 'medium', details.ip + " is down (SNMP) ", details.ip, str(err))
    

def checkHeat(parent, avg, max, data, title): #heatValue is predefined data eg. if temp is greater than 40 generater alert
    # heatValue = 40, data = 34
    # if (34 > 40) then alertBox
    if (data > max):
        generateAlert(parent, 'high', data, title, title + " has high severity of value " + str(data))

def insert(types, data, model):
    # t = type(data)
    # if (t == 'list'):
    #     str(data)
    # elif t == "dict":
    #     json.dumps(data)
    model.objects.create(value=1, type=types , valueArr=data)


def generateAlert(parent=None,status=None, data=None, title=None, content=None): #id, status=[low, medium, high], 
    notification = Notif(parent=parent,title=title, data=data, severity=status, content=content)
    notification.save()
    # print("New Notification Created\nSTATUS: ",status,"\nTITLE: ", title, "\nData: ", data)


def WemMonitoring():
    print("--Collecting Data of Web Monitoring-->")
    websites_pack = WebsiteLinks.objects.all()
    
    # data = []
    # rt = []
    # total = 0
    # down = 0

    for url in websites_pack:
        # state = False
        startTime = time.time()
        webObjects = WebsiteLinks.objects.get(website_name = url.website_name)
        try:
            r = requests.get(url.website_name).status_code
        except ConnectionError as err:
            r = 0
        except requests.exceptions.RequestException as err:
            r = 0
        # if r == 200:
        #     state = True
        #     total = total + 1
        # else:
        #     state=False
        #     down = down + 1
        endTime = time.time()
        if webObjects.response_time != '':
            
            webObjects.response_time = str(webObjects.response_time) + "," + str(round((endTime - startTime),2))
        else:
            webObjects.response_time = str(round((endTime - startTime),2))
        webObjects.save()
        checkHeat("web",3, 5, round((endTime - startTime),2), "Response Time for "+ url.website_name)
    print("--End Collecting Data of Web Monitoring-->")