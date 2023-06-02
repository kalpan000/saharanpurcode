from email.policy import default
import json
import itertools
from dashboard.models import DeviceCapibility, SNMPDataCollection , SNMPInterfaceDataCollection, AddDevice, MyDevice,MyDeviceSNMPData, MyDeviceSNMPInterface
from django.http import JsonResponse
import datetime as DATETIME
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def makedevicefav(request):
    try:
        host = request.POST.get("host")
        device = DeviceCapibility.objects.get(ip = host)
        if device.is_fav:
            device.is_fav = False
            device.save()
            msg = "Removed from favourite"
        else:
            device.is_fav = True
            device.save()
            msg = "Marked as favourite"
        return JsonResponse({
            "data" : msg
        })
    except Exception as err:
        return JsonResponse({
            "data" : "Something went wrong: "+str(err)+"\nUnable to marked as favourite"
        })

def array2str(arr):
    if len(arr) == 0:
        return ""
    return ",".join(map(str, arr))

def SaveSNMPDataToDB(snmpData, ip):
    # print("Running SNMP Recording")
    # snmpData = json.loads(open("media/snmprecording/192-168-1-15@1639588122.json").read())
    print(ip)
    if not snmpData["sysdescr"]:
        snmpData["sysdescr"] = ""
    try:
        device, created = MyDevice.objects.update_or_create(ip = ip, defaults = {"name":str(snmpData["sysname"]),"description":str(snmpData["sysdescr"]),"contact":snmpData["syscontact"],"Location":snmpData["syslocation"]})   
        print(device, created)
    except Exception as err:
        print(str(err))
    # print("Device Created ", device)
    try:
        deviceData = MyDeviceSNMPData()
        sendDaTa = {}
        deviceData.device = device
        deviceData.uptime = snmpData["sysuptime"]
        # try:
        if "hrstorage" in snmpData:
            try:
                for storage in snmpData["hrstorage"]:
                    try:
                        temp = snmpData["hrstorage"][storage]
                        type = ""
                        if temp["hrtoragedescr"] != None:
                            if temp["hrtoragedescr"].lower() == "virtual memory":
                                type = "virtual"
                            elif temp["hrtoragedescr"].lower() == "physical memory":
                                type = "ram"
                            else :
                                type = "storage"
                        else :
                            type = "storage"

                        total = (float(temp["hrstoragesize"]) * float(temp["hrtoragealloc"])) / 1073741824 # total size
                        used = (float(temp["hrstorageused"]) * float(temp["hrtoragealloc"])) / 1073741824

                        if type == "storage":
                            deviceData.storage_total = total
                            sendDaTa["storage_used"] = used
                            deviceData.storage_used = used
                            deviceData.storage_available = total - used
                        elif type == "virtual":
                            deviceData.swap_total = total
                            deviceData.swap_used = used
                            sendDaTa["swap_used"] = used
                            deviceData.swap_available = total - used
                        else:
                            deviceData.ram_total = total
                            deviceData.ram_used = used
                            sendDaTa["ram_used"] = used
                            deviceData.ram_available = total - used
                    except Exception as err:
                        print("ERORR IN VIEWS_NETWORK LINE 81" , str(err))
            except Exception as err:
                print("ERORR IN VIEWS_NETWORK LINE 84" , str(err))
                
        # except Exception as err:
        #     print("ERORR IN VIEWS_NETWORK LINE 87" , str(err))


        if "cpuutil" in snmpData:
            d = {}
            d["cpu"] = []
            for cpu in snmpData["cpuutil"]:
                temp = snmpData["cpuutil"][cpu]
                if "cpuUtilization" in temp:
                    if temp["cpuUtilization"] == None:
                        temp["cpuUtilization"] = 0

                    d["cpu"].append(float(temp["cpuUtilization"]))
                    
            print("CPU" , array2str(d["cpu"]))
            deviceData.cpu = array2str(d["cpu"])
        else:
            deviceData.cpu = str(0)
        
        deviceData.save()
        print("Device Data Inserted ")
    except Exception as err:
        print(str(err))
    
    
    if "interfaces" in snmpData:
        try:
            for interface in snmpData["interfaces"]:          
                temp = snmpData["interfaces"][interface]
                # print(temp)
                for key in temp:
                    if temp[key] == None or temp[key] == False:
                        temp[key] = 0

                # print("ALL KEYS ARE" , temp.keys())
                temp["name"] = str(temp["name"]).replace("\x00", "\uFFFD")
                temp["speed"] = (float(temp["speed"]) / 1048576)  
                deviceInterface = MyDeviceSNMPInterface()   
                deviceInterface.deviceData = deviceData
                # deviceInterface.name = temp["name"] if temp["name"] else "Null"
                deviceInterface.speed = (float(temp["speed"]) * 0.125 / (1024 * 1024)) if temp["speed"] else 0
                deviceInterface.ifindex = temp["ifindex"]
                deviceInterface.inOctect = (float(temp["inOctect"]) * 0.125 / (1024 * 1024)) if temp["inOctect"] else 0
                deviceInterface.outOctect = (float(temp["outOctect"]) * 0.125 / (1024 * 1024)) if temp["outOctect"] else 0
                deviceInterface.name = temp["name"]

                if "inErr" in temp:
                    deviceInterface.inErr = temp["inErr"] if temp["inErr"] else 0
                else:
                    deviceInterface.inErr = 0
                    
                if "outErr" in temp:
                    deviceInterface.outErr = temp["outErr"] if temp["outErr"] else 0
                else:
                    deviceInterface.outErr = 0

                deviceInterface.mtu = (float(temp["mtu"])* 0.125 / (1024 * 1024)) if temp["mtu"] else 0
                # deviceInterface.speed = (float(temp["speed"]) * 0.125 / (1024 * 1024))
                deviceInterface.mac = ":".join(temp["mac"])
                deviceInterface.adminstatus = temp["adminstatus"]
                deviceInterface.operstatus = temp["operstatus"]
                deviceInterface.description = ""
                
                # print(ip)
                # print("Yaha tak to chala")
                deviceInterface.save()
                print("Device Interfaces Added ")
                # print("Save nhi huya")

        except Exception as err:
            print("VIEWS_NETWORK LINE 125" , str(err))
    else:
        deviceInterface = MyDeviceSNMPInterface()   
        deviceInterface.deviceData = deviceData
        deviceInterface.save()
    return sendDaTa

    

def fetchDataFromSNMP():
    pass
def insertData(snmpData , ip):
    # print("Running SNMP Recording")
    # snmpData = json.loads(open("media/snmprecording/192-168-1-15@1639588122.json").read())
    
    d = {}

    d["cpu"] = []
    d["ram"] = [0 , 0 , 0] # total , used , available 
    d["virtual"] = [0 , 0 , 0] # total , used , available 
    d["storage"] = [0 , 0 , 0] # total , used , available 
    d["interfaces"] = ""

    if "cpuutil" in snmpData:
        for cpu in snmpData["cpuutil"]:
            temp = snmpData["cpuutil"][cpu]
            d["cpu"].append(float(temp["cpuUtilization"]))

    if "hrstorage" in snmpData:
        try:
            for storage in snmpData["hrstorage"]:
                try:
                    temp = snmpData["hrstorage"][storage]
                    type = ""
                    if temp["hrtoragedescr"].lower() == "virtual memory":
                        type = "virtual"
                    elif temp["hrtoragedescr"].lower() == "physical memory":
                        type = "ram"
                    else :
                        type = "storage"
                    
                    total = (float(temp["hrstoragesize"]) * float(temp["hrtoragealloc"])) / 1073741824 # total size
                    used = (float(temp["hrstorageused"]) * float(temp["hrtoragealloc"])) / 1073741824 # total used
                    d[type][0] += total
                    d[type][1] += used
                    d[type][2] += (total - used)
                except Exception as err:
                    pass
        except Exception as err:
            pass

    if "interfaces" in snmpData:
        for interface in snmpData["interfaces"]:
            temp = snmpData["interfaces"][interface]
            temp["name"] = temp["name"].replace("\x00", "\uFFFD")
            temp["speed"] = (float(temp["speed"]) / 1048576)
            obj = SNMPInterfaceDataCollection.objects.create(ip = ip, name = temp["name"], description =  temp["description"], 
                mac = ":".join(temp["mac"]) , admin = temp["adminstatus"], port = temp["operstatus"], inbound = (temp["inOctect"] / 1000000),
                outbound = (temp["outOctect"]  / 1000000) , mtu = int(temp["mtu"]) , speed = temp["speed"] , errorin = 0, errorout = 0)

            # print("Inbound" , temp['inOctect'] , "Outbound" , temp["outOctect"] , "Speed" , temp["speed"])
            # print("Formatted Inbound" , (temp["inOctect"] / 1000000) , "Outbound" ,  (temp["outOctect"]  / 1000000) , "Speed" , (temp["speed"] / 1000000))

            d["interfaces"] += str(obj.id) + ","
    
        d["interfaces"] = d["interfaces"][:-1]
    
    tempName = snmpData["sysname"].replace("\x00", "\uFFFD")

    d["cpu"] = array2str(d["cpu"])
    d["ram"] = array2str(d["ram"])
    d["virtual"] = array2str(d["virtual"])
    d["storage"] = array2str(d["storage"])

    obj2 = SNMPDataCollection.objects.create(ip = ip, name = tempName, description = snmpData["sysdescr"] , 
        contact = snmpData["syscontact"] , location = snmpData["syslocation"] , oid = snmpData["sysobjectid"] , 
        uptime = int(int(snmpData["sysuptime"]) / 100) , cpu = d["cpu"] , ram = d["ram"] , virtual = d["virtual"], 
        storage = d["storage"] , interfaces = d["interfaces"])

    return d
    
def str2list(str , type = int):
    if str == None or str == "" or len(str) == 0:
        return []
    return list(map(type , str.split(",")))


def listsum(l1 , l2):
    leng1 = len(l1)
    leng2 = len(l2)

    if leng1 == 0:
        return l2

    if leng1 != leng2:
        return [0] * max(leng1 , leng2)
        
    output = []
    for i in range(0 , leng1):
        output.append(l1[i] + l2[i])

    return output    

# converts [1,2,3,4,5,6] to [[1] , [2] , [3] , [4]]


def listTo2DList(arr , outputArr , runOnce):

    if runOnce:
        outputArr = [ [] for i in arr ]

    index = 0
    for i in arr:
        outputArr[index].append(i)
        index += 1

    return outputArr


# # for 1 day data showing minutes wise
def date_min(timestamp):
    return timestamp.strftime("%x %H:%M") # make groups based on a date and minutes 

# for 1 month data showing hour wise 
def date_hour(timestamp):
    return timestamp.strftime("%x %H") # make groups based on dates and hours 

# for 1+ months showing day wise
def date_days(timestamp):
    return timestamp.strftime("%x") # make groups based on a date


def getSingleDeviceRealtime(ip , totalRecordstoReturn):
    partIP = ip.split(".")
    devices = SNMPDataCollection.objects.filter(ip = ip).order_by("-created_at")[:totalRecordstoReturn]
    AssetDevices = AddDevice.objects.filter(IP_Address_col1=partIP[0],IP_Address_col2=partIP[1],IP_Address_col3=partIP[2],IP_Address_col4=partIP[3])
 
    #print("Device count" , devices.count())
    if devices.count() == 0:
        print("No Device found with the ip " + ip)
        return {"error" : True , "message" : "No device found"}

    serializedAssetDevice = serializers.serialize('json', AssetDevices)
    serializedDevice = serializers.serialize('json', devices)

    firstDevice = devices.first()
    if firstDevice.interfaces == "" or len(firstDevice.interfaces) <= 1:
        serializedInterfaces = {}
                    
    else:
        interfaces = SNMPInterfaceDataCollection.objects.filter(id__in = list(map(int , devices.first().interfaces.split(","))) )
        serializedInterfaces = serializers.serialize('json', interfaces)

    ramOutput = []
    virtualOutput = []
    storageOutput = []
    cpuOutput = []
    ramLineOutput = []


    arrayConvertRunOnce = True
    loopRunOnce = True


    for device in devices:

        try:
            cpu = str2list(device.cpu , float)
            ram = str2list(device.ram , float)

            cpuOutput = listTo2DList(cpu , cpuOutput , arrayConvertRunOnce)
            ramLineOutput = listTo2DList(ram , ramLineOutput , arrayConvertRunOnce)
            arrayConvertRunOnce = False

        except Exception as ex:
            print("CPU is empty" , ex)

        if loopRunOnce:
            loopRunOnce = False
            try:
                ram = str2list(device.ram , float)
                ramOutput = listTo2DList(ram , ramOutput , True)
            except Exception as ex:
                print("ram is empty" , ex)

            try:
                virtual = str2list(device.virtual , float)
                virtualOutput = listTo2DList(virtual , virtualOutput , True)
            except Exception as ex:
                print("virtual is empty" , ex)

            try:
                storage = str2list(device.storage , float)
                storageOutput = listTo2DList(storage , storageOutput , True)
            except Exception as ex:
                print("storage is empty" , ex)

    
    #print("cpu" , cpuOutput ,  "ram" , ramOutput[1:] ,  "virtual" , virtualOutput[1:] ,  "storage" , storageOutput[1:])
    return cpuOutput , ramOutput[1:] , virtualOutput[1:] , storageOutput[1:] , ramLineOutput , serializedDevice , serializedInterfaces, serializedAssetDevice
    #return interfaces



def getData(ip , totalRecordstoReturn , duration = "Live" , start_date = None, end_date = None , aggregate = sum , type = "" ):

    if duration == "Live" :
        return getSingleDeviceRealtime(ip , totalRecordstoReturn)

        # print("Duration and Type" , duration , type)
    #devices = SNMPDataCollection.objects.filter(ip = ip , created_at__range = (start_date , end_date)).order_by("-created_at")
    devices = SNMPDataCollection.objects.filter(ip = ip).order_by("-created_at")
    if duration == "1D":
        groups = itertools.groupby(devices , lambda device : date_min(device.created_at))
    if duration == "1W":
        groups = itertools.groupby(devices , lambda device : date_hour(device.created_at))
    if duration == "1M":
        groups = itertools.groupby(devices , lambda device : date_hour(device.created_at))
    if duration == "year" or duration == "6M" or duration == "12M":
        groups = itertools.groupby(devices , lambda device : date_days(device.created_at))

    output = []
    finalOutput = []
    ramOutput = []
    virtualOutput = []
    storageOutput = []
    cpuOutput = []
    ramLineOutput = []

    for group , matches in groups:

        cpuSum = []
        ramSum = []

        for match in matches:

            try:

                if type == "cpu":
                    cpu = str2list(match.cpu , float)
                    cpuSum = listsum(cpu , cpuSum)
                elif type == "ramline":
                    ram = str2list(match.ram , float)
                    ramSum = listsum(ram , ramSum)

            except Exception as ex:
                print("CPU  / Ram is empty" , ex)

        if type == "cpu" :
            cpuOutput.append(cpuSum)
        elif type == "ramline" :
            ramLineOutput.append(ramSum)
    
    finaloutput = []

    
    indexI = 0
    
    if type == "cpu":
        for i in cpuOutput[0]:
            finaloutput.append([ j[indexI] for j in cpuOutput ])
            indexI = indexI + 1

    elif type == "ramline" :
        for i in ramLineOutput[0]:
            finaloutput.append([ j[indexI] for j in ramLineOutput ])
            indexI = indexI + 1
    
    return finaloutput




def frontendFunc(request , firstRun = 1 , duration = "Live" , ip = "" , type = "" , startDate = None, endDate = None, returnjson = True):
    
    totalRecordsToReturn = (60 * 5) / 5 # 60 seconds * 10 aka 10 minutes divided by retrival time 
    mode = "multi"
    if firstRun == 0:
        totalRecordsToReturn = 1
        mode = "single"

    if ip != "": 
        day = 1
        if duration == "Live":
            day = 0
        elif duration == "1D":
            day = 1
        elif duration == "1W":
            day = 7
        elif duration == "1M":
            day = 30
        elif duration == "6M":
            day = 180
        elif day == "12M":
            day = 365
        
        if startDate == None or endDate == None:
            startDate = DATETIME.datetime.today() - DATETIME.timedelta(days=day)
            endDate = DATETIME.datetime.today()
        
        if type == "ramline" or type == "cpu":
            data = getData(ip , totalRecordsToReturn , duration , type=type , start_date=startDate , end_date=endDate)
            if returnjson:
                return JsonResponse({ "error" : False , "data" : data  , "mode" : mode})
            else:
                return { "error" : False , "data" : data  , "mode" : mode}

        cpu , ram , virtual , storage , ramLineOutput, serializedDevice , interfaces, serializedAssetDevice = getData(ip , totalRecordsToReturn , duration , start_date=startDate , end_date=endDate)
            
        cpuLabels = []
        indexI = 0
        for i in cpu:
            cpuLabels.append("Core " + str(indexI))
            indexI += 1
        obj = {"error" : False , "mode" : mode , "data" : {
                "data" : cpu,
                "assetDevice" : serializedAssetDevice,
                "interfaces" : interfaces,
                "sysinfo" : serializedDevice,
                "cpu" : {
                    "data" : cpu,
                    "labels" : cpuLabels
                },
                "ramline" : {
                    "data" : ramLineOutput,
                    "labels" : ["Total" , "Used" , "Available"],
                    "bgcolor" : ["#1a75ff", "#ff4d4d", "#1aff1a"]
                },
                "ram" : {
                    "data" : ram,
                    "labels" : ["Used" , "Available"],
                    "bgcolor" : ["#ff4d4d", "#1aff1a"]
                },
                "virtual" : {
                    "data" : virtual,
                    "labels" : ["Used" , "Available"],
                    "bgcolor" : ["#ff4d4d", "#1aff1a"]
                },
                "storage" : {
                    "data" : storage,
                    "labels" : ["Used" , "Available"],
                    "bgcolor" : ["#ff4d4d", "#1aff1a"]
                }
            }}
        if returnjson:
            return JsonResponse(obj)
        else:
            return obj
    else:
        return JsonResponse({"error" : True , "mode" : mode , "message" : "IP CANNOT BE EMPTY"})
    