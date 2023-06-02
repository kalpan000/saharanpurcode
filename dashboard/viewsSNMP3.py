
from django.http.response import JsonResponse
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1905 import EndOfMibView
from collections import defaultdict
import codecs
import binascii
import json
import time
from django.views.decorators.csrf import csrf_exempt
from pysnmp.hlapi import *

def defdict_to_dict(defdict, finaldict):
    for k, v in defdict.items():
        if isinstance(v, defaultdict):
            finaldict[k] = defdict_to_dict(v, {})
        else:
            finaldict[k] = v
    return finaldict

def hex2Str(str):
    str = str[2:]
    decode_hex = codecs.getdecoder("hex_codec")
    return decode_hex(str)

def to_text(value):
    if value is None:
        return []
    return [str(p) for p in value]

def decode_hex(hexstring):
    if len(hexstring) < 3:
        return hexstring
    if hexstring[:2] == "0x":
        return to_text(binascii.unhexlify(hexstring[2:]))
    return hexstring

def hex_to_str(hexStr):
    try:
        hex = hexStr[2:]
        bytes_object = bytes.fromhex(hex)
        ascii_string = bytes_object.decode("ASCII")
        return ascii_string
    except Exception as ex:
        return hexStr

class DefineOid(object):
    def __init__(self, dotprefix=False):
        if dotprefix:
            dp = "."
        else:
            dp = ""

        # From SNMPv2-MIB 
        self.sysDescr = dp + "1.3.6.1.2.1.1.1.0"
        self.sysObjectId = dp + "1.3.6.1.2.1.1.2.0"
        self.sysUpTime = dp + "1.3.6.1.2.1.1.3.0"
        self.sysContact = dp + "1.3.6.1.2.1.1.4.0"
        self.sysName = dp + "1.3.6.1.2.1.1.5.0"
        self.sysLocation = dp + "1.3.6.1.2.1.1.6.0"

        # FOR AP
        self.apCpu = dp + "1.3.6.1.4.1.14179.1.1.5.1.0"
        self.apJoint = dp + "1.3.6.1.4.1.9.9.618.1.8.4.0"
        self.apClient = dp + "1.3.6.1.4.1.9.9.618.1.8.12.0"

        # From IF-MIB
        self.ifIndex = dp + "1.3.6.1.2.1.2.2.1.1"
        self.ifDescr = dp + "1.3.6.1.2.1.2.2.1.2"
        self.ifMtu = dp + "1.3.6.1.2.1.2.2.1.4"
        self.ifSpeed = dp + "1.3.6.1.2.1.2.2.1.5"
        self.ifPhysAddress = dp + "1.3.6.1.2.1.2.2.1.6"
        self.ifAdminStatus = dp + "1.3.6.1.2.1.2.2.1.7"
        self.ifOperStatus = dp + "1.3.6.1.2.1.2.2.1.8"
        self.ifInOctets = dp + "1.3.6.1.2.1.2.2.1.10"
        self.ifOutOctets = dp + "1.3.6.1.2.1.2.2.1.16"
        self.ifInErr = dp + "1.3.6.1.2.1.2.2.1.14"
        self.ifOutErr = dp + "1.3.6.1.2.1.2.2.1.20"
        self.ifAlias = dp + "1.3.6.1.2.1.31.1.1.1.18"

        # From IP-MIB
        self.ipAdEntAddr = dp + "1.3.6.1.2.1.4.20.1.1"
        self.ipAdEntIfIndex = dp + "1.3.6.1.2.1.4.20.1.2"
        self.ipAdEntNetMask = dp + "1.3.6.1.2.1.4.20.1.3"

        # storage for servers
        self.hrSystemIndex = "1.3.6.1.2.1.25.2.3.1.1"
        self.storageType = "1.3.6.1.2.1.25.2.3.1.2"
        self.hrStorageDescr = "1.3.6.1.2.1.25.2.3.1.3"
        self.hrStorageAlloc = "1.3.6.1.2.1.25.2.3.1.4"
        self.StorageSize = "1.3.6.1.2.1.25.2.3.1.5"
        self.StorageUsed = "1.3.6.1.2.1.25.2.3.1.6"
        self.AllocationFailure = "1.3.6.1.2.1.25.2.3.1.7"



        self.profileNames = "1.3.6.1.4.1.9.9.512.1.1.1.1.3"
        self.ssid = "1.3.6.1.4.1.9.9.512.1.1.1.1.4"
        self.rowStatus = "1.3.6.1.4.1.9.9.512.1.1.1.1.2"
        self.wire = "1.3.6.1.4.1.9.9.512.1.1.1.1.7"
        
        # CPU CORE UTILIZATION FOR SERVERS
        



        # jhk
        self.bsnAPNumOfSlots = "1.3.6.1.4.1.14179.2.2.1.1.2.0.42.16"
        self.bsnAPName = "1.3.6.1.4.1.14179.2.2.1.1.3.0.42.16"
        self.bsnAPLocation = "1.3.6.1.4.1.14179.2.2.1.1.4.0.42.16"
        self.bsnAPMonitorOnlyMode = "1.3.6.1.4.1.14179.2.2.1.1.5.0.42.16"
        self.bsnAPOperationStatus = "1.3.6.1.4.1.14179.2.2.1.1.6.0.42.16"
        self.bsnAPSoftwareVersion = "1.3.6.1.4.1.14179.2.2.1.1.8.0.42.16"
        self.bsnAPBootVersion = "1.3.6.1.4.1.14179.2.2.1.1.9.0.42.16"
        self.bsnAPPrimaryMwarName = "1.3.6.1.4.1.14179.2.2.1.1.10.0.42.16"
        self.bsnAPReset = "1.3.6.1.4.1.14179.2.2.1.1.11.0.42.16"
        self.bsnAPStatsTimer = "1.3.6.1.4.1.14179.2.2.1.1.12.0.42.16"
        self.bsnAPPortNumber = "1.3.6.1.4.1.14179.2.2.1.1.13.0.42.16"
        self.bsnAPModel = "1.3.6.1.4.1.14179.2.2.1.1.16.0.42.16"
        self.bsnAPSerialNumber = "1.3.6.1.4.1.14179.2.2.1.1.17.0.42.16"
        self.bsnAPClearConfig = "1.3.6.1.4.1.14179.2.2.1.1.18.0.42.16"
        self.bsnApIpAddress = "1.3.6.1.4.1.14179.2.2.1.1.19.0.42.16"
        self.bsnAPMirrorMode = "1.3.6.1.4.1.14179.2.2.1.1.20.0.42.16"
        self.bsnAPRemoteModeSupport = "1.3.6.1.4.1.14179.2.2.1.1.21.0.42.16"
        self.bsnAPType = "1.3.6.1.4.1.14179.2.2.1.1.22.0.42.16"
        self.bsnAPSecondaryMwarName = "1.3.6.1.4.1.14179.2.2.1.1.23.0.42.16"
        self.bsnAPTertiaryMwarName = "1.3.6.1.4.1.14179.2.2.1.1.24.0.42.16"
        self.bsnAPIsStaticIP = "1.3.6.1.4.1.14179.2.2.1.1.25.0.42.16"
        self.bsnAPNetmask = "1.3.6.1.4.1.14179.2.2.1.1.26.0.42.16"
        self.bsnAPGateway = "1.3.6.1.4.1.14179.2.2.1.1.27.0.42.16"
        self.bsnAPStaticIPAddress = "1.3.6.1.4.1.14179.2.2.1.1.28.0.42.16"
        self.bsnAPBridgingSupport = "1.3.6.1.4.1.14179.2.2.1.1.29.0.42.16"
        self.bsnAPGroupVlanName = "1.3.6.1.4.1.14179.2.2.1.1.30.0.42.16"
        self.bsnAPIOSVersion = "1.3.6.1.4.1.14179.2.2.1.1.31.0.42.16"
        self.bsnAPCertificateType = "1.3.6.1.4.1.14179.2.2.1.1.32.0.42.16"
        self.bsnAPEthernetMacAddress = "1.3.6.1.4.1.14179.2.2.1.1.33.0.42.16"
        self.bsnAPAdminStatus = "1.3.6.1.4.1.14179.2.2.1.1.37.0.42.16"

        self.cpuUtilization = "1.3.6.1.2.1.25.3.3.1.2"

def lookup_adminstatus(int_adminstatus):
    adminstatus_options = {
        1: "up",
        2: "down",
        3: "testing"
    }
    if int_adminstatus in adminstatus_options:
        return adminstatus_options[int_adminstatus]
    return ""


def lookup_operstatus(int_operstatus):
    operstatus_options = {
        1: "up",
        2: "down",
        3: "testing",
        4: "unknown",
        5: "dormant",
        6: "notPresent",
        7: "lowerLayerDown"
    }
    if int_operstatus in operstatus_options:
        return operstatus_options[int_operstatus]
    return ""
def lookup_wired(int_operstatus):
    operstatus_options = {
        1: "wired",
        2: "wireless",
    }
    if int_operstatus in operstatus_options:
        return operstatus_options[int_operstatus]
    return ""

# Use p to prefix OIDs with a dot for polling
p = DefineOid(dotprefix=True)
# Use v without a prefix to use with return values
v = DefineOid(dotprefix=False)

def Tree():
    return defaultdict(Tree)

results = Tree()

@csrf_exempt
def getDetails(request = None , host = None , username = None, authkey=None, passkey=None):
    # if request != None:
    #     host = request.POST.get("host","localhost")
    #     snmp_cstr = request.POST.get("cstr","public")
    # else:
    #     snmp_cstr = communityStr
    auth = UsmUserData(username, authkey, passkey,privProtocol=usmAesCfb128Protocol)

    iterator = getCmd(
        SnmpEngine(),
        auth,
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(p.sysDescr)),
        ObjectType(ObjectIdentity(p.sysObjectId)),
        ObjectType(ObjectIdentity(p.sysUpTime)),
        ObjectType(ObjectIdentity(p.sysContact)),
        ObjectType(ObjectIdentity(p.sysName)),
        ObjectType(ObjectIdentity(p.sysLocation)),
        # ObjectType(ObjectIdentity(p.apCpu)),
        # ObjectType(ObjectIdentity(p.apJoint)),
        # ObjectType(ObjectIdentity(p.apClient)),
        lookupMib=False
        )
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    if errorIndication:
        if request == None:
            return False
        return JsonResponse({"error":True, "message":str(errorIndication)})

    for oid, val in varBinds:
        current_oid = oid.prettyPrint()
        current_val = val.prettyPrint()
        print(current_oid, current_val)
        if current_oid == p.sysDescr:
            results['sysdescr'] = hex_to_str(current_val)
            # print(current_val)
        elif current_oid == v.sysObjectId:
            results['sysobjectid'] = current_val
        elif current_oid == v.sysUpTime:
            results['sysuptime'] = current_val
        elif current_oid == v.sysContact:
            results['syscontact'] = current_val
        elif current_oid == v.sysName:
            results['sysname'] = current_val
        elif current_oid == v.sysLocation:
            results['syslocation'] = current_val
        # elif current_oid == v.apCpu:
        #     results['apCpu'] = current_val
        # elif current_oid == v.apJoint:
        #     results['apJoint'] = current_val
        # elif current_oid == v.apClient:
        #     results['apClient'] = current_val
    # print(defdict_to_dict(results, {}))
    iterator = nextCmd(
        SnmpEngine(),
        auth,
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(p.ifInOctets)),
        ObjectType(ObjectIdentity(p.ifOutOctets)),
        ObjectType(ObjectIdentity(p.ifInErr)),
        ObjectType(ObjectIdentity(p.ifOutErr)),
        ObjectType(ObjectIdentity(p.ifIndex)),
        ObjectType(ObjectIdentity(p.ifDescr)),
        ObjectType(ObjectIdentity(p.ifMtu)),
        ObjectType(ObjectIdentity(p.ifSpeed)),
        ObjectType(ObjectIdentity(p.ifPhysAddress)),
        ObjectType(ObjectIdentity(p.ifAdminStatus)),
        ObjectType(ObjectIdentity(p.ifOperStatus)),
        ObjectType(ObjectIdentity(p.ipAdEntAddr)),
        ObjectType(ObjectIdentity(p.ipAdEntIfIndex)),
        ObjectType(ObjectIdentity(p.ipAdEntNetMask)),
        ObjectType(ObjectIdentity(p.ifAlias)),
        lookupMib=False
        )


    interface_indexes = []

    all_ipv4_addresses = []
    ipv4_networks = Tree()
    
    for errorIndication, errorStatus, errorIndex, varTable in iterator:

        if errorIndication:
            if request == None:
                return False
            return JsonResponse({"error":True, "message":str(errorIndication)})

    

        # for varBinds in varTable:
        #     print(varBinds)
        
        for oid, val in varTable:
            print(oid, val)
            if isinstance(val, EndOfMibView):
                continue
            current_oid = oid.prettyPrint()
            current_val = val.prettyPrint()
            # print(current_oid, current_val)
            if v.ifIndex in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                # print(ifIndex,current_val)
                results['interfaces'][ifIndex]['ifindex'] = current_val
                interface_indexes.append(ifIndex)
            if v.ifDescr in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['name'] = hex_to_str(current_val)
            if v.ifMtu in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['mtu'] = current_val
            if v.ifSpeed in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['speed'] = current_val
            if v.ifPhysAddress in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['mac'] = decode_hex(current_val)
            if v.ifAdminStatus in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['adminstatus'] = lookup_adminstatus(int(current_val))
            if v.ifOperStatus in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['operstatus'] = lookup_operstatus(int(current_val))

            if v.ifInOctets in current_oid: 
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['inOctect'] = int(current_val)
            if v.ifOutOctets in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['outOctect'] = int(current_val)

            if v.ifInErr in current_oid: 
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['inErr'] = int(current_val)
            if v.ifOutErr in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['outErr'] = int(current_val)

            if v.ipAdEntAddr in current_oid:
                curIPList = current_oid.rsplit('.', 4)[-4:]
                curIP = ".".join(curIPList)
                ipv4_networks[curIP]['address'] = current_val
                all_ipv4_addresses.append(current_val)
            if v.ipAdEntIfIndex in current_oid:
                curIPList = current_oid.rsplit('.', 4)[-4:]
                curIP = ".".join(curIPList)
                ipv4_networks[curIP]['interface'] = current_val
            if v.ipAdEntNetMask in current_oid:
                curIPList = current_oid.rsplit('.', 4)[-4:]
                curIP = ".".join(curIPList)
                ipv4_networks[curIP]['netmask'] = current_val

            if v.ifAlias in current_oid:
                ifIndex = int(current_oid.rsplit('.', 1)[-1])
                results['interfaces'][ifIndex]['description'] = current_val


   
    interface_to_ipv4 = {}

    for ipv4_network in ipv4_networks:
        current_interface = ipv4_networks[ipv4_network]['interface']
        current_network = {
            'address': ipv4_networks[ipv4_network]['address'],
            'netmask': ipv4_networks[ipv4_network]['netmask']
        }
        if current_interface not in interface_to_ipv4:
            interface_to_ipv4[current_interface] = []
            interface_to_ipv4[current_interface].append(current_network)
        else:
            interface_to_ipv4[current_interface].append(current_network)

    for interface in interface_to_ipv4:
        results['interfaces'][int(interface)]['ipv4'] = interface_to_ipv4[interface]

    results['all_ipv4_addresses'] = all_ipv4_addresses

    data = defdict_to_dict(results, {})

    if request == None:
        return data

    fileError = False
    try:
        path = "media/snmprecording/"
        fileName = "-".join(host.split(".")) + "@" + str(int(time.time())) + ".json"
        file = open(path + fileName, "w")
        file.write(json.dumps(data , indent=4)) 
        file.close() 
    except Exception as ex:
        pass


    try:
        path = "media/snmprecording/"
        fileName = "-".join(host.split(".")) + "@" + str(int(time.time())) + ".txt"
        file = open(path + fileName, "w")
        file.write(results) 
        file.close() 
    except Exception as ex:
        pass
    print(data)
    # return JsonResponse({"data": data , "fileError" : fileError})
# getDetails(None, "192.168.1.19", "NETWORK123")
getDetails(None, "10.1.45.3","admin","Network@123","Network@123")