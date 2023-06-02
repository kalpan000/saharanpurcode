from random import random
from django.http import JsonResponse
from django.shortcuts import render
from .models import DeviceCapibility, AddDevice, MyDeviceSNMPInterface
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import itertools
from django.core import serializers
import random
# # for 1 day data grouping by minutes 
def date_min(timestamp):
    return timestamp.strftime("%x %H:%M") 
    # return timestamp.strftime("%H:%M") 

def Storageindex(request):
    dc = DeviceCapibility.objects.filter(is_snmp = True)
    type_list = ['Storage']
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
    return render(request, 'summary/server.html', data)
def cpu_percent(cpu):
    cpu = list(map(float, cpu))
    cpu = list(map(int, cpu))
    # print(cpu)
    length = len(cpu) #4
    # print(length)
    sum = 0
    for i in range(0, length):
        sum += cpu[i]
    return sum / length

def custUptime(sec):
    time = int(sec)/100
    day = time // (24 * 3600)
    time = time % (24 * 3600)
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    time %= 60
    seconds = time
    return str(int(day))+"D "+str(int(hour))+":"+str(int(minutes))+":"+str(round(seconds,2))

@csrf_exempt
def Storagedata(request): 
    host = request.GET["host"]
    # print(host)
    interfaces = MyDeviceSNMPInterface.objects.filter(deviceData__device__ip = host).order_by("-deviceData__created_at")[:1].prefetch_related("deviceData" , "deviceData__device") 
    # print(interfaces)
    partIP = host.split(".") 
    AssetDevices = AddDevice.objects.filter(IP_Address_col1=partIP[0],IP_Address_col2=partIP[1],IP_Address_col3=partIP[2],IP_Address_col4=partIP[3])
    serializedAssetDevice = list(AssetDevices.values())[0]
    data = {
        "location": "",
        "contact": "",
        "description": "",
        "deviceDataID" : 0,
        "storage_total" : 0,
        "storage_available" : 0,
        "storage_used" : 0,
        "ram_total" : 0,
        "ram_used" : 0,
        "ram_available" : 0,
        "swap_total" : 0,
        "swap_used" : 0,
        "swap_available" : 0,
        "inbound" : 0,
        "outbound" : 0,
        "cpu" : {},
        "cpu_util" : 0,
        "interfaces" : [],
        "uptime" : 0,
    }
    runOnce = True

    data["assets"] = serializedAssetDevice

    deviceData = interfaces.first().deviceData
    data["description"] = deviceData.device.description
    data["contact"] = deviceData.device.contact
    data["location"] = deviceData.device.Location
    data["deviceDataID"] = deviceData.id
    data["storage_total"] = deviceData.storage_total
    data["storage_available"] = deviceData.storage_available
    data["storage_used"] = deviceData.storage_used
    data["ram_total"] = deviceData.ram_total
    data["ram_used"] = deviceData.ram_used
    data["ram_available"] = deviceData.ram_available
    data["swap_total"] = deviceData.swap_total
    data["swap_used"] = deviceData.swap_used
    data["swap_available"] = deviceData.swap_available
    data["uptime"] = custUptime(deviceData.uptime)
    try:
        data["cpu"] = deviceData.cpu.split(",")
        data["cpuLables"] = random.randint(12, 90)
        data["cpu_util"] = cpu_percent(data["cpu"])
    except Exception as err:
        data["cpu"] = 0
        data["cpuLables"] = 0
        data["cpu_util"] = 0
    
    data["name"] = deviceData.device.name
    data["id"] = deviceData.device.id
    
    interfaces =  MyDeviceSNMPInterface.objects.filter(deviceData__id = deviceData.id)

    try:
        for interface in interfaces:

            data["inbound"] += interface.inOctect
            data["outbound"] += interface.outOctect
        
        
        data["interfaces"] = list(interfaces.values())
        return JsonResponse({"data":data})
    except Exception as err:
        return JsonResponse({"data":str(err)})

def storage_summary(request , returnjsonobj = True):
    days = request.GET.get("days", 1)
    dc = DeviceCapibility.objects.all()
    type_list = ['Server']
    selectOptionDevices = []
    assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
    for device in dc:
        ipa = device.ip
        # user = device.user
        # pwd = device.pwd
        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            if (ipa == fullIP):
                selectOptionDevices.append(ipa)
                break
    timeThreshold = datetime.now() - timedelta(days=int(days))
    
    query = MyDeviceSNMPInterface.objects.filter(deviceData__device__ip__in = selectOptionDevices,deviceData__created_at__gt = timeThreshold).prefetch_related("deviceData" , "deviceData__device")
    

    groups = itertools.groupby( query , lambda query_item : date_min(query_item.deviceData.created_at) )
    
    data = {
        "groups" : [],
        "storage_total" : 0,
        "storage_available" : 0,
        "storage_available_groups" : [],
        "storage_used" : 0,
        "storage_used_groups" : [],
        "ram_used" : 0,
        "ram_used_groups" : [],
        "ram_total" : 0,
        "ram_available" : 0,
        "ram_available_groups" : [],
        "swap_used" : 0,
        "swap_used_groups" : [],
        "swap_total" : 0,
        "swap_available" : 0,
        "swap_available_groups" : [],
        "total_inbound" : 0,
        "total_outbound" : 0,
        "total_inbound_err" : 0,
        "total_outbound_err" : 0,
        "total_speed" : 0,        
        "cpu" : 0,
    }


    busyDevices = {}

    read_deviceData = []
    read_device = []
    total_groups = 0

    for group , interfaces in groups:

        temp_storage_used = 0
        temp_storage_available = 0

        temp_ram_used = 0
        temp_ram_available = 0
        
        temp_swap_used = 0
        temp_swap_available = 0

        totalInterfacesInGroup = 0
        total_groups += 1
    
        for interface in interfaces:
            totalInterfacesInGroup += 1
            data["total_inbound"]  += interface.inOctect
            data["total_outbound"]  += interface.outOctect
            data["total_speed"] += interface.speed

            data["total_outbound_err"]  += interface.outErr
            data["total_inbound_err"]  += interface.inErr


            deviceID = str(interface.deviceData.device.id)

            if deviceID not in busyDevices:
                busyDevices[deviceID] = {
                    'name' : interface.deviceData.device.ip,
                    "inbound" : interface.inOctect,
                    "outbound" : interface.outOctect,
                    "ip" : interface.deviceData.device.ip,
                }
            else:
                busyDevices[deviceID]["inbound"] += interface.inOctect   
                busyDevices[deviceID]["outbound"] += interface.outOctect


            if interface.deviceData.device.id not in read_device:
                data["storage_total"] += interface.deviceData.storage_total
                data["ram_total"] += interface.deviceData.ram_total
                data["swap_total"] += interface.deviceData.storage_total
                read_device.append( interface.deviceData.device.id )
                

            if interface.deviceData.id in read_deviceData:
                continue

            read_deviceData.append(interface.deviceData.id)


            # t = list(map(int , interface.deviceData.cpu.split(",")))
            # data["cpu"] += (sum(t) / len(t))

            temp_storage_available += interface.deviceData.storage_available
            temp_storage_used += interface.deviceData.storage_used

            temp_ram_available += interface.deviceData.ram_available
            temp_ram_used += interface.deviceData.ram_used

            temp_swap_available += interface.deviceData.swap_available
            temp_swap_used += interface.deviceData.swap_used

            data["storage_available"] += interface.deviceData.storage_available
            data["storage_used"] += interface.deviceData.storage_used
            data["ram_available"] += interface.deviceData.ram_available
            data["ram_used"] += interface.deviceData.ram_used
            data["swap_available"] += interface.deviceData.swap_available
            data["swap_used"] += interface.deviceData.swap_used


        
        print("Group name" , group , "Total Interfaces" , totalInterfacesInGroup)
        data["storage_available_groups"].append(temp_storage_available)
        data["storage_used_groups"].append(temp_storage_used)
        data["ram_available_groups"].append(temp_ram_available)
        data["ram_used_groups"].append(temp_ram_used)
        data["swap_available_groups"].append(temp_swap_available)
        data["swap_used_groups"].append(temp_swap_used)

        temp = group.split(" ")
        # day = "/".join(temp[0].split("/")[:1])
        time = temp[1]
        # date = day + " " + time
        data["groups"].append(time)


    
    totalInterfaces = len(query)
    readDeviceLen = len(read_deviceData)

    if total_groups == 0:
        total_groups == 1
        data["groups"].append("0")

    if readDeviceLen == 0:
        readDeviceLen = 1

    if totalInterfaces == 0:
        totalInterfaces = 1


    data["storage_available_groups"] = [ round(i / total_groups , 2) for i in data["storage_available_groups"] ]
    data["storage_used_groups"] = [ round(i / total_groups , 2) for i in data["storage_used_groups"] ]
    data["ram_available_groups"] = [ round(i / total_groups , 2) for i in data["ram_available_groups"] ]
    data["ram_used_groups"] = [ round(i / total_groups , 2) for i in data["ram_used_groups"] ]
    data["swap_available_groups"] = [ round(i / total_groups , 2) for i in data["swap_available_groups"] ]
    data["swap_used_groups"] = [ round(i / total_groups , 2) for i in data["swap_used_groups"] ]

    data["cpu"] = ""
    data["storage_total"] = round(data["storage_total"] , 2)
    data["storage_available"] = round(data["storage_available"]  / readDeviceLen , 2)
    data["storage_used"] = round(data["storage_used"]  / readDeviceLen , 2)

    data["ram_total"] = round(data["ram_total"] , 2)
    data["ram_available"] = round(data["ram_available"]  / readDeviceLen , 2)
    data["ram_used"] = round(data["ram_used"]  / readDeviceLen , 2)

    data["swap_total"] = round(data["swap_total"] , 2)
    data["swap_available"] = round(data["swap_available"]  / readDeviceLen , 2)
    data["swap_used"] = round(data["swap_used"]  / readDeviceLen , 2)

    data["total_inbound"] = round(data["total_inbound"] / totalInterfaces , 2)
    data["total_outbound"] = round(data["total_outbound"] / totalInterfaces , 2)
    data["total_inbound_err"] = round(data["total_inbound_err"] / totalInterfaces , 2)
    data["total_outbound_err"] = round(data["total_outbound_err"] / totalInterfaces , 2)
    data["total_speed"] = round(data["total_speed"] / totalInterfaces , 2)
    
    data["busy_devices"] = busyDevices

    data["total_groups"] = total_groups
    if not returnjsonobj:
        return {"data":data}
    return JsonResponse({"data":data})