
from django.db import connection
from django.http.request import MediaType
from django.shortcuts import render, HttpResponse
from django.views import View
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from plotly import data
from pysnmp.hlapi import context
from tablib import Dataset
import psutil, re
from django.core import serializers
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import plotly.graph_objects as go
from django.http import JsonResponse
from .models import WebsiteLinks, Product, addDataCenter
from django.views.decorators.clickjacking import xframe_options_exempt
import pandas as pd
from django.db.models import Sum
import socket
import time
from django.conf import settings
from django.contrib.auth import logout
from django.forms.models import model_to_dict
# from .resources import PersonResource
# from .resources import *
from django.contrib.auth.decorators import login_required
# from dashboard.models import PagePermissionForGroup
from django.contrib.auth.models import Group, Permission
from datetime import datetime
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
from . import views_functions

from django.contrib.auth.hashers import make_password, check_password

from django.contrib.auth.models import User
from .models import UserProfile, addDataCenter, addDataCenterRow, AddDataCenterRackcabinet, AddDevice, Notif, DeviceDetails, PatchPanel, PatchPanelPort, DeviceTemplate, DeviceCapibility, CameraMonitor, ContactUs, RaiseTicket, Cabels, TempIPDevice, PduPortForm, DataCenterState
from django.http import JsonResponse
import requests
from requests.exceptions import ConnectionError
from ncclient import manager
from pprint import pprint
from django.contrib.auth import get_user_model
from django.apps import apps
from django.contrib.auth import logout
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
import speedtest
import platform
from django.contrib import messages
from csv import writer
import logging
from django_db_logger.models import StatusLog
from pysnmp.hlapi import *
from django_q.models import Schedule
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))
def snmpChecker(host, cstr):
    try:
        iterator = getCmd(
        SnmpEngine(),
        CommunityData(cstr, mpModel=0),
        UdpTransportTarget((host, 161)),
        ContextData(),
        ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
        )
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if errorIndication:
            return False
        return True
    except:
        return False

def snmpv3checker(host, username, authkey=None, passkey=None): 
    if authkey and passkey:
        try:
            iterator = getCmd(
            SnmpEngine(),
            UsmUserData(username, authkey, passkey,
            privProtocol=usmAesCfb128Protocol),
            UdpTransportTarget((host, 161)),
            ContextData(),
            ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0))
            )
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            if errorIndication:
                return False
            return True
        except:
            return False

        
# @permission_required("dashboard.add_assetpage" , "/")
def addDC(request):
    if request.method == "POST":
        if not request.user.has_perm("dashboard.add_assetpage"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        print("under")
        data = {key:value.strip() for key, value in request.POST.items()}
        print(data)
        if addDataCenter.objects.filter(DataCenterName=data["data_center_name"]):
            msg = "Device with same name already exsist, please select other name"
            # messages.success(request, msg)
            return JsonResponse({
                'err':True,
                'data':msg
            })
        else:
            add = addDataCenter(

                dataCenterTag = data["data_center_tag"],
                DataCenterName = data["data_center_name"],
                sqr_mtr = data["sqr_mtr"],
                Add_country = data["address_country"],
                Add_state = data["address_state"],
                Address = data["address_text"],
                Contact = data["contact"],
                PersonalDet_fname = data["full_name"],
                PersonalDet_email = data["email_contact"], 
                phone = data["phone_contact"], 
                Capacity_in_MW = data["capacity"],

            )
            add.save() 
            msg = "New Data Center Added Successfully"
            # messages.success(request, msg)
            return JsonResponse({
                'err':False,
                'data':msg
            })

# @permission_required("dashboard.add_assetpage" , "/noperm/")
def addRow(request):
    if request.method == "POST":
        if not request.user.has_perm("dashboard.add_assetpage"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        data = {key:value.strip() for key, value in request.POST.items()}
        if addDataCenterRow.objects.filter(data_center=addDataCenter.objects.get(id=data["data_center"]), RackRow=data["rack_row"]):
            return JsonResponse({'err':True,'data':"Row already exsist, please select other row"})
        else:
            add = addDataCenterRow(
                data_center = addDataCenter.objects.get(id=data["data_center"]),
                RackRow = data["rack_row"],
                Row_Label_Tag = data["row_tag"],
                RowColor = data["row_color_form2"],
            )

            add.save()
            return JsonResponse({'err':False, 'data':"New Data Center Row Added Successfully"})

# @permission_required("dashboard.add_assetpage" , "/noperm/")
def addRack(request):
    if request.method == "POST":
        if not request.user.has_perm("dashboard.add_assetpage"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        data = {key:value.strip() for key, value in request.POST.items()}
        
        if AddDataCenterRackcabinet.objects.filter(datacenter=addDataCenter.objects.get(id=data["datacenter"]),date_center_row = addDataCenterRow.objects.get(id=data["rack_row"]), Rack_Label_Tag=data["rack_tag"]):
            return JsonResponse({'err':True,'data':"Rack with same name already present, please select other rack name"})

        else:
            add = AddDataCenterRackcabinet(
            datacenter = addDataCenter.objects.get(id=data["datacenter"]),
                date_center_row = addDataCenterRow.objects.get(id=data["rack_row"]),
                Rack_Label_Tag = data["rack_tag"],
                RowColor = data["row_color_form3"],
                Rack_Type = data["rack_type3"],
                Rack_Type_Information = data.get("customised_rt_information","42"), 
                Special_Notes = data["special_notes"],
            )
            add.save()
            return JsonResponse({'err':False, 'data': "New Data Center Rack (Cabinet) Added Successfully"})

# @permission_required("dashboard.add_assetpage" , "/noperm/")
def deviceAdd(request):
    if request.method == "POST":
        if not request.user.has_perm("dashboard.add_assetpage"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        data = {key:value.strip() for key, value in request.POST.items()}
        row = AddDataCenterRackcabinet.objects.filter(datacenter=addDataCenter.objects.get(id=data["datacenter"]), date_center_row=addDataCenterRow.objects.get(id=data["rack_row"]), Rack_Label_Tag=AddDataCenterRackcabinet.objects.get(id=data["cabinet"]).Rack_Label_Tag)
        total = row[0].Rack_Type_Information

        maxlim = AddDataCenterRackcabinet.objects.get(datacenter=addDataCenter.objects.get(id=data["datacenter"]), date_center_row=addDataCenterRow.objects.get(id=data["rack_row"]),Rack_Label_Tag=AddDataCenterRackcabinet.objects.get(id=data["cabinet"]))
        list_data = maxlim.device_height_array.split(",")
        # sum = AddDevice.objects.get(datacenter=addDataCenter.objects.get(id=data["datacenter"]),date_center_row=addDataCenterRow.objects.get(id=data["rack_row"])).aggregate(Sum('device_height'))
        # filled = sum["device_height__sum"]
        # print(data)
        # print(maxlim.Rack_Type_Information)
        
        if data["device_type"] == "PDU" or data["device_type"] == "vm":
            data["unit_location"] = "-1"
            data["device_heigth"] = "-1"
            
        if data["unit_location"] in list_data:
            msg = "Unit Location already taken, please select other location"
            # messages.success(request, msg)
            return JsonResponse({
            'err':True,
            'data':msg
        })
        elif int(data["unit_location"]) > maxlim.Rack_Type_Information:
            msg = "Only "+str(maxlim.Rack_Type_Information)+" are there"
            # messages.success(request, msg)
            return JsonResponse({
            'err':True,
            'data':msg
        })
        elif int(data["device_heigth"]) > total:
            msg = "device height limit exceeds"
            # messages.success(request, msg)
            return JsonResponse({
            'err':True,
            'data':msg
        })
        else:
            add = AddDevice(
                datacenter = addDataCenter.objects.get(id=data["datacenter"]),
                date_center_row = addDataCenterRow.objects.get(id=data["rack_row"]),
                data_center_rack = AddDataCenterRackcabinet.objects.get(id=data["cabinet"]),
                device_height = data["device_heigth"],
                Device_Asset_Tag = data.get("device_asset_tag",""),
                Device_Description = data.get("device_description",""),
                type_of_device = data.get("device_type",""),

                Unit_Location = data["unit_location"],

                network_device_category = data["network_category"],
                network_sub_category = data["network_device_type_cat"],
                network_number_of_ports = data["network_device_type_ports"],
                network_uplink_ports_wan = data["network_device_type_uplink"],
                network_connection_type_fibre = data.get("network_category_fibre","false"),
                network_connection_type_ehthernet = data.get("network_category_ethernet","false"),
                network_connection_type_both = data.get("network_category_both","false"),

                security_device_category = data["security_device_type_category"],
                security_number_of_ports_lan = data["security_device_type_ports"],
                security_network_uplink_ports_wan = data["security_device_type_uplink"],
                security_connection_type_fibre = data.get("security_category_fibre","false"),
                security_connection_type_ehthernet = data.get("security_category_ethernet","false"),
                security_connection_type_both = data.get("security_category_both","false"),

                patch_position = data["patch_category_pos"],
                patch_port = data["patch_panel_port"],

                server_number_of_ports = data["server_device_type"],
                server_type_fibre = data.get("server_category_fibre","false"),
                server_type_ehthernet = data.get("server_category_ethernet","false"),
                server_type_both = data.get("server_category_both","false"),

                chassis_number_of_blades = data["number_of_blades"],
                chassis_total_blades_slots = data["chasis_device_type_tblades"],
                chassis_type_fibre = data.get("chasis_category_fibre","false"),
                chassis_type_ehthernet = data.get("chasis_category_ethernet","false"),
                chassis_type_both = data.get("chasis_category_both","false"),

                load_number_of_ports = data["load_device_type_ports"],
                load_uplink_ports_wan = data["load_device_type_uplink"],
                load_type_fibre = data.get("load_category_fibre","false"),
                load_type_ehthernet = data.get("load_category_ethernet","false"),
                # load_type_both = data.get("load_category_both","false"),

                storage_number_of_controllers = data["storage_device_type_control"],
                storage_number_of_disks = data["storage_device_type_disks"],
                storage_capicity_range = data["storage_capicity_range"],
                storage_capicity_input = data["storage_capicity_input"],
                storage_type_fibre = data.get("storage_category_fibre","false"),
                storage_type_ehthernet = data.get("storage_category_ethernet","false"),
                storage_type_both = data.get("storage_category_both","false"),


                tapelib_number_of_magazine = data["tape_device_type_magazine"],
                tapelib_number_io_station = data["tape_device_typ_io"],
                tapelib_type = data["tape_type"],
                tapelib_number_tape_capacity = data.get("tape_device_type_tape_capicity",int(0)),
                tapelib_storage_capacity = data["tape_device_type_storage_capicity"],
                tapelib_space_occupied = data["tape_device_type_space"],

                pdu_category = data["pdu_category"],
                pdu_port = data["pdu_port"],
                pdu_type = data["pdu_category_type"],
                pdu_position = data["pdu_category_pos"],

                ups_max_loads = data["ups_category_load"],
                ups_number_of_power_ports = data["ups_device_type"],

                IP_Address_col1 = data.get("ip_address41",int(0)),
                IP_Address_col2 = data.get("ip_address42",int(0)),
                IP_Address_col3 = data.get("ip_address43",int(0)),
                IP_Address_col4 = data.get("ip_address44",int(0)),
                Special_Notes = data["special_notes4"],

                deviceMake = data["DeviceMake"],
                deviceModel = data["DeviceModel"],
                installDate = data.get("InstallDate",""),
                expiryDate = data.get("ExpireDate",""),
                deviceOwner = data.get("DeviceOwner",""),
                ownerDesc = data.get("DeviceOwnerothers",""),
                deviceport = data.get("deviceposrt",int(1)),
                deviceWatt = data.get("DeviceWatt",float(0.0)),

            )
            add.save() 
            msg = "New Device Added Successfully"
            # print(add)
            if not add.type_of_device == "PDU" or add.type_of_device == "vm":
                HEIGHT = int(data["device_heigth"])
                LOC = int(data["unit_location"])
                DATA = ""
                for i in range(HEIGHT):
                    DATA = str(DATA) + "," + str(LOC)
                    LOC = LOC - 1
                if maxlim.device_height_array:
                    maxlim.device_height_array = str(maxlim.device_height_array) + DATA
                else:
                    maxlim.device_height_array = DATA
                maxlim.save()
            # messages.success(request, msg)
            return JsonResponse({
            'err':False,
            'data':msg
        })

# @permission_required("dashboard.add_assetpage" , "/noperm/")
def addSchedule(request):
    if request.method == "POST":
        if not request.user.has_perm("dashboard.add_assetpage"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        data = {key:value.strip() for key, value in request.POST.items()}
        ip_data = ".".join(data["ippart1"].split("/"))
        if (data["scheduleType"] == 'I'):
            Schedule.objects.create(name='Auto Discovery',func='dashboard.schedulejobs.job',args=ip_data,schedule_type=data["scheduleType"],minutes=data["scheduleMin"],repeats=1)
        else:
            Schedule.objects.create(name='Auto Discovery',func='dashboard.schedulejobs.job',args=ip_data,schedule_type=data["scheduleType"],repeats=1)
        msg = "Device Scheduled"
            # messages.success(request, msg)
        return JsonResponse({
                'err':False,
                'data':msg
            })

# @permission_required("dashboard.add_assetpage" , "/noperm/")
def addDCap(request):
    if request.method == "POST":
        if not request.user.has_perm("dashboard.add_assetpage"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        device = DeviceCapibility.objects.all()
        snmp_status = False
        rest_status = False
        net_status = False
        data = {key.strip():request.POST[key].strip() for key in request.POST}
        router = {
            "ip":data["ippart1"]+"."+data["ippart2"]+"."+data["ippart3"]+"."+data["ippart4"],
            'cstring':data.get("cString",""),
            "user":data["username"],
            "password":data["password"],

            "type":data["type"],

            "devicename":data["devicename"],

            "snmpv3user":data["snmpv3user"],
            "snmpv3auth":data["snmpv3auth"],
            "snmpv3pass":data["snmpv3pass"],

            "dbuser":data["dbusername"],
            "dbpwd":data["dbpassword"],
            "dbname":data["dbname"],
            "dbport":data["dbport"],
        } 

        
        if DeviceCapibility.objects.filter(ip=router["ip"]):
            msg = "Device Already Exsists"
            return JsonResponse({
                'err':True,
                'data':msg
            })
        else:
        #SNMP
            if router["cstring"] and router["type"] != "snmp3":
                snmp_status = snmpChecker(router["ip"], router["cstring"])
            
            if router["type"] == "snmp3" and router["snmpv3user"] and router["snmpv3auth"]:
                # SNMP 3
                pass
            if router["type"] == "snmp3" and router["snmpv3user"] and router["snmpv3auth"] and router["snmpv3pass"]:
                snmp_status = snmpv3checker(router["ip"], router["snmpv3user"], router["snmpv3auth"], router["snmpv3pass"])
            #RESTCONF

            NEWdevice = DeviceCapibility(name = router["devicename"],ip = router["ip"],commString = router["cstring"],user = router["user"],pwd = router["password"],is_snmp = snmp_status,is_netconf = net_status,is_restconf = rest_status, updated=datetime.now(), dbuser = router["dbuser"], dbpwd = router["dbpwd"], dbname = router["dbname"],dbport = router["dbport"],snmpv3user = router["snmpv3user"],snmpv3auth = router["snmpv3auth"],snmpv3pass = router["snmpv3pass"])
            NEWdevice.save()
            msg = "New Device Added"
            print(NEWdevice)
            # messages.success(request, msg)
            return JsonResponse({
                'err':False,
                'data':msg,
                'device':(list(DeviceCapibility.objects.filter(ip=NEWdevice).values()))
            })
class EditDeviceCapability(View):
    # def get(self, request):
        
        # try:
        #     device = DeviceCapibility.objects.get(id=self.kwargs['pk'])
        #     return render(request, "dashboard/DeviceCapiEdit.html",{'device':device})
        # except Exception as e:
        #     db_logger.exception(e)
        #     return render(request, "dashboard/DeviceCapiEdit.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})

        
    # @method_decorator(permission_required("dashboard.change_assetpage" , "/noperm/"))
    def post(self, request):
        # print("IN POST", request.POST)
        if not request.user.has_perm("dashboard.change_assetpage"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        try:
            msg = ""
            data = {key.strip():request.POST[key].strip() for key in request.POST}
            # print(data)
            if not data["cString"]:
                data["cString"] = ""
            router = {
                "ip":data["ippart1"],
                "user":data["username"],
                "cstr": data["cString"],
                "password":data["password"],
                "devicename":data["devicename"],
                "id":data["id"],
            }
            if router["cstr"]:
                snmp_status = snmpChecker(router["ip"], router["cstr"])
            device = DeviceCapibility.objects.get(id=router["id"])
            device.name = router["devicename"]
            device.ip = router["ip"]
            device.commString = router["cstr"]
            device.is_snmp = snmp_status
            device.user = router["user"]
            device.pwd = router["password"]
            device.updated = datetime.now()
            device.save()
            msg = "Device Updated Successfully"
            return JsonResponse({
                'data':msg,
                'err':False
            })
        except Exception as e:
            db_logger.exception(e)
            return JsonResponse({
                'data':str(e),
                'err':True
            })
            # path = request.path
            # return render(request, "dashboard/assets_forms.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})


# @permission_required("dashboard.add_assetpage" , "/noperm/")
def deviceTemplateAdd(request):
    if request.method == "POST":
        if not request.user.has_perm("dashboard.add_assetpage"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        data = {key:value.strip() for key, value in request.POST.items()}
        row = AddDataCenterRackcabinet.objects.filter(datacenter=addDataCenter.objects.get(id=data["datacenter"]), date_center_row=addDataCenterRow.objects.get(id=data["rack_row"]), Rack_Label_Tag=AddDataCenterRackcabinet.objects.get(id=data["cabinet"]).Rack_Label_Tag)
        total = row[0].Rack_Type_Information

        maxlim = AddDataCenterRackcabinet.objects.get(datacenter=addDataCenter.objects.get(id=data["datacenter"]), date_center_row=addDataCenterRow.objects.get(id=data["rack_row"]),Rack_Label_Tag=AddDataCenterRackcabinet.objects.get(id=data["cabinet"]))
        list_data = maxlim.device_height_array
        # sum = AddDevice.objects.get(datacenter=addDataCenter.objects.get(id=data["datacenter"]),date_center_row=addDataCenterRow.objects.get(id=data["rack_row"])).aggregate(Sum('device_height'))
        # filled = sum["device_height__sum"]
        # print(data)
        # print(maxlim.Rack_Type_Information)
        if data["unit_location"] in list_data: 
            msg = "Unit Location already taken, please select other location"
            # messages.success(request, msg)
            return JsonResponse({
            'err':True,
            'data':msg
        })
        elif int(data["unit_location"]) > maxlim.Rack_Type_Information:
            msg = "Only "+str(maxlim.Rack_Type_Information)+" are there"
            # messages.success(request, msg)
            return JsonResponse({
            'err':True,
            'data':msg
        })
        elif int(data["device_heigth"]) > total: 
            msg = "device height limit exceeds"
            # messages.success(request, msg)
            return JsonResponse({
            'err':True,
            'data':msg
        })
        else:
            add = DeviceTemplate(
                datacenter = data.get("datacenter",""),
                date_center_row = data.get("rack_row",""),
                data_center_rack = data.get("cabinet",""),
                device_height = data.get("device_heigth",0),
                Device_Asset_Tag = data["device_asset_tag"],
                Device_Description = data["device_description"],
                type_of_device = data["device_type"],

                Unit_Location = data.get("unit_location",0),

                network_device_category = data["network_category"],
                network_sub_category = data["network_device_type_cat"],
                network_number_of_ports = data["network_device_type_ports"],
                network_uplink_ports_wan = data["network_device_type_uplink"],
                network_connection_type_fibre = data.get("network_category_fibre","false"),
                network_connection_type_ehthernet = data.get("network_category_ethernet","false"),
                network_connection_type_both = data.get("network_category_both","false"),

                security_device_category = data["security_device_type_category"],
                security_number_of_ports_lan = data["security_device_type_ports"],
                security_network_uplink_ports_wan = data["security_device_type_uplink"],
                security_connection_type_fibre = data.get("security_category_fibre","false"),
                security_connection_type_ehthernet = data.get("security_category_ethernet","false"),
                security_connection_type_both = data.get("security_category_both","false"),

                patch_position = data["patch_category_pos"],

                server_number_of_ports = data["server_device_type"],
                server_type_fibre = data.get("server_category_fibre","false"),
                server_type_ehthernet = data.get("server_category_ethernet","false"),
                server_type_both = data.get("server_category_both","false"),

                chassis_number_of_blades = data["number_of_blades"],
                chassis_total_blades_slots = data["chasis_device_type_tblades"],
                chassis_type_fibre = data.get("chasis_category_fibre","false"),
                chassis_type_ehthernet = data.get("chasis_category_ethernet","false"),
                chassis_type_both = data.get("chasis_category_both","false"),

                load_number_of_ports = data["load_device_type_ports"],
                load_uplink_ports_wan = data["load_device_type_uplink"],
                load_type_fibre = data.get("load_category_fibre","false"),
                load_type_ehthernet = data.get("load_category_ethernet","false"),
                # load_type_both = data.get("load_category_both","false"),

                storage_number_of_controllers = data["storage_device_type_control"],
                storage_number_of_disks = data["storage_device_type_disks"],
                storage_capicity_range = data["storage_capicity_range"],
                storage_capicity_input = data["storage_capicity_input"],
                storage_type_fibre = data.get("storage_category_fibre","false"),
                storage_type_ehthernet = data.get("storage_category_ethernet","false"),
                storage_type_both = data.get("storage_category_both","false"),


                tapelib_number_of_magazine = data["tape_device_type_magazine"],
                tapelib_number_io_station = data["tape_device_typ_io"],
                tapelib_type = data["tape_type"],
                tapelib_number_tape_capacity = data.get("tape_device_type_tape_capicity",int(0)),
                tapelib_storage_capacity = data["tape_device_type_storage_capicity"],
                tapelib_space_occupied = data["tape_device_type_space"],

                pdu_category = data["pdu_category"],
                pdu_port = data["pdu_port"],
                pdu_type = data["pdu_category_type"],
                pdu_position = data["pdu_category_pos"],

                ups_max_loads = data["ups_category_load"],
                ups_number_of_power_ports = data["ups_device_type"],

                IP_Address_col1 = data.get("ip_address41",int(0)),
                IP_Address_col2 = data.get("ip_address42",int(0)),
                IP_Address_col3 = data.get("ip_address43",int(0)),
                IP_Address_col4 = data.get("ip_address44",int(0)),
                Special_Notes = data["special_notes4"],

                deviceMake = data["DeviceMake"],
                deviceModel = data["DeviceModel"],
                installDate = data.get("InstallDate",""),
                expiryDate = data.get("ExpireDate",""),
                deviceOwner = data.get("DeviceOwner",""),
                ownerDesc = data.get("DeviceOwnerothers",""),
                deviceport = data.get("deviceposrt",int(1)),
                deviceWatt = data.get("DeviceWatt",float(0.0)),
                templatename = data.get("quickTemplate",""),                        
            )
            add.save() 
            msg = "New Device Template Added Successfully"
            # messages.success(request, msg)
            return JsonResponse({
            'err':False,
            'data':msg
        })
        
def getTemplateData(request):
    id = request.POST.get("id")
    device = DeviceTemplate.objects.get(templatename=id)
    # print(device.id)
    return JsonResponse(
        {
            "datacenter":device.datacenter,
            "date_center_row":device.date_center_row,
            "data_center_rack":device.data_center_rack,
            "device_height":device.device_height,
            "Device_Asset_Tag":device.Device_Asset_Tag,
            "Device_Description":device.Device_Description,
            "type_of_device":device.type_of_device,

            "Unit_Location":device.Unit_Location,

            "network_device_category":device.network_device_category,
            "network_sub_category":device.network_sub_category,
            "network_number_of_ports":device.network_number_of_ports,
            "network_uplink_ports_wan":device.network_uplink_ports_wan,
            "network_connection_type_fibre":device.network_connection_type_fibre,
            "network_connection_type_ehthernet":device.network_connection_type_ehthernet,
            "network_connection_type_both":device.network_connection_type_both,

            "security_device_category":device.security_device_category,
            "security_number_of_ports_lan":device.security_number_of_ports_lan,
            "security_network_uplink_ports_wan":device.security_network_uplink_ports_wan,
            "security_connection_type_fibre":device.security_connection_type_fibre,
            "security_connection_type_ehthernet":device.security_connection_type_ehthernet,
            "security_connection_type_both":device.security_connection_type_both,

            "patch_position":device.patch_position,

            "server_number_of_ports":device.server_number_of_ports,
            "server_type_fibre":device.server_type_fibre,
            "server_type_ehthernet":device.server_type_ehthernet,
            "server_type_both":device.server_type_both,

            "chassis_number_of_blades":device.chassis_number_of_blades,
            "chassis_total_blades_slots":device.chassis_total_blades_slots,
            "chassis_type_fibre":device.chassis_type_fibre,
            "chassis_type_ehthernet":device.chassis_type_ehthernet,
            "chassis_type_both":device.chassis_type_both,

            "load_number_of_ports":device.load_number_of_ports,
            "load_uplink_ports_wan":device.load_uplink_ports_wan,
            "load_type_fibre":device.load_type_fibre,
            "load_type_ehthernet":device.load_type_ehthernet,
            # load_type_both:device.

            "storage_number_of_controllers":device.storage_number_of_controllers,
            "storage_number_of_disks":device.storage_number_of_disks,
            "storage_capicity_range":device.storage_capicity_range,
            "storage_capicity_input":device.storage_capicity_input,
            "storage_type_fibre":device.storage_type_fibre,
            "storage_type_ehthernet":device.storage_type_ehthernet,
            "storage_type_both":device.storage_type_both,


            "tapelib_number_of_magazine":device.tapelib_number_of_magazine,
            "tapelib_number_io_station":device.tapelib_number_io_station,
            "tapelib_type":device.tapelib_type,
            "tapelib_number_tape_capacity":device.tapelib_number_tape_capacity,
            "tapelib_storage_capacity":device.tapelib_storage_capacity,
            "tapelib_space_occupied":device.tapelib_space_occupied,

            "pdu_category":device.pdu_category,
            "pdu_position":device.pdu_position,

            "ups_max_loads":device.ups_max_loads,
            "ups_number_of_power_ports":device.ups_number_of_power_ports,

            "IP_Address_col1":device.IP_Address_col1,
            "IP_Address_col2":device.IP_Address_col2,
            "IP_Address_col3":device.IP_Address_col3,
            "IP_Address_col4":device.IP_Address_col4,
            "Special_Notes":device.Special_Notes,

            "deviceMake":device.deviceMake,
            "deviceModel":device.deviceModel,
            "installDate":device.installDate,
            "expiryDate":device.expiryDate,
            "deviceOwner":device.deviceOwner,
            "ownerDesc":device.ownerDesc,
            "deviceWatt":device.deviceWatt,
            "deviceSupplies":device.deviceSupplies,  
        }, status=200)




def showdc(request):
    try:
        dc = addDataCenter.objects.all().values_list()
        return JsonResponse({
                "dc":list(dc),
            }, status=200)
    except Exception as err:
        print("No DC Found")

def showRows(request):
    try:
        id = request.POST.get("id")
        rows = addDataCenterRow.objects.filter(data_center=id).values_list()
        return JsonResponse({
                "rows":list(rows),
            }, status=200)
    except Exception as err:
        print("No Row Found")

def showRacks(request):
    try:
        datacenter = request.POST.get("device_id")
        row = request.POST.get("row_id")
        rows = AddDataCenterRackcabinet.objects.filter(datacenter=datacenter, date_center_row=row).values_list()
        return JsonResponse({
                "rows":list(rows),
            }, status=200)
    except Exception as err:
        print("No Rack Found")
def showUnitLoc(request):
    try:
        datacenter = int(request.POST.get("device_id"))
        row = int(request.POST.get("row_id"))
        rack = int(request.POST.get("rack_id"))
        maxlim = AddDataCenterRackcabinet.objects.get(datacenter=addDataCenter.objects.get(id=datacenter), date_center_row=addDataCenterRow.objects.get(id=row),Rack_Label_Tag=AddDataCenterRackcabinet.objects.get(id=rack))
        rackheight = maxlim.device_height_array
        rows = AddDataCenterRackcabinet.objects.filter(datacenter=datacenter, date_center_row=row, id=rack).values_list('Rack_Type_Information', flat=True).first()
        return JsonResponse({
                "rows":rows,
                'rackheight':rackheight
            }, status=200)
    except Exception as err:
        print(str(err))
def checkUnitLoc(request):
    try:
        datacenter = int(request.POST.get("device_id"))
        row = int(request.POST.get("row_id"))
        rack = int(request.POST.get("rack_id"))
        unit = str(request.POST.get("unit"))
        maxlim = AddDataCenterRackcabinet.objects.get(datacenter=addDataCenter.objects.get(id=datacenter), date_center_row=addDataCenterRow.objects.get(id=row),Rack_Label_Tag=AddDataCenterRackcabinet.objects.get(id=rack))
        list_data = maxlim.device_height_array.split(",")
        if unit in list_data: 
            return JsonResponse({
                "info":"Unit Location already taken, please select other location"
            }, status=200)
        else:
            return JsonResponse({
                "info":"Available"
            }, status=200)
    except Exception as err:
        print(str(err))
def leftHeight(request):
    try:
        rack = int(request.POST.get("rack_id"))
        unit = int(request.POST.get("unit"))
        maxheight = AddDataCenterRackcabinet.objects.get(id=rack)
        res = maxheight.device_height_array.split(",")
        res = list(map(int, res))
        list_of_numbers = res
        list_of_numbers.sort(reverse=True)
        remaining_height = min(list_of_numbers,key=lambda x : x - unit > 0 )
        final_res = unit - remaining_height
        return JsonResponse({
            'height':final_res
        })
    except Exception as err:
        print(str(err))

def showavailableRacks(request):
    try:
        datacenter = request.POST.get("device_id")
        row = request.POST.get("row_id")
        rows = AddDataCenterRackcabinet.objects.filter(datacenter=datacenter, date_center_row=row).values_list()
        return JsonResponse({
                "rows":list(rows),
            }, status=200)
    except Exception as err:
        print("No Available Racks Found")
        
def cap_device(request):
    device = DeviceCapibility.objects.all().order_by("-created")
    maxDataToShow = request.GET.get('max')
    if not maxDataToShow:
        maxDataToShow = 2
    paginator = Paginator(device, maxDataToShow)
    page = request.GET.get('page')
    
    try:
        users = paginator.page(page)
    # If the number of pages is not an integer, return to the first page
    except PageNotAnInteger:
        users = paginator.page(1)
    # If the number of pages does not exist / is illegal, return to the last page
    except InvalidPage:
        users = paginator.page(paginator.num_pages)
    user_li = list(users.object_list.values())
    # They are whether there is false/true on the previous page, whether there is false/true on the next page, the total number of pages, and the data of the current page
    result = {'has_previous': users.has_previous(),
                'has_next': users.has_next(),
                'num_pages': users.paginator.num_pages,
                # 'total_page':paginator.count,
                'user_li': user_li}
    return JsonResponse(result)




def ipdevices(request):
    tempipdevice = TempIPDevice.objects.filter(status=True).order_by("-created").distinct()
    maxDataToShow = request.GET.get('max')
    if not maxDataToShow:
        maxDataToShow = 2
    paginator = Paginator(tempipdevice, maxDataToShow)
    page = request.GET.get('page')
    
    try:
        users = paginator.page(page)
    # If the number of pages is not an integer, return to the first page
    except PageNotAnInteger:
        users = paginator.page(1)
    # If the number of pages does not exist / is illegal, return to the last page
    except InvalidPage:
        users = paginator.page(paginator.num_pages)
    user_li = list(users.object_list.values())
    # They are whether there is false/true on the previous page, whether there is false/true on the next page, the total number of pages, and the data of the current page
    result = {'has_previous': users.has_previous(),
                'has_next': users.has_next(),
                'num_pages': users.paginator.num_pages,
                # 'total_page':paginator.count,
                'user_li': user_li}
    return JsonResponse(result)
