from datetime import datetime, timedelta
from .models import SNMPDataCollection, SNMPInterfaceDataCollection, DeviceCapibility, AddDevice
from django.http import JsonResponse

def str2list(str):
    if str == None or str == "" or len(str) <= 1:
        return 0
    arr = str.split(",")

    if len(arr) == 0:
        return []
    
    arr = list(map(float , arr))
    return arr


def listSum(l):
    s = 0
    if l == 0:
        return s
    for i in l:
        s += i
    return s

def str2list2getIndex(str , index):
    if str == None or str == "" or len(str) <= 1:
        return 0

    arr = str.split(",")

    if len(arr) - 1 < index:
        return 0
    arr = list(map(float , arr))

    return arr[index]
 
def descendingOrder(list , element):
    index = 0
    output = []
    for i in list:
        if list[i] < element:
            output.append(list[i])
        else:
            output.append(element)
        index += 1

    return output


def NetworkSummaryFor24Hours(reuqest):
    deviceTypes = ["Network" , "Load Balancer"]
    allDevices = DeviceCapibility.objects.filter(is_snmp=True)
    assetDevices = AddDevice.objects.filter(type_of_device__in = deviceTypes) 

    # filtering 
    # get ips of all the devices from assetDevices where their type is `deviceTypes`
    # and their ip exists in `allDevices` model

    filteredIPs = []
    totalWatts = 0
    filteredDevices = []

    for assetDevice in assetDevices:
        filteredIPs.append(str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + 
            str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4))
        totalWatts += assetDevice.deviceWatt
        
    for device in allDevices:      
        if device.ip in filteredIPs:
            filteredDevices.append({
                "name" : device.name,
                "ip" : device.ip
            })
 
    totalInterfaceDevice = len(filteredDevices)


    # main data extraction and formatting

    # we need only 24 hour data 
    timeThreshold = datetime.now() - timedelta(hours=24)

    totalInbound = 0
    totalOutbound = 0
    totalRam = 0
    totalStorage = 0
    interfaceCount = 0
    totalRamUtilizationInADay = 0
    totalStorageUtilizationInADay = 0
    retrieveOnce = True
    ALL_DATA = []


    for device in filteredDevices:
        
        cpu = 0
        inbound = 0
        outbound = 0
        
        snmpDetails = SNMPDataCollection.objects.filter(ip = device["ip"] , created_at__lt=timeThreshold).order_by("-created_at")

        # looping all the snmpDevices     
        for snmpData in snmpDetails:

            # skip this device if its interface details are empty
            if snmpData.interfaces == None or snmpData.interfaces == "" or len(snmpData.interfaces) <= 1:
                continue
            
            
            # get the interfaces details from SNMPInterfaceDataCollection
            interfaceDetails = SNMPInterfaceDataCollection.objects.filter(id__in = list(map( int , snmpData.interfaces.split(",") )))
            interfaceCount += len(interfaceDetails)
            
            # total ram and storage utilization in a day
            totalRamUtilizationInADay += str2list2getIndex(snmpData.ram , 2)
            totalStorageUtilizationInADay += str2list2getIndex(snmpData.storage , 2)
            # print("Always " , snmpData.ram , snmpData.storage)
            
            # we need to retrieve total ram, storage and cpu only once
            if retrieveOnce:
                # print("Retrieve Once" , snmpData.ram , snmpData.storage)
                a = str2list2getIndex(snmpData.ram , 0)
                totalRam += a
                totalStorage += str2list2getIndex(snmpData.storage , 0)
                cpu += listSum(str2list(snmpData.cpu))
                if a != 0:
                    retrieveOnce = False
            

            for interfaceDetail in interfaceDetails:

                inbound += interfaceDetail.inbound
                outbound += interfaceDetail.outbound
                totalInbound += interfaceDetail.inbound
                totalOutbound += interfaceDetail.outbound




        ALL_DATA.append({
            "ip" : device["ip"],
            "cpu" : cpu,
            "busy" : inbound + outbound
        })

    
    top5busy = sorted(ALL_DATA, key = lambda i: i['busy'],reverse=True)[:5]
    top5cpu = sorted(ALL_DATA, key = lambda i: i['cpu'],reverse=True)[:5]


    data = {
        "totalDevice": len(allDevices),
        "totalInterfaceDevice": totalInterfaceDevice,
        "inbound": totalInbound,
        "outbound": totalOutbound,
        "interface": interfaceCount,
        "majorData" : ALL_DATA,
        "top5busy": top5busy,
        "top5cpu": top5cpu,
        "totalRam": totalRam,
        "totalRamUtilizationInADay" : totalRamUtilizationInADay,
        "totalStorage": totalStorage,
        "totalStorageUtilizationInADay" : totalStorageUtilizationInADay,
        "totalWatt" : totalWatts
    }

    return {"finaldata" : data , "error" : False}
    # return JsonResponse({"data" : data, "error": False})







def NetworkSummary(request):
    try:
        realDevice = []
        devices = DeviceCapibility.objects.filter(is_snmp=True)

        type_list = ['Network', 'Load Balancer', 'wlc']
        assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
        totalDevice = assetDevices.count()
        totalWatt = 0

        fullIPs = []

        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            fullIPs.append(fullIP)
            totalWatt = totalWatt + assetDevice.deviceWatt

        for device in devices:      
            if device.ip in fullIPs:
                realDevice.append({
                    "name" : device.name,
                    "ip" : device.ip
                })


        totalInterfaceDevice = len(realDevice)


        allData = []

        TOTALRAM = 0
        TOTALSTORAGE = 0

        totalInbound = 0
        totalOutbound = 0
        totalRam = 0
        totalStorage = 0
        interface = 0
        
        for d in realDevice:
            cpu = 0
            inbound = 0
            outbound = 0
            

            snmpd = SNMPDataCollection.objects.filter(ip = d["ip"]).order_by("-created_at")[:1]
            for interfaces in snmpd:

                if interfaces.interfaces == None or interfaces.interfaces == "" or len(interfaces.interfaces) <= 1:
                    continue

                inter = SNMPInterfaceDataCollection.objects.filter(id__in = list(map(int , interfaces.interfaces.split(","))) )
                for details in inter:
                    interface = interface + 1
                    inbound = inbound + details.inbound
                    outbound = outbound + details.outbound
                    totalInbound += details.inbound
                    totalOutbound += details.outbound

                    totalRam += str2list2getIndex(interfaces.ram , 1)
                    cpu += listSum(str2list(interfaces.cpu))
                    totalStorage += str2list2getIndex(interfaces.storage , 1)
            TOTALRAM = totalRam / totalInterfaceDevice
            TOTALSTORAGE = totalStorage / totalInterfaceDevice
            allData.append({
                "ip" : d["ip"],
                "cpu" : cpu,
                "busy" : inbound + outbound
            })
        data = {
            "totalDevice": totalDevice,
            "totalInterfaceDevice": totalInterfaceDevice,
            "inbound": totalInbound,
            "outbound": totalOutbound,
            "interface": interface,
            "majorData" : allData,
            "totalRam": TOTALRAM,
            "totalStorage": TOTALSTORAGE,
            "totalWatt" : totalWatt,
        }
        return JsonResponse({
            "data" : data,
            "error": False
        })
    except Exception as err:
        return JsonResponse({
            "data" : "Something went wrong, " + str(err),
            "error": True
        })



def StorageSummary(request):
    try:
        realDevice = []
        devices = DeviceCapibility.objects.filter(is_snmp=True)

        type_list = ['Storage']
        assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
        totalDevice = assetDevices.count()
        totalWatt = 0

        fullIPs = []

        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            fullIPs.append(fullIP)
            totalWatt = totalWatt + assetDevice.deviceWatt

        for device in devices:      
            if device.ip in fullIPs:
                realDevice.append({
                    "name" : device.name,
                    "ip" : device.ip
                })


        totalInterfaceDevice = len(realDevice)


        allData = []

        TOTALRAM = 0
        TOTALSTORAGE = 0

        totalInbound = 0
        totalOutbound = 0
        totalRam = 0
        totalStorage = 0
        interface = 0
        
        for d in realDevice:
            cpu = 0
            inbound = 0
            outbound = 0
            

            snmpd = SNMPDataCollection.objects.filter(ip = d["ip"]).order_by("-created_at")[:1]
            for interfaces in snmpd:

                if interfaces.interfaces == None or interfaces.interfaces == "" or len(interfaces.interfaces) <= 1:
                    continue

                inter = SNMPInterfaceDataCollection.objects.filter(id__in = list(map(int , interfaces.interfaces.split(","))) )
                for details in inter:
                    interface = interface + 1
                    inbound = inbound + details.inbound
                    outbound = outbound + details.outbound
                    totalInbound += details.inbound
                    totalOutbound += details.outbound

                    totalRam += str2list2getIndex(interfaces.ram , 1)
                    cpu += listSum(str2list(interfaces.cpu))
                    totalStorage += str2list2getIndex(interfaces.storage , 1)
            TOTALRAM = totalRam / totalInterfaceDevice
            TOTALSTORAGE = totalStorage / totalInterfaceDevice
            allData.append({
                "ip" : d["ip"],
                "cpu" : cpu,
                "busy" : inbound + outbound
            })
        data = {
            "totalDevice": totalDevice,
            "totalInterfaceDevice": totalInterfaceDevice,
            "inbound": totalInbound,
            "outbound": totalOutbound,
            "interface": interface,
            "majorData" : allData,
            "totalRam": TOTALRAM,
            "totalStorage": TOTALSTORAGE,
            "totalWatt" : totalWatt,
        }
        return JsonResponse({
            "data" : data,
            "error": False
        })
    except Exception as err:
        return JsonResponse({
            "data" : "Something went wrong, " + str(err),
            "error": True
        })




    
def ServerSummaryIn24Hours(request):
    try:
        realDevice = []
        devices = DeviceCapibility.objects.filter(is_snmp=True)
        type_list = ['Server', 'Blade Chassis', 'vm']
        assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
        totalDevice = assetDevices.count()
        totalWatt = 0        

        totalBladeChasis = 0
        totalVMs = 0
        
      
        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            totalWatt = totalWatt + assetDevice.deviceWatt  
            its_type = assetDevice.type_of_device
            if (its_type == "Blade Chassis"):
                totalBladeChasis = totalBladeChasis + 1
            if (its_type == "vm"):
                totalVMs = totalVMs + 1
            for device in devices:
                ipa = device.ip                
                if (fullIP == ipa):
                    realDevice.append({
                        "name" : device.name,
                        "ip" : fullIP
                    })
                    break
        totalInterfaceDevice = len(realDevice)


        allData = []

       

        # we need only 24 hour data 
        timeThreshold = datetime.now() - timedelta(hours=24)
        totalInbound = 0
        totalOutbound = 0
        totalRam = 0
        totalStorage = 0
        interface = 0
        retrieveOnce = True
        ramUsageIn24Hours = 0
        storageUsageIn24Hours = 0
        # 
        TOTALRAM = 0
        TOTALSTORAGE = 0
        # 
        
        for d in realDevice:
            cpu = 0
            inbound = 0
            outbound = 0
            # interface = 0

            snmpDetails = SNMPDataCollection.objects.filter(ip = d["ip"] , created_at__gt=timeThreshold).order_by("-created_at")
            for snmpData in snmpDetails:

                if snmpData.interfaces == None or snmpData.interfaces == "" or len(snmpData.interfaces) <= 1:
                    continue

                interfaceDetails = SNMPInterfaceDataCollection.objects.filter(id__in = list(map(int , snmpData.interfaces.split(","))) )
                interface += len(interfaceDetails)
                ramUsageIn24Hours += str2list2getIndex(snmpData.ram , 2)
                storageUsageIn24Hours += str2list2getIndex(snmpData.storage , 2)

                if retrieveOnce:
                    a = str2list2getIndex(snmpData.ram , 0)
                    totalRam += a
                    totalStorage += str2list2getIndex(snmpData.storage , 0)
                    cpu += listSum(str2list(snmpData.cpu))
                    if a != 0:
                        retrieveOnce = False              
                    
                for interfaceDetail in interfaceDetails:
                    inbound = inbound + interfaceDetail.inbound
                    outbound = outbound + interfaceDetail.outbound
                    totalInbound += interfaceDetail.inbound
                    totalOutbound += interfaceDetail.outbound

            TOTALRAM = totalRam / totalInterfaceDevice
            TOTALSTORAGE = totalStorage / totalInterfaceDevice
            allData.append({
                "ip" : d["ip"],
                "cpu" : cpu,
                "busy" : inbound + outbound
            })

        top5busy = sorted(allData, key = lambda i: i['busy'],reverse=True)[:5]
        top5cpu = sorted(allData, key = lambda i: i['cpu'],reverse=True)[:5]
        #top5ram = sorted(allData, key = lambda i: i['ram'],reverse=True)[:5]
        #top5storage = sorted(allData, key = lambda i: i['storage'],reverse=True)[:5]

        data = {
            "totalDevice": totalDevice,
            "totalInterfaceDevice": totalInterfaceDevice,
            "inbound": totalInbound,
            "outbound": totalOutbound,
            "interface": interface,
            "majorData" : allData,
            "top5busy": top5busy,
            "top5cpu": top5cpu,
            "totalRam": TOTALRAM,
            "totalRamUtilizationInADay" : ramUsageIn24Hours,
            "totalStorage": TOTALSTORAGE,
            "totalStorageUtilizationInADay" : storageUsageIn24Hours,
            "totalBladeChasis" : totalBladeChasis,
            "totalVMs" : totalVMs,
            "totalWatt" : totalWatt
        }
        return JsonResponse({
            "data" : data,
            "error": False
        })
    except Exception as err:
        return JsonResponse({
            "data" : "Something went wrong, " + str(err),
            "error": True
        })
        
def ServerSummary(request):
    try:
        realDevice = []
        devices = DeviceCapibility.objects.filter(is_snmp=True)
        type_list = ['Server', 'Blade Chassis', 'vm']
        assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
        totalDevice = assetDevices.count()
        totalWatt = 0        

        totalBladeChasis = 0
        totalVMs = 0  
              
      
        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            totalWatt = totalWatt + assetDevice.deviceWatt  
            its_type = assetDevice.type_of_device
            if (its_type == "Blade Chassis"):
                totalBladeChasis = totalBladeChasis + 1
            if (its_type == "Server"):
                totalVMs = totalVMs + 1
            for device in devices:
                ipa = device.ip                
                if (fullIP == ipa):
                    realDevice.append({
                        "name" : device.name,
                        "ip" : fullIP
                    })
                    break
        totalInterfaceDevice = len(realDevice)      

        totalInbound = 0
        totalOutbound = 0
        interface = 0
        
        for d in realDevice:
            snmpd = SNMPDataCollection.objects.filter(ip = d["ip"]).order_by("-created_at")[:1]
            for interfaces in snmpd:

                if interfaces.interfaces == None or interfaces.interfaces == "" or len(interfaces.interfaces) <= 1:
                    continue

                inter = SNMPInterfaceDataCollection.objects.filter(id__in = list(map(int , interfaces.interfaces.split(","))) )
                for details in inter:
                    interface = interface + 1
                    totalInbound += details.inbound
                    totalOutbound += details.outbound

        data = {
            "totalDevice": totalDevice,
            "totalInterfaceDevice": totalInterfaceDevice,
            "inbound": totalInbound,
            "outbound": totalOutbound,
            "interface": interface,
            "totalBladeChasis" : totalBladeChasis,
            "totalVMs" : totalVMs,
            "totalWatt" : totalWatt
        }
        return JsonResponse({
            "data" : data,
            "error": False
        })
    except Exception as err:
        return JsonResponse({
            "data" : "Something went wrong, " + str(err),
            "error": True
        })



