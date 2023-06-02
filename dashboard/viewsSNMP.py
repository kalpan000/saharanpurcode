import sys
from django.http.response import JsonResponse
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1905 import EndOfMibView
from collections import defaultdict
import codecs
import binascii
import json
import time
from django.views.decorators.csrf import csrf_exempt

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
def getDetails(request = None , host = None , communityStr = None):
    if request != None:
        host = request.POST.get("host","localhost")
        snmp_cstr = request.POST.get("cstr","public")
    else:
        snmp_cstr = communityStr
    # print(host, snmp_cstr)
    auth = cmdgen.CommunityData(snmp_cstr)
    cmdGen = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        auth,
        cmdgen.UdpTransportTarget((host, 161)),
        cmdgen.MibVariable(p.sysDescr,),
        cmdgen.MibVariable(p.sysObjectId,),
        cmdgen.MibVariable(p.sysUpTime,),
        cmdgen.MibVariable(p.sysContact,),
        cmdgen.MibVariable(p.sysName,),
        cmdgen.MibVariable(p.sysLocation,),

        cmdgen.MibVariable(p.apCpu,),
        cmdgen.MibVariable(p.apJoint,),
        cmdgen.MibVariable(p.apClient,),
        lookupMib=False
    )
    if errorIndication:
        if request == None:
            return False
        return JsonResponse({"error":True, "message":str(errorIndication)})

    for oid, val in varBinds:
        current_oid = oid.prettyPrint()
        current_val = val.prettyPrint()
        if current_oid == v.sysDescr:
            results['sysdescr'] = hex_to_str(current_val)
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
        elif current_oid == v.apCpu:
            results['apCpu'] = current_val
        elif current_oid == v.apJoint:
            results['apJoint'] = current_val
        elif current_oid == v.apClient:
            results['apClient'] = current_val
        # print(current_oid, current_val)
    errorIndication, errorStatus, errorIndex, varCpuUtil = cmdGen.nextCmd(
    auth,
    cmdgen.UdpTransportTarget((host, 161)),
    cmdgen.MibVariable(p.cpuUtilization,),
    lookupMib=False
    )

    if errorIndication:
        sys.exit()

    for varBinds in varCpuUtil:
        for oid, val in varBinds:
            if isinstance(val, EndOfMibView):
                continue
            current_oid = oid.prettyPrint()
            current_val = val.prettyPrint()
            # print(current_oid, current_val)
            if v.cpuUtilization in current_oid:
                cpuUtilization = int(current_oid.rsplit('.', 1)[-1])
                results['cpuutil'][cpuUtilization]['cpuUtilization'] = current_val
    try:
        errorIndication, errorStatus, errorIndex, varhrStorage = cmdGen.nextCmd(
            auth,
            cmdgen.UdpTransportTarget((host, 161)),
            cmdgen.MibVariable(p.hrSystemIndex,),
            cmdgen.MibVariable(p.storageType,),
            cmdgen.MibVariable(p.hrStorageDescr,),
            cmdgen.MibVariable(p.hrStorageAlloc,),
            cmdgen.MibVariable(p.StorageSize,),
            cmdgen.MibVariable(p.StorageUsed,),
            cmdgen.MibVariable(p.AllocationFailure,),
            lookupMib=False
        )

        if errorIndication:
            print(str(errorIndication))
        
        for varBinds in varhrStorage:
            for oid, val in varBinds:
                if isinstance(val, EndOfMibView):
                    continue
                current_oid = oid.prettyPrint()
                current_val = val.prettyPrint()
                # print(current_oid, current_val)
                if v.hrSystemIndex in current_oid:
                    hrSystemIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['hrstorage'][hrSystemIndex]['hrsystemindex'] = hrSystemIndex
                if v.storageType in current_oid:
                    hrSystemIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['hrstorage'][hrSystemIndex]['hrstoragetype'] = current_val
                if v.hrStorageDescr in current_oid:
                    hrSystemIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['hrstorage'][hrSystemIndex]['hrtoragedescr'] = current_val
                if v.hrStorageAlloc in current_oid:
                    hrSystemIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['hrstorage'][hrSystemIndex]['hrtoragealloc'] = current_val
                if v.StorageSize in current_oid:
                    hrSystemIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['hrstorage'][hrSystemIndex]['hrstoragesize'] = current_val
                if v.StorageUsed in current_oid:
                    hrSystemIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['hrstorage'][hrSystemIndex]['hrstorageused'] = current_val
                if v.AllocationFailure in current_oid:
                    hrSystemIndex = int(current_oid.rsplit('.', 1)[-1])
                    results['hrstorage'][hrSystemIndex]['hrallocfail'] = current_val
    except Exception as err:
        results['hrstorage'][0]['hrsystemindex'] = 0
        results['hrstorage'][0]['hrstoragetype'] = 0
        results['hrstorage'][0]['hrtoragedescr'] = 0
        results['hrstorage'][0]['hrtoragealloc'] = 0
        results['hrstorage'][0]['hrstoragesize'] = 0
        results['hrstorage'][0]['hrstorageused'] = 0
        results['hrstorage'][0]['hrallocfail'] = 0



    errorIndication, errorStatus, errorIndex, varTable = cmdGen.nextCmd(
        auth,
        cmdgen.UdpTransportTarget((host, 161)),
        cmdgen.MibVariable(p.ifInOctets,),
        cmdgen.MibVariable(p.ifOutOctets,),
        cmdgen.MibVariable(p.ifInErr,),
        cmdgen.MibVariable(p.ifOutErr,),
        cmdgen.MibVariable(p.ifIndex,),
        cmdgen.MibVariable(p.ifDescr,),
        cmdgen.MibVariable(p.ifMtu,),
        cmdgen.MibVariable(p.ifSpeed,),
        cmdgen.MibVariable(p.ifPhysAddress,),
        cmdgen.MibVariable(p.ifAdminStatus,),
        cmdgen.MibVariable(p.ifOperStatus,),
        cmdgen.MibVariable(p.ipAdEntAddr,),
        cmdgen.MibVariable(p.ipAdEntIfIndex,),
        cmdgen.MibVariable(p.ipAdEntNetMask,),
        cmdgen.MibVariable(p.ifAlias,),
        lookupMib=False
    )

    if errorIndication:
        if request == None:
            return False
        return JsonResponse({"error":True, "message":str(errorIndication)})

    interface_indexes = []

    all_ipv4_addresses = []
    ipv4_networks = Tree()

    for varBinds in varTable:
        for oid, val in varBinds:
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


    errorIndication, errorStatus, errorIndex, varAP = cmdGen.nextCmd(
        auth,
        cmdgen.UdpTransportTarget((host, 161)),
        cmdgen.MibVariable(p.profileNames,),
        cmdgen.MibVariable(p.rowStatus,),
        cmdgen.MibVariable(p.ssid,),
        cmdgen.MibVariable(p.wire,),
        lookupMib=False
    )

    if errorIndication:
        if request == None:
            return False
        return JsonResponse({"error":True, "message":str(errorIndication)})

    interface_indexes = []

    for varBinds in varAP:
        for oid, val in varBinds:
            if isinstance(val, EndOfMibView):
                continue
            current_oid = oid.prettyPrint()
            current_val = val.prettyPrint()
            # print(current_oid, current_val)
            # if v.ifIndex in current_oid:
            #     ifIndex = int(current_oid.rsplit('.', 1)[-1])
            #     # print(ifIndex,current_val)
            #     results['interfaces'][ifIndex]['ifindex'] = current_val
            #     interface_indexes.append(ifIndex)
            if v.profileNames in current_oid:
                profileNames = int(current_oid.rsplit('.', 1)[-1])
                # print(profileNames,current_val)
                results['AP'][profileNames]['profileNames'] = current_val
                interface_indexes.append(profileNames)
            if v.rowStatus in current_oid:
                profileNames = int(current_oid.rsplit('.', 1)[-1])
                results['AP'][profileNames]['row_status'] = current_val
            if v.ssid in current_oid:
                profileNames = int(current_oid.rsplit('.', 1)[-1])
                results['AP'][profileNames]['ssid'] = current_val
            if v.wire in current_oid:
                profileNames = int(current_oid.rsplit('.', 1)[-1])
                results['AP'][profileNames]['wired'] = lookup_wired(int(current_val))

    errorIndication, errorStatus, errorIndex, varsbn = cmdGen.nextCmd(
        auth,
        cmdgen.UdpTransportTarget((host, 161)),
        cmdgen.MibVariable(p.bsnAPNumOfSlots,),
        cmdgen.MibVariable(p.bsnApIpAddress,),
        cmdgen.MibVariable(p.bsnAPLocation,),
        cmdgen.MibVariable(p.bsnAPMonitorOnlyMode,),
        cmdgen.MibVariable(p.bsnAPOperationStatus,),
        cmdgen.MibVariable(p.bsnAPSoftwareVersion,),
        cmdgen.MibVariable(p.bsnAPBootVersion,),
        cmdgen.MibVariable(p.bsnAPPrimaryMwarName,),
        cmdgen.MibVariable(p.bsnAPReset,),
        cmdgen.MibVariable(p.bsnAPStatsTimer,),
        cmdgen.MibVariable(p.bsnAPPortNumber,),
        cmdgen.MibVariable(p.bsnAPModel,),
        cmdgen.MibVariable(p.bsnAPSerialNumber,),
        cmdgen.MibVariable(p.bsnAPClearConfig,),
        cmdgen.MibVariable(p.bsnApIpAddress,),
        # cmdgen.MibVariable(p.bsnAPMirrorMode,),
        # cmdgen.MibVariable(p.bsnAPRemoteModeSupport,),
        cmdgen.MibVariable(p.bsnAPType,),
        # cmdgen.MibVariable(p.bsnAPSecondaryMwarName,),
        # cmdgen.MibVariable(p.bsnAPTertiaryMwarName,),
        cmdgen.MibVariable(p.bsnAPIsStaticIP,),
        cmdgen.MibVariable(p.bsnAPNetmask,),
        cmdgen.MibVariable(p.bsnAPGateway,),
        cmdgen.MibVariable(p.bsnAPStaticIPAddress,),
        cmdgen.MibVariable(p.bsnAPBridgingSupport,),
        cmdgen.MibVariable(p.bsnAPGroupVlanName,),
        cmdgen.MibVariable(p.bsnAPIOSVersion,),
        cmdgen.MibVariable(p.bsnAPCertificateType,),
        cmdgen.MibVariable(p.bsnAPEthernetMacAddress,),
        cmdgen.MibVariable(p.bsnAPName,),
        lookupMib=False
    )

    if errorIndication:
        if request == None:
            return False
        return JsonResponse({"error":True, "message":str(errorIndication)})

    interface_indexes = []

    for varBinds in varsbn:
        for oid, val in varBinds:
            if isinstance(val, EndOfMibView):
                continue
            current_oid = oid.prettyPrint()
            current_val = val.prettyPrint()
            if v.bsnAPName in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                # print(bsnAPName,current_val)
                results['sbn'][bsnAPName]['bsnAPName'] = current_val
                interface_indexes.append(bsnAPName)
            if v.bsnAPLocation in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPLocation'] = current_val
            if v.bsnAPMonitorOnlyMode in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPMonitorOnlyMode'] = current_val
            if v.bsnAPOperationStatus in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPOperationStatus'] = current_val
            if v.bsnAPSoftwareVersion in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPSoftwareVersion'] = current_val
            if v.bsnAPBootVersion in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPBootVersion'] = current_val
            if v.bsnAPPrimaryMwarName in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPPrimaryMwarName'] = current_val
            if v.bsnAPReset in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPReset'] = current_val
            if v.bsnAPStatsTimer in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPStatsTimer'] = current_val
            if v.bsnAPPortNumber in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPPortNumber'] = current_val
            if v.bsnAPModel in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPModel'] = current_val
            if v.bsnAPSerialNumber in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPSerialNumber'] = current_val
            if v.bsnAPClearConfig in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPClearConfig'] = current_val
            if v.bsnApIpAddress in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnApIpAddress'] = current_val
            if v.bsnAPType in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPType'] = current_val
            if v.bsnAPIsStaticIP in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPIsStaticIP'] = current_val
            if v.bsnAPNetmask in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPNetmask'] = current_val
            if v.bsnAPGateway in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPGateway'] = current_val
            if v.bsnAPStaticIPAddress in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPStaticIPAddress'] = current_val
            if v.bsnAPBridgingSupport in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPBridgingSupport'] = current_val
            if v.bsnAPGroupVlanName in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPGroupVlanName'] = current_val
            if v.bsnAPIOSVersion in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPIOSVersion'] = current_val
            if v.bsnAPCertificateType in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPCertificateType'] = current_val
            if v.bsnAPEthernetMacAddress in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPEthernetMacAddress'] = current_val
            if v.bsnAPAdminStatus in current_oid:
                bsnAPName = int(current_oid.rsplit('.', 1)[-1])
                results['sbn'][bsnAPName]['bsnAPAdminStatus'] = current_val
    # print(results)

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
    # try:
    #     path = "media/snmprecording/"
    #     fileName = "-".join(host.split(".")) + "@" + str(int(time.time())) + ".json"
    #     file = open(path + fileName, "w")
    #     file.write(json.dumps(data , indent=4)) 
    #     file.close() 
    # except Exception as ex:
    #     pass
    # print(data)
    return JsonResponse({"data": data , "fileError" : fileError})
# getDetails(None, "192.168.1.19", "NETWORK123")
