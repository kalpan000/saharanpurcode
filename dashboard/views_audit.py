from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from dashboard.views_apm import CPU
from django.template.loader import get_template
from .utils import render_to_pdf 
from dashboard.views import basicInfo, iowatInfo, usage_analytics, running_process, get_cpu_temp, networkspeed
from .models import *
import itertools
from datetime import datetime
#Creating our view, it is a class based view





def date_min(timestamp):
    return timestamp.strftime("%x %H:%M")

def UpTime(ip):
    try:
        records = MyDeviceSNMPData.objects.filter(device = MyDevice.objects.get(ip = ip)).order_by("created_at")
        # start_date = records.first().created_at
        # todays_date = datetime.now()
        # days = todays_date - start_date
        # total_minutes = (days.seconds) / 60
        groups = itertools.groupby(records , lambda record : date_min(record.created_at))
        start_date = records.first().created_at
        last_date = datetime.now()
        first_run = True
        count = 0
        for g, m in groups:
            if (first_run):
                start_date = g
                first_run = False
            count += 1
            print("Groups", g)
        
        total_min = (last_date - (datetime.strptime(start_date, '%m/%d/%y %H:%M'))).seconds / 60
        print(total_min)
        uptime = count / total_min * 100
        return round(uptime, 2)
    except:
        pass

def user_info():
    users = UserProfile.objects.all().prefetch_related("user")
    return users

def web_info():

    results = WebsiteLinks.objects.all()

    output = {
        "websites" : [],
        "total" : len(results)
    }

    for record in results:
        output["websites"].append( {"name" : record.website_name , "isFavorite" : record.is_favorite , "responses" : record.response_time.split(",") , "created_at" : record.created_at} )

    return output


def cctv_info():

    results = Product.objects.all()

    output = {
        "cctvs" : [ ],
        "total" : len(results)
    }

    for record in results:
        output["cctvs"].append( {"name" : record.name , "created_at" : record.created_at, "isFavorite":record.is_favorite} )

    return output

def assets_info():
    # ASSETS MANAGEMENT
    assets = []
    datacenter = addDataCenter.objects.all()
    for dc in datacenter:
        rows = addDataCenterRow.objects.filter(data_center=dc)
        rowsTotal = rows.count()
        racks = AddDataCenterRackcabinet.objects.filter(datacenter=dc, is_delete=False)
        racksTotal = racks.count()
        deviceTotal = AddDevice.objects.filter(datacenter=dc).count()
        assets.append({
            "dataCenterTag" : dc.dataCenterTag,
            "DataCenterName" : dc.DataCenterName,
            "sqr_mtr" : dc.sqr_mtr,
            "Add_country" : dc.Add_country,
            "Add_state" : dc.Add_state,
            "Address" : dc.Address,
            "Contact" : dc.Contact,
            "PersonalDet_fname" : dc.PersonalDet_fname,
            "PersonalDet_email" : dc.PersonalDet_email,
            "phone" : dc.phone,
            "Capacity_in_MW" : dc.Capacity_in_MW,
            "totalrow" : rowsTotal,
            "totalrack" : racksTotal,
            "totaldevice" : deviceTotal
        })

    return assets

def deviceInfo():
    devicess = AddDevice.objects.all()
    assets = {
        "network" : [],
        "server": [],
        "storage": []
    }
    for device in devicess:
        ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)
        if device.type_of_device == "Network":
            assets['network'].append({"id":device.id,"name":device.Device_Asset_Tag, "ip":ip ,"uptime": UpTime(ip)})
        elif device.type_of_device == "Server":
            assets['server'].append({"id":device.id,"name":device.Device_Asset_Tag, "ip":ip ,"uptime": UpTime(ip)})
        elif device.type_of_device == "Storage":
            assets['storage'].append({"id":device.id,"name":device.Device_Asset_Tag, "ip":ip ,"uptime": UpTime(ip)})
    return assets

def notification_info():
    obj = Notif.objects.all()
    total_notification = obj.count()
    lSeverity = obj.filter(severity = 'low').count()
    mSeverity = obj.filter(severity = 'medium').count()
    hSeverity = obj.filter(severity = 'high').count()

    WebMonitoringData = obj.filter(content__icontains = 'Response').count()

    cpuUsage = obj.filter(content__icontains = 'CPU').count()
    cpuTemp = obj.filter(content__icontains = 'Temerature').count()
    Ram = obj.filter(content__icontains = 'RAM').count()
    Swap = obj.filter(content__icontains = 'SWAP').count()
    Storage = obj.filter(content__icontains = 'Storage').count()
    IOwait = obj.filter(content__icontains = 'IOWAT').count()
    applianceData = cpuUsage+cpuTemp+Ram+Swap+Storage+IOwait
    dashboardData = obj.filter(parent__icontains = 'snmp').count()

    notifications = {
        # 'cpuUsage':cpuUsage,
        # 'cpuTemp':cpuTemp,
        # 'Ram':Ram,
        # 'Swap':Swap,
        # 'Storage':Storage,
        # 'IOwait':IOwait,
        'low':lSeverity,
        'med':mSeverity,
        'high':hSeverity,
        'web':WebMonitoringData,
        'appliance':applianceData,
        'dashboard':dashboardData,
        'total':total_notification
    }
    return notifications

def device_capabilities_info():
    devices = DeviceCapibility.objects.filter(is_active=False)
    return devices

def GeneratePdf(request):
    # print("--Collecting Data of Appliance-->")
    cpuPercentage,usedRam,AvailRam,totalRam,usedSMemory,availSMemory,totalStorage,usedStorage,freeStorage = basicInfo()
    # total_users, web_websites, dc, notification, camera = usage_analytics()
    temperature = get_cpu_temp()
    # process = running_process()   
    iowait = iowatInfo()  

    terminalLog = TerminalLog.objects.all()

    data = {
        'users':user_info(),
        'base_url':request.scheme+"://"+request.META['HTTP_HOST'],
        'cpuPercentage':cpuPercentage,
        'usedRam':usedRam,
        'AvailRam':AvailRam,
        'totalRam':totalRam,
        'usedSMemory':usedSMemory,
        'availSMemory':availSMemory,
        'totalStorage':totalStorage,
        'usedStorage':usedStorage,
        'freeStorage':freeStorage,
        'temperature':temperature,
        'iowait':iowait,
        'cpu':CPU.usage()["data"]["CPUUtilization"],
        'cctv':cctv_info(),
        'web':web_info(),
        'terminalLog' : terminalLog,
        'assets':assets_info(),
        'notifications':notification_info(),
        'capabilities':device_capabilities_info(),
        'deviceinfo' : deviceInfo(),
    }
    # pdf = render_to_pdf('audit.html', data)
    # return HttpResponse(pdf, content_type='application/pdf')
    return render(request, "audit.html", data)