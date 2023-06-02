from pysnmp import hlapi
from django.contrib.auth.decorators import login_required
from .models import DeviceCapibility, AddDevice
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required

# https://www.oidview.com/ for oid
def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types(oids)
    )
    print(handler)
    return fetch(handler, 60)[0]


def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
    return object_types


def fetch(handler, count):
    result = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                    result.append(items)
            else:
                raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
        except StopIteration:
            break
    print("**** RESULT ****")
    print(result)
    print("***** END RESULT ****")
    return result

def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value

# for SNMPv2


def get_bulk(target, oids, credentials, count, start_from=0, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):

    handler = hlapi.bulkCmd(engine,credentials,hlapi.UdpTransportTarget((target, port)),context,start_from, count, *construct_object_types(oids))
    return fetch(handler, count)

def runthis(host , communityString , oid , count  = 40 ,  port = 161):

    #l = []

    # for i in range(0 , 10):
    #     for j in range(0,30):
    #         l.append("1.3.6.1.2.1.4.34." + str(i) + "."  + str(j))


    res = get_bulk(host , oid , hlapi.CommunityData(communityString) , count)
    return res


# always use oid - 1 (minus)
d = {
    "ports" : "1.3.6.1.2.1.2.2.1.2",
    "portState" : "1.3.6.1.2.1.2.2.1.9",
    "runtime" : "1.3.6.1.2.1.1.2.0",
    "name" : "1.3.6.1.2.1.1.0.0",
    "adminDown" : "1.3.6.1.2.1.2.2.1.7",
    "packetsInbound" : "1.3.6.1.2.1.31.1.1.1.6",
    "packetsOutbound" : "1.3.6.1.2.1.31.1.1.1.10",
    "macaddress" : "1.3.6.1.2.1.2.2.1.6"
}


def convertDictToList(d):

    for key in d : 
        return d[key]

    return None

def getPortStatus(host , communityString , count = 40):
    try:
        ports = runthis(host , communityString , [d["ports"]] , count)    
        states = runthis(host , communityString , [d["portState"]] , count) 
        adminDown = runthis(host , communityString , [d["adminDown"]] , count)
        uptime = runthis(host, communityString , [d["runtime"]] , 1)
        inbound = runthis(host , communityString , [d["packetsInbound"]] , count)
        outbound = runthis(host , communityString , [d["packetsOutbound"]] , count)
        mac = runthis(host , communityString , [d["macaddress"]] , count)

        output = []
        inboundOutput = []
        outboundOutput = []
        macOutput = []

        counter = 0
        portCount = 0
        addToOutput = False
        for port in ports :
            for key in port :
                if( not isinstance( port[key] , int) and port[key][:8] == "Ethernet"):
                    portCount += 1

        states = states[:portCount]
        adminDown = adminDown[:portCount]
        inbound = inbound[:portCount]
        outbound = outbound[:portCount]
        mac = mac[:portCount]

        

        for i in range(0 , len(adminDown)):

            inboundOutput.append( str(int(convertDictToList( inbound[i]) / 1000)) + "MB" )
            outboundOutput.append( str(int(convertDictToList(outbound[i]) / 1000)) + "MB" )
            macOutput.append( str(convertDictToList(mac[i])) )
            
            

            for key in states[i]:
                if(states[i][key] == 0):
                    for key in adminDown[i]:
                        if(adminDown[i][key] == 2):
                            output.append(-1)
                        else:
                            output.append(0)
                else :
                    output.append(1)

        return {"error" : False , "data" : {"output" : output, "states" : states , "portCount" : portCount , "uptime" : convertDictToList(uptime[0]) , "inbound" : inboundOutput , "outbound" : outboundOutput , "macaddress" : macOutput } }
    

    except RuntimeError as err:
        return {"error" : True , "message" : "Device not available / Incorrect Credentials"}



@login_required(redirect_field_name=None)
@permission_required("dashboard.view_networksummary" , "/noperm/")
def network(request):

    # data = functionToGETSNMPDATA()
    #data2 = getPortStatus("192.168.2.10" , "NETWORK@123" , 40)
    dc = DeviceCapibility.objects.filter(is_snmp = True)
    devices = list(dc)
    type_list = ['Network', 'Load Balancer','utm','firewall','wlc']
    # # type_list2 = ['Server', 'Blade Chassis', 'vm']
    selectOptionDevices = []
    assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
    # assetDevices = AddDevice.objects.all()
    for device in dc:
        ipa = device.ip
        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            if (ipa == fullIP):
                selectOptionDevices.append({
                    "name" : device.name,
                    "ip" : ipa,
                    "cstr": device.commString
                })
                break
    # print(selectOptionDevices)
    
    # print(devices)
    data = {
        #"networkGraph" : data2,
        "snmpdevices" : selectOptionDevices,
        #"totalDevices" : totalDevices
    }
    return render(request, 'dashboard/networkGraph.html' , data)

@login_required(redirect_field_name=None)
@permission_required("dashboard.view_serversummary" , "/noperm/")
def server(request):

    dc = DeviceCapibility.objects.filter(is_snmp=True)
    type_list = ['Server', 'Blade Chassis', 'vm']
    selectOptionDevices = []
    assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
    for device in dc:
        ipa = device.ip
        # user = device.user
        # pwd = device.pwd
        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            if (ipa == fullIP):
                selectOptionDevices.append({
                    "name" : device.name,
                    "ip" : ipa,
                    "cstr": device.commString
                })
                break
    data = {
        "snmpdevices" : selectOptionDevices,
    }
    return render(request, 'dashboard/serverGraph.html' , data)
@login_required(redirect_field_name=None)
@permission_required("dashboard.view_storagesummary" , "/noperm/")
def storage(request):

    dc = DeviceCapibility.objects.filter(is_snmp=True)
    type_list = ['Storage']
    selectOptionDevices = []
    assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
    for device in dc:
        ipa = device.ip
        # user = device.user
        # pwd = device.pwd
        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            if (ipa == fullIP):
                selectOptionDevices.append({
                    "name" : device.name,
                    "ip" : ipa,
                    "cstr": device.commString
                })
                break
    data = {
        "snmpdevices" : selectOptionDevices,
    }


    return render(request, 'dashboard/storageGraph.html' , data)
@login_required(redirect_field_name=None)
@permission_required("dashboard.view_databasesummary" , "/noperm/")
def database(request): #APM

    # data = functionToGETSNMPDATA()
    #data2 = getPortStatus("192.168.2.10" , "NETWORK@123" , 40)
    dc = DeviceCapibility.objects.filter(is_snmp = True)
    devices = list(dc)
    type_list = ['Server', 'Blade Chassis', 'vm']
    # type_list = ['Server', 'Blade Chassis', 'vm']
    selectOptionDevices = []
    # assetDevices = AddDevice.objects.all()
    assetDevices = AddDevice.objects.filter(type_of_device__in = type_list)
    for device in dc:
        ipa = device.ip
        for assetDevice in assetDevices:
            fullIP = str(assetDevice.IP_Address_col1) + "." + str(assetDevice.IP_Address_col2) + "." + str(assetDevice.IP_Address_col3) + "." + str(assetDevice.IP_Address_col4)
            if (ipa == fullIP):
                selectOptionDevices.append({
                    "name" : device.name,
                    "ip" : ipa
                })
                break
    # print(selectOptionDevices)
    
    # print(devices)
    data = {
        #"networkGraph" : data2,
        "snmpdevices" : selectOptionDevices,
        #"totalDevices" : totalDevices
    }
    return render(request, 'dashboard/dbmsGraph.html' , data)


def listSum(l1):
    sum = 0
    for i in l1:
        sum = sum + int( i[:-2] )
    
    return sum

def getNetworkSummary(request):
    totalDevices = len(DeviceCapibility.objects.all())
    devices = DeviceCapibility.objects.filter(is_snmp = True).values('id' , 'is_snmp' , 'name' , 'ip' , 'commString')

    totalOutbound = 0
    totalInbound = 0

    for device in devices:

        if len(device["ip"]) == 0 or len(device["commString"]) == 0:
            continue

        data = getPortStatus(device["ip"] , device["commString"] , 40)

        if(data["error"]):
            continue
            
        data = data["data"]

        totalOutbound = totalOutbound + listSum(data["outbound"])
        totalInbound = totalInbound + listSum(data["inbound"])

    
    return JsonResponse( {"error" : False , "totalDevices" : totalDevices , "outbound" : totalOutbound , "inbound" : totalInbound} )


def getNetworkDeviceData(request):
    ID = request.GET["id"]
    if(id == None):
        return JsonResponse({"error" : True , "message" : "Device ID missing."})

    try:
        record = DeviceCapibility.objects.get(id = ID)
    except Exception as err :
        return JsonResponse({"error" : True , "message" : "No device found with the ID " + ID})
    
    if not record.is_snmp :
        return JsonResponse({"error" : True , "message" : "Device does not support SNMP"})
    
    print(record.ip)
    print(record.commString)

    if(record.ip == None or record.commString == None or len(record.ip) == 0 or len(record.commString) == 0):
        return JsonResponse({"error" : True , "message" : "Host / Community String is empty"})
        
    data2 = getPortStatus(record.ip , record.commString , 40)
    #data2 = getPortStatus("192.168.2.10" , "NETWORK@123" , 40)
    return JsonResponse(data2)

