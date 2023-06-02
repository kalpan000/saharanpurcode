from dashboard.models import DeviceCapibility
import json
from django.http.response import JsonResponse
from django.shortcuts import render
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1905 import EndOfMibView
from collections import defaultdict
import codecs
import binascii
import datetime
    
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
    if hexStr.isdigit():
        return hexStr
    try:
        hex = hexStr[2:]
        bytes_object = bytes.fromhex(hex)
        ascii_string = bytes_object.decode("ASCII")
        return ascii_string
    except Exception as ex:
        return hexStr

def Tree():
    return defaultdict(Tree)

def index(request):
    ip = request.GET["ip"]
    dc = DeviceCapibility.objects.get(ip = ip)
    data = {
        "ip" : dc.ip,
        "snmp" : dc.commString
    }
    return render(request, "snmpDashboard.html", data)

def checkdatatype(data, type):
    if type == "str":
        data = hex_to_str(data)
    elif type == "num":
        data = int(data)
    elif type == "timetick":
        time = int(data)/100
        day = time // (24 * 3600)
        time = time % (24 * 3600)
        hour = time // 3600
        time %= 3600
        minutes = time // 60
        time %= 60
        seconds = time

        data = str(int(day))+"D "+str(int(hour))+":"+str(int(minutes))+":"+str(round(seconds,2))
    else:
        pass
    return data

def getDetail(request):
    try:
        results = Tree()

        oid = request.GET["oid"]
        title = request.GET["title"]
        type = request.GET["type"]
        datatype = request.GET["datatype"]
        host = request.GET.get("host", "localhost")
        snmp_cstr = request.GET.get("cstr", "public")

        auth = cmdgen.CommunityData(snmp_cstr)
        cmdGen = cmdgen.CommandGenerator()

        if type == "single":
            errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(auth,
                cmdgen.UdpTransportTarget((host, 161)),
                cmdgen.MibVariable("."+oid,),
                lookupMib=False
            )
            if errorIndication:
                return JsonResponse({"status":False, "data":str(errorIndication)})

            for oid, val in varBinds:
                current_val = val.prettyPrint()
                results[title] = checkdatatype(current_val, datatype)

        elif type == "multi":
            pass
        else:
            print("Invalid Type")
        
        data = defdict_to_dict(results, {})

        return JsonResponse({"status":True, "data":data})
    except Exception as err:
        return JsonResponse({"status":False, "data":str(err)})