from celery import shared_task
from dashboard.views_apm import CPU
from dashboard.models import WebsiteLinks, Notif, TestModal, DeviceCapibility, DeviceSetting , SnmpDeviceSetting
from dashboard.views_network import SaveSNMPDataToDB as snmpDeviceRecording 
from dashboard.views_network import insertData
import requests, time
from dashboard.schedulejobs import scan
from dashboard.viewsSNMP import getDetails as GetSNMPData
from dashboard.views import basicInfo, iowatInfo, get_cpu_temp, networkspeed
from dashboard.models import Notif, RaiseTicket
import datetime
# @shared_task(name = "print_msg_main")
# def print_message(message, *args, **kwargs):
#   print(f"Celery is working!! Message is {message}")
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
@shared_task(name = "collectSNMPData")
def snmpDataCollection():
    #CheckIfGetMaxValue
    obj = DeviceCapibility.objects.filter(is_snmp=True)
    for details in obj:

        if not scan(details.ip):
            generateAlert("SNMP", 'high', details.ip + " is down ", details.ip, details.ip+" is not reachable")
        
        response = GetSNMPData(request = None , host = details.ip , communityStr = details.commString)
        # print("Response: ",details.ip,response)
        if response != False:
            try:
                res = snmpDeviceRecording(response , details.ip)
                # res1 = insertData(response , details.ip)
                # print("Snmp", res1)
                try:
                    threshold = SnmpDeviceSetting.objects.get(ip=details.ip)
                except:
                    threshold = SnmpDeviceSetting.objects.create(ip=details.ip)
                if "ram_used" in res:
                    if res["ram_used"] >= threshold.usedRam:
                        generateAlert("SNMP" , "high" , details.ip + " has high ram usage" , details.ip , details.ip + " has high ram usage")
                if "swap_used" in res:
                    if res["swap_used"] >= threshold.usedSMemory:
                        generateAlert("SNMP" , "high" , details.ip + " has high memory usage" , details.ip , details.ip + " has high memory usage")
                if "storage_used" in res:
                    if res["storage_used"] >= threshold.usedStorage:
                        generateAlert("SNMP" , "high" , details.ip + " has high storage usage" , details.ip , details.ip + " has high storage usage")    

                # if float(res["cpu"].split(",")[0]) >= threshold.cpu_threshold:
                #     generateAlert("SNMP" , "high" , details.ip + " has high cpu usage" , details.ip , "")  
            except:
                pass                  


        else:
            if (details.ip != "10.1.45.3"):
                generateAlert("SNMP", 'medium', details.ip + " is down (SNMP) ", details.ip, details.ip+" is not reachable")


@shared_task(name = "collectDashboardData")
def collectData():
    # print("--Collecting Data of Appliance-->")
    cpuPercentage,usedRam,AvailRam,totalRam,usedSMemory,availSMemory,totalStorage,usedStorage,freeStorage = basicInfo()
    
    # total_users, web_websites, dc, notification, camera = usage_analytics()
    temperature = get_cpu_temp()
    # process = running_process()   
    iowait = iowatInfo()
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

@shared_task(name = "collectWebsiteData")
def WemMonitoring():
    # print("--Collecting Data of Web Monitoring-->")
    websites_pack = WebsiteLinks.objects.all()
    
    # data = []
    # rt = []
    # total = 0
    # down = 0

    for url in websites_pack:
        # state = False
        startTime = time.time()
        webObjects = WebsiteLinks.objects.get(website_name = url.website_name)
        if webObjects.repeat > 4:
            webObjects.repeat = 0
            webObjects.save()
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
        # print("R", r)
        if r == 0:
            webObjects.repeat = 0
            webObjects.save()
            checkHeat("web",0, 0, 1, "Unreachable "+ url.website_name)

        endTime = time.time()

        ressponse = round((endTime - startTime),2)
        if webObjects.response_time != '':
            webObjects.response_time = str(webObjects.response_time) + "," + str(ressponse)
        else:
            webObjects.response_time = str(ressponse)

        # print("Response ",ressponse)
        # print("Repeat ",webObjects.repeat)

        if ressponse > 2:
            webObjects.repeat += 1
        else:
            webObjects.repeat = 0

        # print("REpeat After", webObjects.repeat)

        webObjects.save()
        if webObjects.repeat == 3:
            checkHeat("web",3, 5, ressponse, "Response Time for "+ url.website_name)
    # print("--End Collecting Data of Web Monitoring-->")

@shared_task(name = "raiseTicketToAdmin")
def raiseticket():
    date_format_str = '%Y-%m-%d %H:%M:%S.%f'
    notifications = Notif.objects.filter(is_raised=False)
    for n in notifications:
        given_time = datetime.datetime.strptime(str(n.date), date_format_str)
        final_time = datetime.datetime.now()
        compare_time = final_time - given_time
        if compare_time > datetime.timedelta(minutes=30):
            title = n.title
            content =n.content
            newTicket = RaiseTicket()
            newTicket.user = None
            newTicket.fname = "tyyy"
            newTicket.lname = "rtryt"
            newTicket.email = "emil"
            newTicket.subject = title
            newTicket.msg = content
            newTicket.save()
            n.is_raised = True
            n.save()