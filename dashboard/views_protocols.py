from ncclient import manager, xml_
import requests
import json
import time
from django.http import JsonResponse
from xml.etree import ElementTree 
from django.views.decorators.csrf import csrf_exempt
import xmltodict
#from viewsSNMP import getDetails as getSNMPDetails


DEFAULT_PORTS = {
    "netconf" : ["22","831","832","833","834","835"],
    "restconf" : ["443"],
    "snmp" :["161","162"]
}

# Supported device handlers
# When instantiating a connection to a known type of NETCONF server:

# Juniper: device_params={'name':'junos'}
# Cisco:
# CSR: device_params={'name':'csr'}
# Nexus: device_params={'name':'nexus'}
# IOS XR: device_params={'name':'iosxr'}
# IOS XE: device_params={'name':'iosxe'}
# Huawei:
# device_params={'name':'huawei'}
# device_params={'name':'huaweiyang'}
# Nokia SR OS: device_params={'name':'sros'}
# H3C: device_params={'name':'h3c'}
# HP Comware: device_params={'name':'hpcomware'}
# Server or anything not in above: device_params={'name':'default'}

# with manager.connect(host=host, port=830, username=user, hostkey_verify=False, device_params={'name':'junos'}) as m:


class Netconf():
    def __init__(self, host , username , password , port):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        

    def connect(self):
        try:
            with manager.connect(host=self.host , port=self.port, username=self.username, password=self.password ,  hostkey_verify=False) as m:
                
                #config = m.get_config(source='running').data_xml
                config = m.get_config(source='running')
                cap = m.get_capabilities
                print("---------------------- Printing config")
                #print(config)
                print("---------------------- Printing capabilities")
                #print(cap)

                #return (200, json.dumps(xmltodict.parse(config))) , str(cap) , False
                return str(config) , str(cap) , False
        except Exception as ex:
            print(str(ex))
            return str(ex) , str(ex) , True
            
# for restconf read this https://blog.wimwauters.com/networkprogrammability/2020-04-04_restconf_python/
# url syntax url = f"https://{device['ip']}:{device['port']}/restconf/data/{module}"
class Restconf():
    def __init__(self, host , username , password , port):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.headers = {
            "Accept" : "application/yang-data+json", 
            "Content-Type" : "application/yang-data+json", 
        }    
        self.module = "ietf-interfaces:interfaces-state"
        self.url = f"https://{host}:{port}/restconf/data/{self.module}"
    
    def connect(self):
        response = requests.get(self.url, headers=self.headers, auth=(self.username, self.password), verify=False)
        print("---------------------- Printing restconf response")
        content = response.content.decode("utf-8")
        print(content)
        return content
        # interfaces = response['ietf-interfaces:interfaces']['interface']
        # for interface in interfaces:
        #     if bool(interface['ietf-ip:ipv4']): #check if IP address is available
        #         print(f"{interface['name']} -- {interface['description']} -- {interface['ietf-ip:ipv4']['address'][0]['ip']}")

            
# class SNMP():
#     def __init__(self, host , communityStr , username = None , password = None , port = None):
#         self.host = host
#         self.username = username
#         self.password = password
#         self.communityStr = communityStr
#         self.port = port
    
#     def connect(self):
#         details = getSNMPDetails(None , self.host , self.communityStr)
#         print("---------------------- Printing snmp response")
#         print(details)

@csrf_exempt
def restconfajax(request):
    
    host = request.POST.get("host")
    username = request.POST.get("username")
    password = request.POST.get("password")
    port = request.POST.get("port")

    obj1 = Restconf(host , username , password , port)
    response = obj1.connect()
    #response = json.dumps(response , indent=4)
    output1 = saveFile(host , response , "json" , "response")

    return JsonResponse({"data": response  , "fileError" : output1 })



@csrf_exempt
def netconfajax(request):
    print("running netconf")
    host = request.POST.get("host")
    username = request.POST.get("username")
    password = request.POST.get("password")
    port = request.POST.get("port")

    obj1 = Netconf(host , username , password , port)
    # might need to convert config and cap to string
    config , cap , error = obj1.connect()

    if error:    
        return JsonResponse({"erorr" : True , "message" : config})

    output1 = saveFile(host , config , "xml" , "config")
    output2 = saveFile(host , cap , "txt" , "cap")

    return JsonResponse({"data": { "config" : config , "cap" : cap } , "fileError" : {"config" : output1 , "cap" : output2}})


def saveFile(host , data , fileType = "xml" , type = "config"):
       
    fileError = False
    try:
        path = "media/netconfrecording/"
        fileName = "-".join(host.split(".")) + "@" + type + "@" + str(int(time.time())) + "." + fileType
        file = open(path + fileName, "w")

        file.write(data) 
        
        file.close() 
    except Exception as ex:
        fileError = str(ex)
        print(ex)

    return fileError
