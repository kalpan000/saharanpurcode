from cgi import print_directory
from pydoc import describe

from matplotlib.pyplot import sca
from dashboard.views_assets import top
from uptime import uptime as customUptime
from django.shortcuts import render, HttpResponse
from django.views import View
from collections import Counter
from dashboard.views_apm import CPU
import os, socket
from django.db.models import Q
import random, ipcalc, re
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import login
from import_export import resources
from tablib import Dataset
import psutil
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import SnmpDeviceSetting, StartApp, WebsiteLinks,Product, addDataCenter
import pandas as pd
from django.db.models import Sum
import socket
import time
from .schedulejobs import scan
from django.conf import settings
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
# from .resources import PersonResource
# from .resources import *
from django.contrib.auth.decorators import login_required
# from dashboard.models import PagePermissionForGroup
from django.contrib.auth.models import Group, Permission, User
from datetime import datetime
from .views_nms import runssh

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .models import UserProfile,addDataCenter, SaveXYZ, addDataCenterRow, AddDataCenterRackcabinet, AddDevice, Notif, DeviceDetails, PatchPanel,PatchPanelPort, DeviceCapibility, ContactUs, RaiseTicket , Cabels, TempIPDevice, PduPortForm, DeviceSetting, AssetPage, NetworkSummary ,ServerSummary,DatabaseSummary,StorageSummary,CCTV,WebMonitoring,Reports,APM,Settings,Dashboard,Appliance, Topology

from .forms import RaiseTicketForm
from django.apps import apps
from django.contrib.auth import logout
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import platform
from django.contrib import messages
import logging
from django_db_logger.models import StatusLog
from .views_topology import mainFunction

from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
from .viewsSNMP import getDetails

from .views_management import snmpv3checker
@login_required
def patchesGet(request):
    type = request.GET.get("type", "server")
    print(type)
    
    if type == "server":
        type = "Server"
    else:
        type = 'Network'
    selectOptionDevices = []

    data = AddDevice.objects.filter(type_of_device = type)
    for record in data:
        ip = str(record.IP_Address_col1) + "." + str(record.IP_Address_col2) + "." + str(record.IP_Address_col3) + "." + str(record.IP_Address_col4)
        selectOptionDevices.append(ip)
    records = DeviceCapibility.objects.filter(ip__in = selectOptionDevices)

    print(len(records) , records)
    data = {
        "records" : records
    }

    return render(request , "dashboard/patches.html" , data)


def runLinuxPatch(devices, command):
    for i in devices:
        try:
            client = runssh(i, devices[i]["username"], str(devices[i]["password"]))
            if client:
                for cmd in command:
                    _, stdout, stderr = client.exec_command(cmd)
                    status = stdout.channel.recv_exit_status()    
                    if (status == 0):
                        print(stdout.read().decode('utf-8'))
                    else:
                        print(str(stderr.read().decode('utf-8')))
        except:
            pass
    return 1

def runWindowsPatch(devices, cmd):
    pass

@csrf_exempt
def runPatch(request):

    data = json.loads(request.POST.get("data",{}))
    cmd = json.loads(request.POST.get("commands",[]))
    if request.POST["type"] == "linux":
        res = runLinuxPatch(data, cmd)
    else:
        res = runWindowsPatch(data, request.POST.get("commands",[]))
    return JsonResponse({"error":False,"message":res})

def noperm(request):
    return render(request , "dashboard/error.html")

# db_logger = logging.getLogger('db')
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))

def custom_page_not_found_view(request, exception):
    data = {
            "title":"Page Not Found",
            "result":404,
            "helping_text":"Page not found",
        }
    return render(request, "dashboard/message_page.html", data)

def custom_error_view(request, exception=None):
    data = {
            "title":"Something Error",
            "result":500,
            "helping_text":"Something went wrong",
        }
    return render(request, "dashboard/message_page.html", data)

def custom_permission_denied_view(request, exception=None):
    data = {
            "title":"Page Permission Denied",
            "result":403,
            "helping_text":"You don't have permission to this page",
        }
    return render(request, "dashboard/message_page.html", data)

def custom_bad_request_view(request, exception=None):
    data = {
            "title":"Bad Request",
            "result":400,
            "helping_text":"Bad Request",
        }
    return render(request, "dashboard/message_page.html", data)

try:
    obj, created = DeviceSetting.objects.update_or_create(id=1)
except Exception as err:
    # print("Device Setting Done")
    pass
def startPage(request):
    try:
        firstTime = StartApp.objects.get(id=1)
        if firstTime.is_start:
            return redirect('/login')
        return render(request, 'starter/index.html')
    except Exception as err:
        print(str(err))
        return render(request, 'starter/index.html')

def xyzSettings(request):
    ipaddress = request.POST.get("ipaddress").strip()
    subnet = request.POST.get("subnet").strip()
    gateway = request.POST.get("gateway").strip()
    dns1 = request.POST.get("dns1").strip()
    dns2 = request.POST.get("dns2").strip()

    try:
        SaveXYZ.objects.create(ipaddress=ipaddress , subnet=subnet , gateway=gateway , dns1=dns1 , dns2=dns2)
    except Exception as ex:
        return {"error" : True , "message" : str(ex)}

    return {"error" : False , "message" : "success"}

@csrf_exempt
def saveStarterSetting(request):
    data = {key:value.strip() for key, value in request.POST.items()}
    print(data)
    first_name = data["data[first_name]"]
    last_name = data["data[last_name]"]
    username = data["data[user_name]"]
    password = data["data[password]"]
    email = data["data[email]"]
    # country = data["data[country]"]
    if User.objects.filter(Q(email=email)).count():
        return JsonResponse({'error':True, 'data':"Email Already Exsist"})
    elif User.objects.filter(Q(username=username)).count():
        return JsonResponse({'error':True, 'data':"Username Already Exsist"})
    else:
        user = User()
        user.username = username
        user.email = email
        # user.password = data['password']
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        user.is_superuser = True   
        user.is_admin = True
        user.is_staff = True    

        user.save()

        profile = UserProfile()
        profile.user = user
        profile.staff_type = "SUPERADMIN"
        # profile.master_password = data['master_password']
        profile.save()
        # country = DeviceSetting()
        # country.country = country
        # country.save()
        obj, created = StartApp.objects.update_or_create(id=1, defaults={'is_start':True})
        login(request, user)
        return redirect('/')
    # print(data)
    # return JsonResponse({'error':False, 'data':data})

def get_notifications(request):
    all_notifications = Notif.objects.filter(is_read=False, is_delete=False).order_by("-date")[:5]
    count = Notif.objects.filter(is_delete=False, is_read=False).count()
    try:
        footer = DeviceSetting.objects.get(id=1)
    except:
        footer = DeviceSetting.objects.update_or_create(id = 1)
    return {
        'notifications':all_notifications, 'count':count, 'footer':footer.footer
    }

def change_footer(request):
    option = request.GET.get("choice")
    try:
        footer = DeviceSetting.objects.get(id=1)
    except:
        footer = DeviceSetting.objects.update_or_create(id = 1)
    if option == "1" or option == 1:
        footer.footer = "Made with <img src='/static/dashboard/images/heart.png'> in <img src='/static/dashboard/images/india.png'>"
    else:
        footer.footer = "Made in India"
    footer.save()
    return JsonResponse({'error':False})

def get_notifications_count(request):
    count = Notif.objects.filter(is_delete=False, is_read=False).count()
    return JsonResponse({
        'count':count
    })
    
def myPath(request,id, value):
    
    try:
        d = DeviceCapibility.objects.get(id=id)
        value = value
        if value=='snmp':
            context = {'device':d.snmp}
        if value=='rest':
            context = {'device':d.restconf}
        if value=='net':
            context = {'device':d.netconf}
        # print(device)
        return render(request , "dashboard/displayServerInformation.html",context)
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/displayServerInformation.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

# CABLES FUNCTIONS 
# @method_decorator(permission_required("dashboard.add_adddatacenter" , "/noperm/"))
@csrf_exempt
def cablesPOST(request):
    try:
        obj = Cabels.objects.get(name=request.POST["title"])
        #obj.quantity = int(obj.quantity) + int(request.POST["qty"])
        obj.quantity = int(request.POST["qty"])
        obj.save()
    except Cabels.DoesNotExist:
        obj = Cabels(name=request.POST["title"], quantity=request.POST["qty"])
        obj.save()
        return JsonResponse({"error" : False , "message" : "Updated Successfully"})
        db_logger.exception(e)
            
    return JsonResponse({"error" : False , "message" : "Updated Successfully"})


@csrf_exempt
def cablesDevices(request):
    deviceID = request.POST["deviceID"]
    deviceName = request.POST["deviceName"]
    device = AddDevice.objects.get(id=deviceID)
    queries = PatchPanelPort.objects.filter(patchpanel=device)
    connections = []
    
    for query in queries:
        connections.append({"device" : query.device.Device_Asset_Tag , "id" : query.device.id , "port" : query.port})

    data = {
        "error" : False,
        "device" : deviceName,
        "connections" : connections
    }
    return JsonResponse(data)


@login_required(redirect_field_name=None)
@csrf_exempt
def cablesGET(request):
    records = Cabels.objects.all()
    j = {}

    for record in records:
        j[record.name] = record.quantity

    print(j)

    queries = PatchPanelPort.objects.all()
    devices = []
    for query in queries:
        devices.append({"port" : query.port , "id" : query.patchpanel.id , "name" : query.patchpanel.Device_Asset_Tag })

    data = {
        "cablesData" : j,
        "deviceData" : devices
    }

    return render(request, 'dashboard/cables.html' , data)



def logoutView(request):
    logout(request)
    return redirect('/login')

      
        
    
# class Notification(object):
#     def __init__(self):
#         pass
#     def trigger_email(self):
#         pass

#     def show_result(self, **kwargs):
#         context = {
#             "other" : "",
#             "button_text":"Contact US",
#             "button_url":"/contact-us/"
#         }

#         for key,value in kwargs.items():
#             if key == "result":
#                 context["result"] = value
#             if key == "helping_text":
#                 context["helping_text"] = value
#             if key == "title":
#                 context["title"] = value
#             if key == "button_text":
#                 context["button_text"] = value
#             if key == "button_url":
#                 context["button_url"] = value
#             else:
#                 context["other"] = context["other"] + value + " ; "

#         return context      


# Create Dashboard  views here

# class autoDiscovery(View):
#     def get(self, request):
#         return render(request, "dashboard/autoDiscover.html")

#     def post(self, request):
        
#         try:
#             msg = ""
#             devices = []
#             data = {key.strip():request.POST[key].strip() for key in request.POST}
#             router = {
#                 "ip":data["ippart1"]+"."+data["ippart2"]+"."+data["ippart3"]+".",
#                 "last":data["ippart4"],
#                 "enRange":data["enRange"],
#             }
#             ip = router["ip"]
#             last = int(router["last"])
#             enRange = int(router["enRange"])+1
#             # print(str(ip) + str(last))
#             def scan(addr):
#                 s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#                 socket.setdefaulttimeout(1)
#                 result = s.connect_ex((addr,443))
#                 if result == 0:
#                     return 1
#                 else :
#                     return 0

#             def run1():
#                 for i in range(last,enRange):
#                     addr = str(ip) + str(i)
#                     if (scan(addr)):
#                         if DeviceCapibility.objects.filter(ip=addr).exists():
#                             devices.append({
#                             'device':addr,
#                             'status':'live',
#                             'action':'none'
#                             })
#                         else:
#                             devices.append({
#                             'device':addr,
#                             'status':'live',
#                             'action':'required'
#                             })
#                         # print (addr , "is live")

#                     else:
#                         devices.append({
#                             'device':addr,
#                             'status':'down',
#                             'action':'none'
#                         })
#                         # print(addr, "is down")
                        
#             run1()
#             print ("Scanning completed")
#             return render(request, "dashboard/autoDiscover.html",{'devices':devices})
#         except Exception as e:
#             db_logger.exception(e)
#             path = request.path
#             return render(request, "dashboard/autoDiscover.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

# class EditDeviceCapabilityPage(View):
#     def get(self, request):
        
#         try:
#             device = DeviceCapibility.objects.all()
#             return render(request, "dashboard/DeviceCapibilityEdit.html",{'device':device})
#         except Exception as e:
#             db_logger.exception(e)
#             path = request.path
#             return render(request, "dashboard/DeviceCapibilityEdit.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})





# class DelDeviceCapabilityPage(View):
#     def get(self, request):
        
#         try:
#             device = DeviceCapibility.objects.all()
#             return render(request, "dashboard/DeviceCapibilityDel.html",{'device':device})
#         except Exception as e:
#             db_logger.exception(e)
#             path = request.path
#             return render(request, "dashboard/DeviceCapibilityDel.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})


class DelDeviceCapability(View):
    # def get(self, request,pk):
        
    #     try:
    #         device = DeviceCapibility.objects.get(id=self.kwargs['pk'])
    #         return render(request, "dashboard/DeviceCapiDel.html",{'device':device})
    #     except Exception as e:
    #         db_logger.exception(e)
    #         return render(request, "dashboard/DeviceCapiDel.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
    def post(self, request):
        print(request.POST.get("id"))
        try:
            msg = ""
            data = request.POST["id"]
            print(data)
            device = DeviceCapibility.objects.get(id=data)
            device.delete()
            msg = "Device Deleted Successfully"
            return JsonResponse({
                'data':msg,
                'err':False
            })
            messages.success(request, msg)
            return redirect('/asset/forms/')
        except Exception as e:
            db_logger.exception(e)
            return JsonResponse({
                'data':str(e),
                'err':True
            })
            # path = request.path
            # return render(request, "dashboard/assets_forms.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
class ScheduleDeviceCapability(View):
    def get(self, request,id):
        
        try:
            device = DeviceCapibility.objects.all()
            return render(request, "dashboard/DeviceCapibilityShedule.html",{'device':device})
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/DeviceCapibilityShedule.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
    def post(self, request,id):
        
        try:
            msg = ""
            data = {key.strip():request.POST[key].strip() for key in request.POST}
            router = {
                "id":data["id"],
                "date":data["date"],
            }
            device = DeviceCapibility.objects.get(id=router["id"])
            device.schedule = router["date"]
            device.save()
            msg = "Schedule Deleted Successfully"
            return redirect('show-device-capability')
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/DeviceCapibilityShedule.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})       
        
        


        
# @login_required(redirect_field_name=None)        
# class Assets(View):
#     def get(self, request):

#         # world_map = views_functions.world_map()
#         india_map_plt = views_functions.indian_map()
#         return render(request,'dashboard/assets.html',
#                       {
#                         #   'world_map':world_map,
#                           'india_map_plt':india_map_plt,
#                       })
    
#     def post(self, request):
        
#         try:
            
#             return render(request, 'dashboard/assets.html')
#         except Exception as e:
#             db_logger.exception(e)
#             path = request.path
#             return render(request, "dashboard/assets.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
# @login_required(redirect_field_name=None)


# class assetsWorld(View):
#     def get(self, request):

#         world_map = views_functions.world_map()
#         return render(request,'dashboard/assets_world.html',
#                       {
#                           'world_map':world_map,
#                       })
    
#     def post(self, request):
        
#         try:
            
#             return render(request, 'dashboard/assets_world.html')
#         except Exception as e:
#             db_logger.exception(e)
#             path = request.path
#             return render(request, "dashboard/assets_world.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
           




@login_required(redirect_field_name=None)
def deleteAssetDevice(request,id):
    try:
        HEIGHT = int(request.GET.get("height"))
        LOC = int(request.GET.get("loc"))
        rackID = int(request.GET.get("rackid"))
        try:
            rack = AddDataCenterRackcabinet.objects.get(id=rackID)   
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})     
        data = []
        arr = rack.device_height_array.split(",")
        for i in range(HEIGHT):
            data.append(LOC)
            LOC = LOC - 1
        data = [str(x) for x in data]
        for i in data:
            if i in arr:
                arr.remove(i)
        new_data = ','.join([str(elem) for elem in arr])
        rack.device_height_array = new_data
        rack.save()
        try:
            dc = AddDevice.objects.get(id=id)
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/assets_forms.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
        dc.delete()
        msg = "Device Deleted"
        messages.success(request, msg)
        return redirect('/asset/forms/')
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/assets_forms.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
# def deleteDevice(request, id):
#     try:
#         goback = request.GET.get("return")
#         HEIGHT = int(request.GET.get("height"))
#         LOC = int(request.GET.get("loc"))
#         rackID = int(request.GET.get("rackid"))
#         try:
#             rack = AddDataCenterRackcabinet.objects.get(id=rackID)   
#         except Exception as e:
#             db_logger.exception(e)
#             return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})     
#         data = []
#         arr = rack.device_height_array.split(",")
#         for i in range(HEIGHT):
#             data.append(LOC)
#             LOC = LOC - 1
#         data = [str(x) for x in data]
#         for i in data:
#             if i in arr:
#                 arr.remove(i)
#         new_data = ','.join([str(elem) for elem in arr])
#         rack.device_height_array = new_data
#         rack.save()
#         try:
#             dc = AddDevice.objects.get(id=id)
#         except Exception as e:
#             db_logger.exception(e)
#             return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
#         dc.delete()
#         return redirect('rack_page', goback)
#     except Exception as e:
#         db_logger.exception(e)
#         path = request.path
#         return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
@login_required(redirect_field_name=None)
def decomAssetDevice(request, id):
    try:
        try:
            dc = AddDevice.objects.get(id=id)
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/assets_forms.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
        dc.is_delete = True
        dc.save()
        msg = "Device Decomissioned"
        messages.success(request, msg)
        return redirect('/asset/forms/')
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/assets_forms.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
@login_required(redirect_field_name=None)
def delete_rack(request, id):
    
    try:
        goback = request.GET.get("return")
        try:
            racks = AddDataCenterRackcabinet.objects.get(id=id)
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/dc.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
        racks.is_delete = True
        racks.save()
        return redirect('datacenter',goback)
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/dc.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
@login_required(redirect_field_name=None)
def edit_rack(request, id):
    
    try:
        data_center = addDataCenter.objects.all()
        racks = AddDataCenterRackcabinet.objects.get(id=id)
        msg = ""
        if request.method == "POST":
            data = {key:value.strip() for key, value in request.POST.items()}
            # print(data)
            racks.datacenter = addDataCenter.objects.get(id=data["datacenter"])
            racks.date_center_row = addDataCenterRow.objects.get(id=data["rack_row"])
            racks.Rack_Label_Tag = data["rack_tag"]
            racks.RowColor = data["row_color_form3"]
            racks.Rack_Type = data["rack_type3"]
            racks.Rack_Type_Information = data.get("customised_rt_information","42")
            racks.Patch_Panels_Ethernet = data.get("ethernet","false")
            racks.Patch_Panels_Fiber = data.get("fibre","false")
            racks.Patch_Panels_Other = data.get("other","false")
            racks.Patch = data.get("patch_panels_information","")
            racks.Special_Notes = data["special_notes"]
            racks.save()
            msg = "New Data Center Rack (Cabinet) Added Successfully"
        return render(request, 'dashboard/edit_rack_form.html', {'racks':racks,'datacenter':data_center,'msg':msg})
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/edit_rack_form.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

@login_required(redirect_field_name=None)
def rack_page(request, id):
    
    try:
        rack = AddDataCenterRackcabinet.objects.get(id=id)
        device = AddDevice.objects.filter(data_center_rack=rack.id)
        tableDevice=device.order_by("-Unit_Location")
        frontDevice = device.filter(pdu_position="front").order_by("-Unit_Location")
        rearDevice = device.filter(pdu_position="rear").order_by("-Unit_Location")
        pdu_devices = device.filter(type_of_device="PDU").count()
        count_device = device.exclude(type_of_device="PDU").count()
        # pdu_devices = pdu_devices.aggregate(Sum('pdu_port'))
        # print(pdu_devices)
        all_device = AddDevice.objects.all()
        details = DeviceDetails.objects.all()
        patchpanel = PatchPanel.objects.filter(rack=rack)
        patchport = PatchPanelPort.objects.all()
        pduDevice = PduPortForm.objects.filter(rack = id)
        # print(pduDevice)
        # details = DeviceDetails.objects.filter(device__data_center_rack=rack.id)
        alphabets = {'50':'BX','49':'BW','48':'BV','47':'BU','46':'BT','45':'BS','44':'BR','43':'BQ','42':'BP','41':'BO','40':'BN','39':'BM','38':'BL','37':'BK','36':'BJ','35':'BI','34':'BH','33':'BG','32':'BF','31':'BE','30':'BD','29':'BC','28':'BB','27':'BA','26':'AZ','25':'AY','24':'AX','23':'AW','22':'AV','21':'AU','20':'AT','19':'AS','18':'AR','17':'AQ','16':'AP','15':'AO','14':'AN','13':'AM','12':'AL','11':'AK','10':'AJ','9':'AI','8':'AH','7':'AG','6':'AF','5':'AE','4':'AD','3':'AC','2':'AB','1':'AA'}
        res = rack.device_height_array.split(",")
        res = list(map(int, res))
        res = list(filter(lambda x : x > 0, res))
        occupied_slots = len(res)
        power_utilization = device.aggregate(Sum('deviceWatt'))
        rackload = power_utilization["deviceWatt__sum"]
        if rackload is None:
            rackload = 0
        if request.method == "POST":          

            if request.POST.get("form_type") == 'formTwo': 
                data = {key:value.strip() for key, value in request.POST.items()}
                # print(data)
                # add, created = DeviceDetails.objects.update_or_create(
                #     device=AddDevice.objects.get(id=data["outgoing_device"]),defaults={'patchpanel_outgoing':data["outgoing_port"],'patchpanel_incoming':0}
                # )
                add = PatchPanelPort(
                    patchpanel = AddDevice.objects.get(id=data["patch"]),
                    device = AddDevice.objects.get(id=data["device"]),
                    port = data["port"],
                    information = data["information"],
                    in_out = data["inOut"]
                )
                add.save()
                msg = "Patch Port added"
                return render(request, 'dashboard/rackinfo.html',{
                        'msg' : msg,'datacenterracks':rack, 'device':device, 'alphabets':alphabets, 'details':details,'all_device':all_device,'patchpanel':patchpanel,'patchport':patchport,'frontDevice':frontDevice,'rearDevice':rearDevice,'tableDevice':tableDevice,'pdu_devices':pdu_devices,'occupied_slots':occupied_slots,'rackload':round(rackload,2),'pduDevice':pduDevice,'count_device':count_device
                    })

            if request.POST.get("form_type") == 'formThree': 
                data = {key:value.strip() for key, value in request.POST.items()}
                value = int(data["patch"])
                # print(value)
                return render(request, 'dashboard/rackinfo.html',{
                        'datacenterracks':rack, 'device':device, 'alphabets':alphabets, 'details':details,'all_device':all_device,'patchpanel':patchpanel,'patchport':patchport,'value':value,'frontDevice':frontDevice,'rearDevice':rearDevice,'tableDevice':tableDevice,'pdu_devices':pdu_devices,'occupied_slots':occupied_slots,'rackload':round(rackload,2),'pduDevice':pduDevice,'expand':True,'count_device':count_device
                    })
            if request.POST.get("form_type") == 'formFour': 
                # print("Fourthfoem")
                data = {key:value.strip() for key, value in request.POST.items()}
                pdu_device = data["pdu"]
                pdu_type = data["power_type"]
                port = int(data["port"])
                deviceid = data["device"]
                devicePort = data["deviceport"]  
                obj, created = PduPortForm.objects.update_or_create(device_port=devicePort,device=AddDevice.objects.get(id=deviceid),rack=rack,defaults={'pdu_type':pdu_type,'pdu_port':port,'device_port':devicePort, 'device':AddDevice.objects.get(id=deviceid), 'pdudevice':AddDevice.objects.get(id=pdu_device)})
                msg = "PDU Port added"             
                return render(request, 'dashboard/rackinfo.html',{
                        'msg':msg, 'datacenterracks':rack, 'device':device, 'alphabets':alphabets, 'details':details,'all_device':all_device,'patchpanel':patchpanel,'patchport':patchport,'frontDevice':frontDevice,'rearDevice':rearDevice,'tableDevice':tableDevice,'pdu_devices':pdu_devices,'occupied_slots':occupied_slots,'rackload':round(rackload,2),'pduDevice':pduDevice,'count_device':count_device
                    })
        return render(request, "dashboard/rackinfo.html", {'datacenterracks':rack, 'device':device, 'alphabets':alphabets, 'details':details,'all_device':all_device,'patchpanel':patchpanel,'patchport':patchport,'frontDevice':frontDevice,'rearDevice':rearDevice,'tableDevice':tableDevice,'pdu_devices':pdu_devices,'occupied_slots':occupied_slots,'rackload':round(rackload,2),'pduDevice':pduDevice,'count_device':count_device})
        # return HttpResponse("Open Datacenter "+str(id))
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
def getpdutype(request):
    id = int(request.POST.get("id"))
    device = AddDevice.objects.get(id=id)
    ltype = ""
    port = ""
    if (device.type_of_device == "PDU"):
        ltype = device.pdu_type
        port = device.pdu_port
    if (device.type_of_device == "UPS"):
        ltype = "left"
        port = device.ups_number_of_power_ports
    return JsonResponse({
        'pduType':ltype,
        'pduPort':port,
        'devicePort':device.deviceport,
    })

def getpatchport(request):
    id = int(request.POST.get("id"))
    device = AddDevice.objects.get(id=id)
    return JsonResponse({
        'patchPort':device.patch_port,
    })

def getdeviceport(request):
    id = int(request.POST.get("id"))
    device = AddDevice.objects.get(id=id)
    return JsonResponse({
        'devicePort':device.deviceport,
    })

@login_required(redirect_field_name=None)
def deleteDevice(request, id):
    try:
        goback = request.GET.get("return")
        HEIGHT = int(request.GET.get("height"))
        LOC = int(request.GET.get("loc"))
        rackID = int(request.GET.get("rackid"))
        try:
            rack = AddDataCenterRackcabinet.objects.get(id=rackID)   
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})     
        data = []
        arr = rack.device_height_array.split(",")
        for i in range(HEIGHT):
            data.append(LOC)
            LOC = LOC - 1
        data = [str(x) for x in data]
        for i in data:
            if i in arr:
                arr.remove(i)
        new_data = ','.join([str(elem) for elem in arr])
        rack.device_height_array = new_data
        rack.save()
        try:
            dc = AddDevice.objects.get(id=id)
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
        dc.delete()
        return redirect('rack_page', goback)
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
    
def patch_panel(request):
    
    # if request.POST.get("form_type") == 'formOne':
    #     try:
    #         data = {key:value.strip() for key, value in request.POST.items()}
    #         # print(data)
    #         add, created = DeviceDetails.objects.update_or_create(
    #             device=AddDevice.objects.get(id=data["incoming_device"]),defaults={'patchpanel_incoming':data["incoming_port"],'patchpanel_outgoing':0}
    #         )
    #         # add.save()
    #         msg = "New Device Added Successfully"
    #         return render(request, 'dashboard/rackinfo.html',{
    #                 'msg' : msg,'datacenterracks':rack, 'device':device, 'alphabets':alphabets, 'details':details,'all_device':all_device,
    #             })
    #     except Exception as e:
    #         db_logger.exception(e)
    #         path = request.path
    #         return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
    if request.POST.get("form_type") == 'formTwo': 
        try:
            data = {key:value.strip() for key, value in request.POST.items()}
            # print(data)
            add = DeviceDetails(
                device = AddDevice.objects.get(id=data["outgoing_device"]),
                patchpanel_incoming = 0,
                patchpanel_outgoing = int(data["outgoing_port"]),
                )
            add.save()
            msg = "New Device Added Successfully"
            return render(request, 'dashboard/rackinfo.html',{
                    'msg' : msg,
                })
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/rackinfo.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
@login_required(redirect_field_name=None)
def device_page(request, id):
    
    try:
        device = AddDevice.objects.get(id=id)
        return render(request, "dashboard/deviceinfo.html", {'device':device})

        # return HttpResponse("Open Datacenter "+str(id))
    except Exception as e:
        db_logger.exception(e)
        return render(request, "dashboard/deviceinfo.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})

#POWER ON or OFF
# def change_device_status_right(request):
#     id = request.POST.get("id")
#     device = AddDevice.objects.get(id=id)
#     if device.power_right:
#         device.power_right=False
#         device.save()
#         # return redirect('/show/user', {'allusers': User.objects.all()})
#         return JsonResponse({"msg":"Right Device Off",}, status=200)
#     else:
#         device.power_right=True
#         device.save()
#         return JsonResponse({"msg":"Right Device On",}, status=200)
# def change_device_status_left(request):
#     id = request.POST.get("id")
#     device = AddDevice.objects.get(id=id)
#     if device.power_left:
#         device.power_left=False
#         device.save()
#         # return redirect('/show/user', {'allusers': User.objects.all()})
#         return JsonResponse({"msg":"Left Device Off",}, status=200)
#     else:
#         device.power_left=True
#         device.save()
#         return JsonResponse({"msg":"Left Device On",}, status=200)

def send_device_via_mail(request):
    
    try:
        if request.method == "POST":
            id = request.POST.get("id")
            device = AddDevice.objects.get(id=id)
            subject = str(device.id) + " Information"
            html_message = render_to_string('email/deviceinfo.html', {'device': device})
            plain_message = strip_tags(html_message)
            email_from = settings.EMAIL_HOST_USER
            email_to = [email_from,]
            send_mail(subject=subject,message=plain_message, html_message=html_message, from_email=email_from, recipient_list=email_to)
            return JsonResponse({"msg":"Mail Sent",}, status=200)

            # return HttpResponse("Open Datacenter "+str(id))
    except Exception as e:
        db_logger.exception(e)
        print("Error: "+str(e))

@login_required(redirect_field_name=None)
@permission_required("dashboard.view_settings" , "/noperm/")
def showUser(request):
    try:
        all_users= User.objects.all()
        context= {'allusers': all_users}
        return render(request, 'dashboard/show_user.html', context)
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/show_user.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
@login_required(redirect_field_name=None)
@permission_required("dashboard.add_settings" , "/noperm/")
def changeStatus(request, id):
    # user = User.objects.filter(id=id).update(is_active=True)
    try:
        user = User.objects.get(id=id)
        if user.is_active:
            user.is_active=False
            user.save()
            return redirect('/show/user', {'allusers': User.objects.all()})
        else:
            user.is_active=True
            user.save()
            return redirect('/show/user', {'allusers': User.objects.all()})
        # return render(request, 'dashboard/show_user.html')
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/show_user.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
@csrf_exempt
@permission_required("dashboard.view_settings" , "/noperm/")
def changeUserType(request):
    try:
        id = int(request.POST.get("id"))
        staff_type = request.POST.get("type")
        profile = UserProfile.objects.get(id=id)
        current_type = profile.staff_type
        profile.staff_type = staff_type.upper()
        profile.save()
        return JsonResponse({"data":"Type Changed from {} to {}".format(current_type, staff_type)})
    except Exception as err:
        return JsonResponse({"data":str(err)})


def create_resource(modelName):
    class model_resource(resources.ModelResource):
        class Meta:
           model = modelName
    return model_resource()
@login_required(redirect_field_name=None)
def importEx(request):
    app_models = [model.__name__ for model in apps.get_models()][:-5]
    msg = ""
    if request.method == 'POST':
        
        try:
            file_format = request.POST['file-format']
            modelName = request.POST['modelName'].lower()
            
            myModel = apps.all_models['dashboard'][modelName]

            dataset = Dataset()
            data = request.FILES['importData']

            # resource = GlobalResource(myModel)
            resource = create_resource(myModel)
            if file_format == 'CSV':
                imported_data = dataset.load(data.read().decode('utf-8'),format='csv')
                res = resource.import_data(dataset, dry_run=True, raise_errors=True)                                                                 
            elif file_format == 'JSON':
                imported_data = dataset.load(data.read().decode('utf-8'),format='json')
                # Testing data import
                res = resource.import_data(dataset, dry_run=True, raise_errors=True) 

            if not res.has_errors():
                # Import now
                resource.import_data(dataset, dry_run=False)
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/import.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

    return render(request, 'dashboard/import.html',{'AllModels':app_models, 'msg':msg})


@login_required(redirect_field_name=None)
@csrf_exempt
def exportData(request):
    app_models = [model.__name__ for model in apps.get_models()][:-5]
    if request.method == 'POST':
        try:
            # Get selected option from form
            modelName = request.POST["name"].lower()
            file_format = request.POST["format"]

            myModel = apps.all_models['dashboard'][modelName]
            # dataset = Dataset()
            # data = request.FILES['importData']

            resource = create_resource(myModel)
            dataset = resource.export()
            if file_format == 'CSV':
                response = HttpResponse(json.dumps(dataset.csv), content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="'+modelName+'.csv"'
                return response        
            elif file_format == 'JSON':
                response = HttpResponse(json.dumps(dataset.json), content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="'+modelName+'.json"'
                return response
            # elif file_format == 'XLS (Excel)':
            #     response = HttpResponse(json.dumps(dataset.xls), content_type='application/vnd.ms-excel')
            #     response['Content-Disposition'] = 'attachment; filename="'+modelName+'.xls"'
            #     return response   
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/export.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
    else:
        pass# Returns a "list" of all models created
        # print(app_models)

    return render(request, 'dashboard/export.html',{'AllModels':app_models})


# class dataBrowser(View):
#     def get (self,request):
#         return render(request,'dashboard/db.html')


# @login_required(redirect_field_name=None)
class GP(View):
    
    @method_decorator(permission_required("dashboard.view_settings" , "/noperm/"))
    def get(self,request):
        try:
            all_group=Group.objects.all()
            # all_page=PagePermissionForGroup.objects.all()
            return render(request,'dashboard/groups.html',{"all_group":all_group})
                # return HttpResponse("this ")
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/groups.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
    
    @method_decorator(permission_required("dashboard.add_settings" , "/noperm/"))
    def post(self, request):
        try:
            all_group=Group.objects.all()
            # all_page=PagePermissionForGroup.objects.all()

            msg = ""

            data = {key:request.POST[key].strip() for key in request.POST if not key == "csrfmiddlewaretoken"}
            all_change = []
            p = request.POST.getlist('permission')
            string_search = "dashboard.add_"
            all_add = [x for x in p if x.startswith(string_search)]
            all_change += [x.replace('.add_', '.change_') for x in all_add]
            p = all_change + p
            # page_data={key:request.POST[key].strip() for key in request.POST if not key =="csrfmiddlewaretoken"}
                
            if "creategroup" in data:
                if Group.objects.filter(name=data['creategroup']).count():
                    # return HttpResponse("group already taken please write another name")
                    return render(request,'dashboard/groups.html',{"all_group":all_group, 'msg':'group already taken please write another name'})
                    
                else:
                    groupname, created=Group.objects.update_or_create(name=data['creategroup'])
                    # return HttpResponse("group created successfully")
                    return render(request,'dashboard/groups.html',{"all_group":all_group, 'msg':'group created successfully'})
                
            if "groupname" in data:
                
                group_django = Group.objects.get(name=data['groupname'])
                perm_set = Permission.objects.values("codename","id")
                perm_ids = []

                for i in perm_set:
                    for perm in p:
                        if perm.split(".")[1] in i["codename"]:
                            perm_ids.append(i["id"])
                    
                group_django.permissions.set(perm_ids)
                # page_group = PagePermissionForGroup.objects.filter(name_of_page=data['pagename'])

                # updated = page_group.update(read_perm=data.get("read_perm",False),
                # write_perm=data.get("write_perm",False),delete_perm=data.get("delete_perm",False),
                # update_perm=data.get("update_perm",False),patch_perm=data.get("patch_perm",False),
                # all_perm=data.get("all_perm",False))

                # if updated:
                #     # return HttpResponse("Page Permissions are also set")
                #     return render(request,'dashboard/groups.html',{"all_perm":all_perm,"perm_count":perm_count,"all_group":all_group, 'msg':'Page Permissions are also set'})
                # # return HttpResponse("Only Models Permissions Set")
                return render(request,'dashboard/groups.html',{"all_group":all_group,'msg':'Permissions Set'})
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/groups.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
@csrf_exempt
@login_required(redirect_field_name=None)
@permission_required("dashboard.view_settings" , "/noperm/")
def getUserPermission(request):
    all_group=Group.objects.all()
    if request.method == 'POST':        
        all_p = []
        try:
            models = [AssetPage,NetworkSummary,ServerSummary,DatabaseSummary,StorageSummary,CCTV,WebMonitoring,Reports,APM,Settings,Dashboard,Appliance]      
            for model in models:      
                content_type = ContentType.objects.get_for_model(model)
                post_permission = Permission.objects.filter(content_type=content_type)
                all_p += ["dashboard."+perm.codename for perm in post_permission]
            user_name = request.POST.get('user')
            a=Group.objects.get(name=user_name)
            a_all=a.permissions.all()
            # return render(request, 'dashboard/test_badal.html', context={"a_all":a_all,"all_group":all_group})
            return JsonResponse({"a_all":list(a_all.values()), "all_p":all_p})
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/test_badal.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
    return render(request, 'dashboard/test_badal.html', context={'all_group':all_group})
@login_required(redirect_field_name=None)
@permission_required("dashboard.view_settings" , "/noperm/")
def assignGroup(request):
    msg=""
    all_group=Group.objects.all()
    all_user=User.objects.all()
    if request.method == 'POST':
        group = request.POST.get('group')
        user = request.POST.get('user')
        get_group = Group.objects.get(name=group)
        get_group.user_set.add(user)
        msg = "successfully added"
    return render(request, 'dashboard/test_badal_p2.html', context={'all_group':all_group, 'all_user':all_user,'msg':msg})
# @login_required(redirect_field_name=None)
# def fun1(request):
#     form = PagePermissionForGroupForm()
#     msg=""
#     if request.method == "POST":
#         new_form = PagePermissionForGroupForm(request.POST)
#         if new_form.is_valid():
#             new_form.save()
#             msg = "Successs"
#     return render(request,'dashboard/test_badal_p3.html', context={'form':form, 'msg':msg})


@login_required(redirect_field_name=None)
def temp(request):
    return render(request, "dashboard/tempview.html")





@login_required(redirect_field_name=None)
@permission_required("dashboard.view_settings" , "/noperm/")
def setting(request):
    return render(request,"dashboard/setting.html")

@login_required(redirect_field_name=None)
@permission_required("dashboard.view_settings" , "/noperm/")
def AdminSetting(request):
    return render(request,"dashboard/admin_settings.html")

@permission_required("dashboard.view_settings" , "/noperm/")
def AdminGroup(request):
    return render(request,"dashboard/admin_groups.html")
    
@permission_required("dashboard.view_settings" , "/noperm/")
def AdminIO(request):
    return render(request,"dashboard/admin_bulkio.html")

@permission_required("dashboard.view_settings" , "/noperm/")
def AdminServices(request):
    is_blink = DeviceSetting.objects.get(id=1)
    data = {
        'is_blink': is_blink.is_blink,
    }
    return render(request,"dashboard/admin_services.html", data)

@permission_required("dashboard.add_settings" , "/noperm/")
def changeBlinkStatus(request):
    current = DeviceSetting.objects.get(id=1)
    if current.is_blink:
        current.is_blink = False
    else:
        current.is_blink = True
    current.save()
    return JsonResponse({
        'status':current.is_blink
    })
def fetch_notifications(request):
    try:
        data = Notif.objects.filter(is_read=False, is_delete=False).order_by("-date").values()
        count = data.count()
        is_blink = DeviceSetting.objects.get(id=1)
        return JsonResponse({
            'err':False,
            'is_blink':is_blink.is_blink,
            'count':count,
            'data':list(data)
        })
    except Exception as err:
        return JsonResponse({
            'err':True,
            'data':str(err)
        })


@login_required(redirect_field_name=None)
def all_notifications(request):
    if request.method == "POST":
        oper = request.POST.get("bulkoper")
        start = int(request.POST.get("start"))
        end = int(request.POST.get("end"))
        # print(oper, start, end)
        if oper == "read":
            try:
                for i in range(start, end+1):
                    obj = Notif.objects.get(id = i)
                    obj.is_read = True
                    obj.save()
            except Exception as err:
                pass
        if oper == "delete":
            try:
                for i in range(start, end+1):
                    obj = Notif.objects.get(id = i)
                    obj.is_delete = True
                    obj.save()
            except Exception as err:
                pass
    times = []
    data = Notif.objects.filter(is_delete=False)

    for datas in data:
        times.append(datas.date.strftime("%m/%d/%Y %H:%M"))

    page = request.GET.get('page', 1)
    filter = request.GET.get('type', "unread")
    
    if filter == "unread":
        notif = data.filter(is_read = False).order_by("-date")
    elif filter == "read":
        notif = data.filter(is_read = True).order_by("-date")
    else:
        notif = data

    paginator = Paginator(notif, 50)
    try:
        data_page = paginator.page(page)
    except PageNotAnInteger:
        data_page = paginator.page(1)
    except EmptyPage:
        data_page = paginator.page(paginator.num_pages)

    lSeverity = data.filter(severity = 'low').count()
    mSeverity = data.filter(severity = 'medium').count()
    hSeverity = data.filter(severity = 'high').count()

    WebMonitoringData = data.filter(content__icontains = 'Response').count()

    cpuUsage = data.filter(content__icontains = 'CPU').count()
    cpuTemp = data.filter(content__icontains = 'Temerature').count()
    Ram = data.filter(content__icontains = 'RAM').count()
    Swap = data.filter(content__icontains = 'SWAP').count()
    Storage = data.filter(content__icontains = 'Storage').count()
    IOwait = data.filter(content__icontains = 'IOWAT').count()
    applianceData = cpuUsage+cpuTemp+Ram+Swap+Storage+IOwait
    dashboardData = data.filter(parent__icontains = 'snmp').count()
    # print(lSeverity, mSeverity, hSeverity, WebMonitoringData, applianceData,dashboardData)
    # websites = WebsiteLinks.objects.all()
    websites = []
    for d in data.filter(content__icontains = 'Response Time for htt'):
        name = d.title.split("Response Time for ")[1]
        websites.append(name)
    
    context = {

        # 
    'cpuUsage':cpuUsage,
    'cpuTemp':cpuTemp,
    'Ram':Ram,
    'Swap':Swap,
    'Storage':Storage,
    'IOwait':IOwait,
    'data':data_page,
    'low':lSeverity,
    'med':mSeverity,
    'high':hSeverity,

    'webname':list(Counter(websites).keys()),
    'webnameoccu':list(Counter(websites).values()),

    'times':list(Counter(times).keys()),
    'datas':list(Counter(times).values()),

    'web':WebMonitoringData,
    'appliance':applianceData,
    'dashboard':dashboardData,
    }
    return render(request, 'dashboard/notifications.html', context)

@login_required(redirect_field_name=None)
def notification_update(request):
    try:
        id = int(request.POST.get("id"))
        # print(id)
        id = Notif.objects.get(id=id)
        id.is_read=True
        id.save()
        obj = Notif.objects.filter(is_delete=False, is_read=False)
        return JsonResponse({
            'err': False,
            'count': obj.count(),
            'data': list(obj.order_by("-date")[:5].values())
        })
        # return redirect(path)
    except Exception as err:
        print(str(err))
        return JsonResponse({
            'err': True,
        })

@login_required(redirect_field_name=None)
def notification_read(request,id):
    path = request.META['HTTP_REFERER']
    id = Notif.objects.get(id=id)
    id.is_read=True
    id.save()
    return redirect(path)

@login_required(redirect_field_name=None)
def notification_delete(request,id):
    path = request.META['HTTP_REFERER']
    id = Notif.objects.get(id=id)
    id.is_delete=True
    id.save()
    return redirect(path)


######### menu functionality ############    




@login_required(redirect_field_name=None)
def genearte_raw_data_report(request,id=id):
    if request.user.is_authenticated:
        user = User.objects.filter(email=request.user.email)
        for data in user:
            import csv
            from fpdf import FPDF
            df = pd.read_csv('dashboard/extraFiles/sample_data.csv',
                                header=None, skiprows=3)
            result = df.to_html(classes='table table-striped')

            with open('dashboard/extraFiles/sample_data.csv', newline='') as f:
                reader = csv.reader(f)

                pdf = FPDF()
                pdf.add_page()
                page_width = pdf.w - 2 * pdf.l_margin

                pdf.set_font('Times', 'B', 14.0)
                pdf.cell(page_width, 0.0, 'Sample Data', align='C')
                pdf.ln(10)

                pdf.set_font('Courier', '', 12)

                col_width = page_width / 4

                pdf.ln(1)

                th = pdf.font_size

                for row in reader:
                    # print(len(row))
                    pdf.cell(col_width, th, str(row[0]), border=1)
                    pdf.cell(col_width, th, row[1], border=1)
                    pdf.cell(col_width, th, row[2], border=1)

                    pdf.ln(th)

                pdf.ln(10)

                pdf.set_font('Times', '', 10.0)
                pdf.cell(page_width, 0.0, '- end of report -', align='C')

                pdf.output(name='dashboard/extraFiles/sample.pdf')
                report = pdf.output(dest='S').encode('latin-1')
                response  = HttpResponse(report,content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
                return  response



                return render(request,'dashboard/reports.html')
        else:
            return HttpResponse('Sorry , You do not have access rights to this page. Kindly login as admin .')

    else:
        return redirect('/')

# @login_required(redirect_field_name=None)
# def rack_report(request):
#     from django.template.loader import get_template
#     from weasyprint import HTML
#     from django.http import HttpResponse

#     html_template = get_template('dashboard/check.html').render()
#     pdf_file = HTML(string=html_template).write_pdf()
#     response = HttpResponse(pdf_file, content_type='application/pdf')
#     response['Content-Disposition'] = 'filename="home_page.pdf"'
#     return response
#     return render(request,'dashboard/reports.html')



@login_required(redirect_field_name=None)
def apmReport(request):
    return render(request,'dashboard/apm_report.html')



def mail(request):
    return render(request,'dashboard/mail.html')


@login_required(redirect_field_name=None)
def aboutUs(request):
    return render(request,'dashboard/aboutUs.html') 

@login_required(redirect_field_name=None)
def dataReview(request):
    return render(request,'dashboard/dataReview.html') 
def dataReviewAjax(request):
    # print("Enter")
    if request.method == "POST": 
        try:
            data = {key:value.strip() for key, value in request.POST.items()}
            # print(data)
            index = data["filter"]
            value = data["value"]
            if value == "":
                obj = AddDevice.objects.filter(is_delete=False).values()
            else:
                if index == 'device':
                    obj = AddDevice.objects.filter(Device_Asset_Tag__icontains=value, is_delete=False).values()
                else:
                    fullIP = value.split(".")
                    obj = AddDevice.objects.filter(IP_Address_col1=int(fullIP[0]),IP_Address_col2=int(fullIP[1]),IP_Address_col3=int(fullIP[2]),IP_Address_col4=int(fullIP[3]),is_delete=False).values()
            if obj.count() == 0:
                return JsonResponse({
                'data':None,
                'count':obj.count()
            }) 
            context = list(obj)
            return JsonResponse({
                'data':context,
                'count':obj.count()
            }) 
        except Exception as err:
            return JsonResponse({
                'data':None,
                'count':0
            }) 
@login_required(redirect_field_name=None)
def dataCheck(request):
    ip = request.GET.get("ip" , None)
    data = {}
    if ip == None or ip == "":
        data["type"] = "appliance"
        obj = DeviceSetting.objects.get(id=1)
    else:
        data["type"] = "device"
        try:
            obj = SnmpDeviceSetting.objects.get(ip=ip)
        except:
            obj = SnmpDeviceSetting.objects.create(ip=ip)

    data["settings"] = obj
    
    return render(request,'dashboard/dataCheck.html',data) 
@csrf_exempt
def devicesetting(request):
    types = request.POST.get("type","")
    ip = request.POST.get("ip",None)
    value = request.POST.get("value","")
    deviceType = request.POST.get("devicetype" , "appliance")
    if deviceType == "appliance":
        obj = DeviceSetting.objects.get(id=1)
    else:
        obj = SnmpDeviceSetting.objects.get(ip=ip)

    if value != "reset":
        if types == "cpu":
            obj.cpu_threshold = value
            newValue = value
        if types == "ram":
            obj.usedRam = value
            newValue = value
        if types == "swap":
            obj.usedSMemory = value
            newValue = value
        if types == "storage":
            obj.usedStorage = value
            newValue = value
        if types == "iowait":
            obj.iowait = value
            newValue = value
        if types == "temp":
            obj.temperature = value
            newValue = value
        obj.save()

    if value == "reset":
        if types == "cpu":
            obj.cpu_threshold = obj._meta.get_field('cpu_threshold').get_default()
            newValue = obj._meta.get_field('cpu_threshold').get_default()
        if types == "ram":
            obj.usedRam = obj._meta.get_field('usedRam').get_default()
            newValue = obj._meta.get_field('usedRam').get_default()
        if types == "swap":
            obj.usedSMemory = obj._meta.get_field('usedSMemory').get_default()
            newValue = obj._meta.get_field('usedSMemory').get_default()
        if types == "storage":
            obj.usedStorage = obj._meta.get_field('usedStorage').get_default()
            newValue = obj._meta.get_field('usedStorage').get_default()
        if types == "iowait":
            obj.iowait = obj._meta.get_field('iowait').get_default()
            newValue = obj._meta.get_field('iowait').get_default()
        if types == "temp":
            obj.temperature = obj._meta.get_field('temperature').get_default()
            newValue = obj._meta.get_field('temperature').get_default()
        obj.save()
    return JsonResponse({
        'data':str(types)+" threshold changed",
        "value":newValue
    })

@login_required(redirect_field_name=None)
def contactUs(request):
    
    try:
        user = User.objects.get(username=request.user)
        msg = ""
        # print(user)
        if request.method == "POST":
            data = {key:request.POST[key].strip() for key in request.POST if not key == "csrfmiddlewaretoken"}
            contact = ContactUs(fname = data["firstname"], lname=data["lastname"], email=data.get("email",""), msg=data["subject"])
            contact.save()
            msg = "Thank you for contacting us"
        
        return render(request,'dashboard/contactUs.html',{'user':user,'msg':msg}) 
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/contactUs.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

@login_required(redirect_field_name=None)
def raiseTicket(request):
    try:
        # if request.user.is_superuser: # just using request.user attributes
        #     allTicket = RaiseTicket.objects.all()
        #     return render(request,'dashboard/raiseTicketadmin.html',{'allTicket':allTicket})
        # else:
        allTicket = RaiseTicket.objects.all()
        user = User.objects.get(username=request.user)
        msg = ""
        id = int(request.GET.get("id",-1))

        title = request.GET.get('title','')
        content = request.GET.get('content','')
        extradata = {'subject':title, 'message':content}
        myTicket = RaiseTicket.objects.filter(user=user)
        # print(extradata)
        if request.method == "POST":

            emails = request.POST.get("sendemail","")
            emails = emails.split(",")
            for email in emails:
                print("Send mail to", email) #send Mail to these emails send_mail(emails)
            ticket = RaiseTicketForm(request.POST, request.FILES)
            if ticket.is_valid():
                instance = ticket.save(commit=False)
                instance.user = request.user
                instance.save()
                if id != -1:
                    notif = Notif.objects.get(id=id)
                    notif.is_raised = True
                    notif.save()
                msg = "Thank you for raising a ticket"
            return redirect('/raiseticket/')
        else:
            ticket = RaiseTicketForm()
        return render(request,'dashboard/raiseTicket.html',{'user':user,'msg':msg, 'ticket':ticket,'myTicket':myTicket, 'extradata':extradata,'allTicket':allTicket}) 
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/raiseTicket.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

@login_required(redirect_field_name=None)
def viewRaiseTicket(request, id):    
    try:
        ticket = RaiseTicket.objects.get(id=id)
        assigni = None
        if ticket.assigned_to:
            if request.user == ticket.assigned_to:
                assigni = User.objects.get(id = ticket.assigned_to.id)
            else:
                print("No one is assigned")
        if request.user.is_superuser: # just using request.user attributes
            users = User.objects.all()
            msg = ""
            if request.method == "POST":
                data = {key:request.POST[key].strip() for key in request.POST if not key == "csrfmiddlewaretoken"}
                # print(data)
                ticket = RaiseTicket.objects.get(id=id)
                ticket.admin_response = data.get("admin_response","")
                try:
                    ticket.assigned_to = User.objects.get(id = data.get("assigned_to",""))
                except Exception:
                    ticket.assigned_to = None
                if data["aprove"] == 'aproved':
                    ticket.is_aprove = True
                else:
                    ticket.is_aprove = False
                ticket.accepted = True
                ticket.updated = datetime.now()
                ticket.save()
            return render(request,'dashboard/viewRaiseTicket.html',{'ticket':ticket,'is_admin':True, 'users':users, 'assigni':assigni}) 
        else:
            if request.method == "POST":
                data = {key:request.POST[key].strip() for key in request.POST if not key == "csrfmiddlewaretoken"}
                # print(data)
                # ticket = RaiseTicket.objects.get(id=id)
                ticket.admin_response = data.get("admin_response","")
                # ticket.assigned_to = User.objects.get(id = data.get("assigned_to",""))
                # if data["aprove"] == 'aproved':
                #     ticket.is_aprove = True
                # else:
                #     ticket.is_aprove = False
                # ticket.accepted = True
                ticket.updated = datetime.now()
                ticket.save()
            return render(request,'dashboard/viewRaiseTicket.html',{'ticket':ticket,'assigni':assigni}) 
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/viewRaiseTicket.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

@login_required(redirect_field_name=None)
def AssignedTicket(request):
    try:
        allTicket = RaiseTicket.objects.filter(assigned_to = request.user)
        # print(request.user,allTicket)
        return render(request,'dashboard/assignTicketadmin.html',{'allTicket':allTicket})
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/assignTicketadmin.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
@csrf_exempt
def favTopology(request):
    type = request.POST.get("type", "topo2")
    topo = Topology.objects.get(id = 1)
    topo.type = type
    topo.save()
    return JsonResponse({"msg": "Marked as default topology"})
# @login_required(redirect_field_name=None)
def topology(request):
    try:
        type = Topology.objects.get(id = 1)
    except:
        Topology.objects.create(id = 1)
        type = Topology.objects.first()

    if type.type == "topo1":
        mainFunction()
        return render(request, "dashboard/topology.html")
    elif type.type == "topo2":
        data = {}
        datacenter = addDataCenter.objects.all()
        for dc in datacenter:
            dcName = dc.dataCenterTag.replace(" ", "_")
            data[dcName] = {}
            devices = AddDevice.objects.filter(datacenter=dc)
            for device in devices:
                type = device.type_of_device
                thistype = device.network_device_category
                category = device.network_sub_category
                ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)            
                if type not in data[dcName]:
                    data[dcName][type] = []
                data[dcName][type].append({"ip":ip, "status":scan(ip), "thistype":thistype, "category":category})
        data = {"data": getProperResponse(data)}
        return render(request, "topology.html", data)
    elif type.type == "topo4":
        data = {}
        datacenter = DeviceCapibility.objects.all()
        for dc in datacenter:
            try:
                dcName = dc.ip
                data[dcName] = {}
                devices = AddDevice.objects.filter(type_of_device="wlc") # wsl
                temp = getDetails(None, dc.ip, dc.commString)
                # AP = temp["AP"]
                AP = temp["interfaces"]
                count = 0
                for ap in AP:            
                    # type = AP[ap]["ssid"]
                    type = AP[ap]["name"]
                    ip = count
                    # adminstatus = AP[ap]["bsnAPAdminStatus"]

                    if type not in data[dcName]:
                        data[dcName][type] = []  
                    # if adminstatus not in data[dcName]:
                    #     data[dcName][adminstatus] = []  
        
                    data[dcName][type].append(ip) 
                    # data[dcName][adminstatus].append(adminstatus)
                    count += count
            except:
                pass
            # for device in devices:
            #     type = str(count) # interfaces
            #     ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)            
            #     if type not in data[dcName]:
            #         data[dcName][type] = []            
            #     data[dcName][type].append(ip)
            #     count += count
        data = {"data": getProperResponseWSL(data)}
        print(data)
        return render(request, "wsl.html", data)
    elif type.type == "topo5":
        data = {}
        datacenter = addDataCenter.objects.all()
        for dc in datacenter:
            dcName = dc.dataCenterTag.replace(" ", "_")
            data[dcName] = {}
            devices = AddDevice.objects.filter(datacenter=dc)
            for device in devices:
                type = device.type_of_device
                ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)            
                if type not in data[dcName]:
                    data[dcName][type] = []
                data[dcName][type].append({"ip":ip, "status":True})
        data = {"data": getProperResponseSan(data)}
        return render(request, "sankey.html", data)
    else:
        data = {}
        datacenter = addDataCenter.objects.all()
        for dc in datacenter:
            dcName = dc.dataCenterTag.replace(" ", "_")
            data[dcName] = {}
            devices = AddDevice.objects.filter(datacenter=dc)
            for device in devices:
                type = device.type_of_device
                ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)    
                if type not in data[dcName]:
                    data[dcName][type] = []
                status = False
                thistype = device.network_device_category
                category = device.network_sub_category
                try:
                    dc = DeviceCapibility.objects.get(ip = ip)
                except:
                    continue
                response = getDetails(request = None , host = dc.ip , communityStr = dc.commString)
                if response != False:
                    status = True
                
                if dc.snmpv3user:
                    status = snmpv3checker(dc.ip, dc.snmpv3user, dc.snmpv3auth, dc.snmpv3pass)
                    print(status)
                data[dcName][type].append({"ip":ip, "status":status, "thistype":thistype, "category":category})
        data = {"data": makeConnections(data)}
        return render(request, "topology3.html", data)

def topology1(request):
    mainFunction()
    return render(request, "dashboard/topology.html")

def topology2(request):
    data = {}
    datacenter = addDataCenter.objects.all()
    for dc in datacenter:
        dcName = dc.dataCenterTag.replace(" ", "_")
        data[dcName] = {}
        devices = AddDevice.objects.filter(datacenter=dc)
        for device in devices:
            type = device.type_of_device
            thistype = device.network_device_category
            category = device.network_sub_category
            ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)            
            if type not in data[dcName]:
                data[dcName][type] = []
            data[dcName][type].append({"ip":ip, "status":scan(ip), "thistype":thistype, "category":category})
    data = {"data": getProperResponse(data)}
    return render(request, "topology.html", data)

def topology5(request): #Sankey
    data = {}
    datacenter = addDataCenter.objects.all()
    for dc in datacenter:
        dcName = dc.dataCenterTag.replace(" ", "_")
        data[dcName] = {}
        devices = AddDevice.objects.filter(datacenter=dc)
        for device in devices:
            type = device.type_of_device
            ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)            
            if type not in data[dcName]:
                data[dcName][type] = []
            data[dcName][type].append({"ip":ip})
    data = {"data": getProperResponseSan(data)}
    return render(request, "sankey.html", data)

def topology3(request):
    data = {}
    datacenter = addDataCenter.objects.all()
    try:
        for dc in datacenter:
            dcName = dc.dataCenterTag.replace(" ", "_")
            data[dcName] = {}
            devices = AddDevice.objects.filter(datacenter=dc)
            for device in devices:
                type = device.type_of_device
                ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)    
                if type not in data[dcName]:
                    data[dcName][type] = []
                status = False
                thistype = device.network_device_category
                category = device.network_sub_category
                try:
                    dc = DeviceCapibility.objects.get(ip = ip)
                except:
                    continue
                response = getDetails(request = None , host = dc.ip , communityStr = dc.commString)
                if response != False:
                    status = True
                
                if dc.snmpv3user:
                    status = snmpv3checker(dc.ip, dc.snmpv3user, dc.snmpv3auth, dc.snmpv3pass)
                    print(status)
                data[dcName][type].append({"ip":ip, "status":status, "thistype":thistype, "category":category})
    except Exception as err:
        data = {
            "title":"Page Can't be opened",
            "helping_text":str(err),
            "result":"Devices taking long time to respond",
        }
        return render(request, "dashboard/message_page.html", data)
    data = {"data": makeConnections(data)}
    return render(request, "topology3.html", data)

    # data = {"data": makeConnections(data)}
    # return render(request, "topology3.html", data)

def wsl(request):
    data = {}
    datacenter = DeviceCapibility.objects.all()
    for dc in datacenter:
        try:
            devices = AddDevice.objects.filter(type_of_device="wlc") # wsl
            for d in devices:
                ipA = str(d.IP_Address_col1) + "." + str(d.IP_Address_col2) + "." + str(d.IP_Address_col3) + "." + str(d.IP_Address_col4)
                if dc.ip == ipA:
                    dcName = dc.ip
                    data[dcName] = {}
                    temp = getDetails(None, dc.ip, dc.commString)
                    AP = temp["AP"]
                    # AP = temp["interfaces"]
                    count = 0
                    for ap in AP:            
                        type = AP[ap]["ssid"]
                        # type = AP[ap]["name"]
                        ip = count
                        # adminstatus = AP[ap]["bsnAPAdminStatus"]

                        if type not in data[dcName]:
                            data[dcName][type] = []  
                        # if adminstatus not in data[dcName]:
                        #     data[dcName][adminstatus] = []  
            
                        data[dcName][type].append(ip) 
                        # data[dcName][adminstatus].append(adminstatus)
                        count += count
        except:
            pass
        # for device in devices:
        #     type = str(count) # interfaces
        #     ip = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)            
        #     if type not in data[dcName]:
        #         data[dcName][type] = []            
        #     data[dcName][type].append(ip)
        #     count += count
    data = {"data": getProperResponseWSL(data)}
    return render(request, "wsl.html", data)

def makeConnections(data):
    output = {"nodes": [], "links": []}

    for dc in data:
        output["nodes"].append({"id": dc, "name": dc, "type": "datacenter"})

        if (data[dc]):
            output["nodes"].append({"id" : dc + "network" , "name" : dc + "network" , "type" : "snmp"})
            output["links"].append({"source" : dc + "network" , "target" : dc , "type" : "snmp"})
        
        
        
        for type in data[dc]:
            if type == "Network" or type == "Server" or type == "wlc" or type == "Storage" or type == "Blade Chassis":
                for ip in data[dc][type]:
                    output["nodes"].append({"id" : ip["ip"] , "name" : ip["ip"] , "type" : type.lower(), "subtype":ip["thistype"], "category": ip["category"]})
                    output["links"].append({"source" : dc + "network" , "target" : ip["ip"] , "type" : type.lower(),"status": ip["status"]})

        
    lastDC = None
    for node in output["nodes"]:
        if node["type"] == "datacenter":
            if lastDC != None:
                output["links"].append({"source" : node["id"] , "target" : lastDC["id"] , "type" : "datacenter"}) 
            lastDC = node

    if lastDC != None:
        output["links"].append({"source" : lastDC["id"] , "target" : output["nodes"][0]["id"] , "type" : "datacenter"})
    # print(output)
    return output
    
def getProperResponseSan(data):
    output = {"nodes": [], "links": []}
    for dc in data:
        if data[dc]:
            output["nodes"].append({"id": dc, "name": dc, "type": "datacenter"})

        for type in data[dc]:
            count = len(data[dc][type])
            if type == "Network" or type == "Server" or type == "wlc" or type == "Storage" or type == "Blade Chassis":
                output["nodes"].append({"id" : dc + type.lower() , "name" : dc + type.lower() , "type" : type+"type"})
                output["links"].append({"target" : dc + type.lower() , "source" : dc , "type" : type+"type","value":count})   
                for ip in data[dc][type]:
                    output["nodes"].append({"id" : ip["ip"] , "name" : ip["ip"] , "type" : type.lower()})
                    output["links"].append({"source" : dc + type.lower() , "target" : ip["ip"] , "type" : type.lower(),"value":count+1})

        
    # lastDC = None
    # for node in output["nodes"]:
    #     if node["type"] == "datacenter":
    #         if lastDC != None:
    #             output["links"].append({"target" : node["id"] , "source" : lastDC["id"] , "type" : "datacenter"}) 
    #         lastDC = node

    # if lastDC != None:
    #     output["links"].append({"target" : lastDC["id"] , "source" : output["nodes"][0]["id"] , "type" : "datacenter"})
    return output

def getProperResponse(data):
    output = {"nodes": [], "links": []}

    output["nodes"].append({"id": "cloud", "name": "cloud", "type": "cloud"})
    
    for dc in data:
        output["nodes"].append({"id": dc, "name": dc, "type": "datacenter"})

        # output["nodes"].append({"id" : dc + "network" , "name" : dc + "network" , "type" : "networktype"})
        # output["nodes"].append({"id" : dc + "server" , "name" : dc + "server" , "type" : "servertype"})

        output["links"].append({"source" : dc , "target" : "cloud" , "type" : "cloudtype"}) 
        # output["links"].append({"source" : dc + "network" , "target" : dc , "type" : "networktype"}) 
        # output["links"].append({"source" : dc + "server" , "target" : dc , "type" : "servertype"}) 
        
        
        
        for type in data[dc]:
            if type == "Network" or type == "Server" or type == "wlc" or type == "Storage" or type == "Blade Chassis":
                output["nodes"].append({"id" : dc + type.lower() , "name" : dc + type.lower() , "type" : type.lower()+"type"})
                output["links"].append({"source" : dc + type.lower() , "target" : dc , "type" : type.lower()+"type"}) 
                for ip in data[dc][type]:
                    output["nodes"].append({"id" : ip["ip"] , "name" : ip["ip"] , "type" : type.lower(),"subtype":ip["thistype"], "category": ip["category"]})
                    output["links"].append({"source" : dc + type.lower() , "target" : ip["ip"] , "type" : type.lower(),"status": ip["status"]}) 
                # else:
                #     output["links"].append({"source" : dc + "server" , "target" : ip["ip"] , "type" : type.lower(),"status": ip["status"]})

        
    lastDC = None
    for node in output["nodes"]:
        if node["type"] == "datacenter":
            if lastDC != None:
                output["links"].append({"source" : node["id"] , "target" : lastDC["id"] , "type" : "datacenter"}) 
            lastDC = node

    if lastDC != None:
        output["links"].append({"source" : lastDC["id"] , "target" : output["nodes"][0]["id"] , "type" : "datacenter"})
    return output

def getProperResponseWSL(data):
    # print(data)
    output = {"nodes": [], "links": []}

    for dc,v in data.items():
        output["nodes"].append({"id": dc, "name": dc, "type": "wlc"})

        for val in v:
                output["nodes"].append({"id" : dc+val , "name" : dc+val , "type" : val})
                output["links"].append({"source" : dc+val , "target" : dc , "type" : val}) 
            # break

        
    lastDC = None
    for node in output["nodes"]:
        # print(node)
        if node["type"] == "wlc":
            if lastDC != None:
                output["links"].append({"source" : node["id"] , "target" : lastDC["id"] , "type" : "wlc"}) 
            lastDC = node

    if lastDC != None:
        output["links"].append({"source" : lastDC["id"] , "target" : output["nodes"][0]["id"] , "type" : "wlc"}) 

    return output

@login_required(redirect_field_name=None)
def table(request):
    data = {}
    device = DeviceCapibility.objects.filter(is_snmp = True, is_fav=True)
    for d in device:
        data[d.ip] = {
            "url" : d.ip,
            "string": d.commString
        }
        
    print(data)
    return render(request,"dashboard/table.html",{"data":data})

@login_required(redirect_field_name=None)
def individualDashboard(request, ip, str):
    device = DeviceCapibility.objects.get(ip = ip)
    commStr = device.commString
    # print(device)
    return render(request,"dashboard/individualDashboard.html",{"device":device.ip, "str":commStr})

def get_cpu_temp():
    try:
        if platform.system() == 'Windows':
            return random.randint(0,100)
        else:
            return psutil.sensors_temperatures()['acpitz'][0].current
            # return random.randint(0,100)
    except Exception as e:
        db_logger.exception(e)
        return 0
def getListOfProcessSortedByMemory():
    '''
    Get list of running process sorted by Memory Usage
    '''
    listOfProcObjects = []
    totalPs = len(psutil.pids())
    # Iterate over the list
    # for proc in psutil.process_iter():
    #    try:
    #        # Fetch process details as dict
    #        pinfo = proc.as_dict(attrs=['name'])
    #     #    pinfo['vms'] = proc.memory_info().vms / (1024 * 1024)
    #        totalPs = totalPs + 1
    #        # Append dict to list
    #        listOfProcObjects.append(pinfo)
    #    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
    #        pass
    # Sort list of dict by key vms i.e. memory usage
    # listOfProcObjects = sorted(listOfProcObjects, key=lambda procObj: procObj['vms'], reverse=True)
    return totalPs, [{'name':'ps1','vms':1897},{'name':'ps2','vms':1000},{'name':'ps3','vms':985},{'name':'ps4','vms':984}]
# DAHSBOARD FUNCTIONS
def networkWriteInCV():
    network = pd.read_csv("dashboard/extraFiles/network.csv")
    time = [str(i) for i in list(network['TIME'])]
    download = [float(i) for i in list(network['DOWNLOAD'])]
    upload = [float(i) for i in list(network['UPLOAD'])]
    return time, download, upload
def running_process():
    count = 0
    for proc in psutil.process_iter():
        count = count + 1
    return count
def usage_analytics(user=None):
    total_users = User.objects.count()
    web_websites = WebsiteLinks.objects.count()
    dc = addDataCenter.objects.count()
    notification = Notif.objects.filter(is_read=False, is_delete=False).count()
    # notification = 0
    camera = Product.objects.all().count()
    return total_users, web_websites, dc, notification, camera
def iowatInfo():
    if platform.system() == 'Windows':
        return 0
    else:
        return round(psutil.cpu_times().iowait/1000,1)
def basicInfo():
    try:
        cpuPercentage = psutil.cpu_percent()
        svmem = psutil.virtual_memory() 
        usedRam = round(svmem.used/1024**3,2)
        AvailRam = round(svmem.available/1024**3,2) # RUKO!!!! ok
        totalRam = round(svmem.total/1024**3,2)
        swapMemory = psutil.swap_memory()
        usedSMemory = round(swapMemory.used/(1000000000),2)
        availSMemory = round(swapMemory.free/(1000000000),2)
        hdd = psutil.disk_usage('/')
        totalStorage = round(hdd[0]/(1000000000),2)
        usedStorage = round(hdd[1]/(1000000000),2)
        freeStorage = round(hdd[2]/(1000000000),2)
        return cpuPercentage, usedRam, AvailRam, totalRam, usedSMemory, availSMemory, totalStorage, usedStorage, freeStorage
    except Exception as err:
        return 0,0,0,0,0,0,0,0,0
def engine_core():
    snmp = []
    snmpID = 0
    netconf = []
    netID = 0
    restconf = []
    restID = 0
    DeviceID = []
    deviceCapabilities = DeviceCapibility.objects.all()
    totalDevice = deviceCapabilities.count()
    # print(deviceCapabilities)
    for device in deviceCapabilities:
        if device.is_snmp:
            snmpID = snmpID+3
            snmp.append(snmpID)
        if device.is_netconf:
            netID = netID+4
            netconf.append(netID)
        if device.is_restconf:
            restID = restID+2    # phone swtich off ho gya meraokok charge mai laga diya hai mai lekin anydesk mai hoon 2 m lar duga
            restconf.append(restID)
        DeviceID.append(device.id)
    return snmp, netconf, restconf, DeviceID, totalDevice
def notif_heatmap(user):
    notifTime = []
    low = []
    mid = []
    high = []
    appliance = []
    web = []
    snmp = []
    notifs = Notif.objects.filter(is_delete=False).order_by("-date")
    for n in notifs:
        # notifTime.append(n.date.strftime("%d/%m/%y"))
        # print(n.id, n.parent)
        notifTime.append(n.date.strftime("%d/%m/%y%H:%M:%S"))
        if n.severity == 'high':
            high.append(3)
            mid.append(0)
            low.append(0)
            if (n.parent == "appliance"):
                appliance.append(3)
            if (n.parent == "web"):
                web.append(3)
            if (n.parent == "SNMP"):
                web.append(3)    
        if n.severity == 'medium':
            mid.append(2)
            high.append(0)
            low.append(0)
            if (n.parent == "appliance"):
                appliance.append(2)
            if (n.parent == "web"):
                web.append(2)
            if (n.parent == "SNMP"):
                web.append(2) 
        if n.severity == 'low':
            low.append(1)
            mid.append(0)
            high.append(0)
            if (n.parent == "appliance"):
                appliance.append(1)
            if (n.parent == "web"):
                web.append(1)
            if (n.parent == "SNMP"):
                web.append(1) 
    # print(appliance, web)
    return notifTime, low, mid, high, appliance, web, snmp
@login_required(redirect_field_name=None)
@permission_required("dashboard.view_dashboard" , "/noperm/")
def echart(request):
    from uptime import uptime 
    if request.user.is_authenticated:
        try:
            total_users, web_websites, dc, notification, camera = usage_analytics(request.user)
            cpuPercentage,usedRam,AvailRam,totalRam,usedSMemory,availSMemory,totalStorage,usedStorage,freeStorage = basicInfo()
            snmp,netconf,restconf,DeviceID,totalDevice = engine_core()
            notifTime,low,mid,high, applianceHM, webHM, snmpHM = notif_heatmap(request.user)
            websitenames = []
            servername = []
            networkname = []
            storagesss = []
            temp = {}
            color = {}
            temp["name"] = "Total "+str(totalStorage) + "GB"
            temp["value"] = 8.34
            color["color"] = "#fcba03"
            temp["itemStyle"] = color
            storagesss.append(temp)
            temp = {}
            temp["name"] = "Used "+str(usedStorage)+ "GB"
            temp["value"] = 8.33
            color["color"] = "#fcba03"
            temp["itemStyle"] = color
            storagesss.append(temp)
            temp = {}
            temp["name"] = "Free "+str(freeStorage)+ "GB"
            temp["value"] = 8.33
            color["color"] = "#fcba03"
            temp["itemStyle"] = color
            storagesss.append(temp)
            websites = WebsiteLinks.objects.all()
            for website in websites:
                temp = {}
                color = {}
                temp["name"] = website.website_name
                temp["value"] = 25 / websites.count()
                color["color"] = "#56fc03"
                temp["itemStyle"] = color
                websitenames.append(temp)
            # print(websitenames)
            devicess = AddDevice.objects.all()
            for device in devicess:
                temp = {}
                color = {}
                if device.type_of_device == "Network":
                    temp["name"] = device.Device_Asset_Tag
                    temp["value"] = 25 / devicess.count()
                    color["color"] = "#ffbbff"
                    temp["itemStyle"] = color
                    networkname.append(temp)
                elif device.type_of_device == "Server":
                    temp["name"] = device.Device_Asset_Tag
                    temp["value"] = 25 / devicess.count()
                    color["color"] = "#44bbff"
                    temp["itemStyle"] = color
                    servername.append(temp)
                else:
                    pass
            # print(websitenames, servername, networkname, storage)
            return render(request, 'dashboard/charts.html',{'total_users':total_users,'web_websites':web_websites,'datacenter':dc, 'notification':notification,'device':totalDevice,'camera':camera,'second':uptime,'cpuPercentage':cpuPercentage,'usedRam':usedRam,'AvailRam':AvailRam,'totalRam':totalRam,'totalStorage':totalStorage,'usedStorage':usedStorage,'freeStorage':freeStorage,'networkTime':time,'usedSMemory':usedSMemory, 'availSMemory':availSMemory,'snmp':snmp, 'netconf':netconf, 'restconf':restconf,'DeviceID':DeviceID,'notifTime':notifTime,'low':low, 'mid':mid, 'high':high, "applianceHM":applianceHM, 'webHM':webHM,'snmpHM':snmpHM, "allweb":websitenames, "allserver":servername, "allnetwork":networkname, "allstor":storagesss})
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/charts.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
    else:
        return redirect('login_page')

def applianceAjax(request, firstRun = 1):
    try:
        
        temperature = get_cpu_temp()
        total_users, web_websites, dc, notification, camera = usage_analytics(request.user)
        iowat = iowatInfo()
        cpuPercentage,usedRam,AvailRam,totalRam,usedSMemory,availSMemory,totalStorage,usedStorage,freeStorage = basicInfo()
        BYTES, PKTS = networkspeed()
        byte = [[BYTES[0]], [BYTES[1]]]
        pkts = [[PKTS[0]], [PKTS[1]]]
        cpulabels = []
        cpu = CPU.usage()["data"]["CPUUtilization"]
        indexI = 0
        for i in cpu:
            cpulabels.append("Core "+ str(indexI))
            indexI = indexI+1
        cpu = list(map(lambda el:[el], cpu))
        
        mode = "multi"
        if firstRun == 0:
            mode = "single"
        p, listOfRunningProcess = getListOfProcessSortedByMemory()
        returnData = {
            'usedRam':usedRam,
            'totalRam':totalRam,
            'availRam':AvailRam,
            'cpuPercentage':cpuPercentage, 
            'totalStorage':totalStorage,
            'usedStorage':usedStorage,
            'freeStorage':freeStorage,
            'usedSMemory':usedSMemory,
            'availSMemory':availSMemory,
            'runningProcess':p,
            'temp':temperature,
            'iowat':iowat,
            'total_users':total_users,
            'web_websites':web_websites,
            'notification':notification,
            'camera':camera,
            'datacenter':dc,
            'listOfRunningProcess':listOfRunningProcess[:5],
            'upload':BYTES[0],
            'download':BYTES[1]
        }
        
        return JsonResponse({
            "sideData" : returnData,
        "error" : False , "mode" : mode ,
        "data" : 
        {
            "network" :{
                "data": byte,
                "labels": ["Download", "Upload"],
                "xaxis" : datetime.now().strftime("%H:%M:%S")
                },
            "packet" :{
                "data": pkts,
                "labels": ["Packet In", "Packet Out"],
                "xaxis" : datetime.now().strftime("%H:%M:%S")
                },
            "cpu" :{
                "data": cpu,
                "labels": cpulabels,
                "xaxis" : datetime.now().strftime("%H:%M:%S")
                },
            "cpuUtil":{
                "data":[[returnData["cpuPercentage"]]],
                "labels": ["AVG"],
                "xaxis" : datetime.now().strftime("%H:%M:%S")
                },
            "ram":{
                "data":[[usedRam], [AvailRam]],
                "labels": ["Used", "Free"],
                "xaxis" : datetime.now().strftime("%H:%M:%S")
                },
            "swap":{
                "data" : [[usedSMemory], [availSMemory]],
                "labels" : ["Used" , "Available"],
                "xaxis" : datetime.now().strftime("%H:%M:%S")
                },
            "storage":{
                "data":[[usedStorage], [totalStorage]],
                "labels": ["Used", "Available"],
                "xaxis" : datetime.now().strftime("%H:%M:%S")
                },
            "iowait":{
                "data":[[iowat]],
                "labels": ["IOWAIT"],
                "xaxis" : datetime.now().strftime("%H:%M:%S")
                }
        }
        })
    except Exception as err:
        pass

def get_ip_address():
    if platform.system() == 'Windows':
        return socket.gethostbyname(socket.gethostname())
    else:
        try:
            # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # s.connect(("8.8.8.8", 80))
            # return s.getsockname()[0]
            # from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE
            import netifaces
            addr = [netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr'] for iface in netifaces.interfaces() if netifaces.AF_INET in netifaces.ifaddresses(iface)]
            if "127.0.0.1" in addr: addr.remove("127.0.0.1")
            # netmmask = ni.ifaddresses('enp2s0')[AF_INET][0]["addr"]
            return "<br>".join(addr)
        except Exception as err:
            return ""


@login_required(redirect_field_name=None)
@permission_required("dashboard.view_appliance" , "/noperm/")
def applianceDashboard(request):
    try:
        returnData = {}
        if not request.is_ajax():
            returnData["msg"] = "running"
            returnData["uptime"] = customUptime() 
            returnData["ipaddr"] = get_ip_address()
            print(returnData["ipaddr"])
            return render(request, 'dashboard/appliance.html', returnData)
        
    except Exception as e:
        db_logger.exception(e)        
        print(str(e))

        if request.is_ajax():
            return JsonResponse({"error" : True , "message" : "got an error"} )
        else:
            return render(request, "dashboard/appliance.html",{"exceptionRaise":"exceptionRaise","Curpath":"somepath","errTitle":"Page can't be opened",'errOutput':str(e)})

def networkspeed():
    try:
        # formula = (10000000/1.192)
        # st=speedtest.Speedtest()
        # time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # online
        # download = round(st.download()/formula,2)
        # upload= round(st.upload()/formula,2)
        # just to test and save my data
        # for i in range(100):
        #     upload = random.randint(1,78)
        #     download = random.randint(1,100)
        net_stat = psutil.net_io_counters()
        net_in_1 = net_stat.bytes_recv
        pkt_in_1 = net_stat.packets_recv

        net_out_1 = net_stat.bytes_sent
        pkt_out_1 = net_stat.packets_sent
        time.sleep(1)
        net_stat = psutil.net_io_counters()
        net_in_2 = net_stat.bytes_recv
        pkt_in_2 = net_stat.packets_recv

        net_out_2 = net_stat.bytes_sent
        pkt_out_2 = net_stat.packets_sent

        net_in = round((net_in_2 - net_in_1) / 1024 , 3)
        pkt_in = round((pkt_in_2 - pkt_in_1) / 1024 , 3)
        net_out = round((net_out_2 - net_out_1) / 1024 , 3)
        pkt_out = round((pkt_out_2 - pkt_out_1) / 1024 , 3)
        
        # print(pktSend, pktRecieve)

        BYTES=[net_in,net_out]
        PKTS=[pkt_in,pkt_out]
        # with open('dashboard/extraFiles/network.csv', 'a') as f_object:
        #     writer_object = writer(f_object)
        #     #f_object.write("\n")
        #     writer_object.writerow(List)
        #     f_object.close()
        # return JsonResponse({'status':'200','download':download,'upload':upload})
        return BYTES, PKTS
    except Exception as e:
        db_logger.exception(e)
        BYTES = [0, 0]
        PKTS = [0, 0]
        return BYTES, PKTS
        # with open('dashboard/extraFiles/network.csv', 'a') as f_object:
        #     writer_object = writer(f_object)
        #     #f_object.write("\n")
        #     writer_object.writerow(List)
        #     f_object.close()
        # return JsonResponse({'status':'200'})

class IPScan(View): 
    def post(self, request):
        regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
        part_ip = request.POST.get("ippart1")
        address = []
        if "/" in part_ip:
            try:
                for x in ipcalc.Network(part_ip):
                    address.append(str(x))
            except:
                return JsonResponse({
                    'IPdevices':'Invalid IP Adress'
                }, status=200)
        else:
            if(re.search(regex, part_ip)):
                address = [part_ip]
            else:
                return JsonResponse({
                    'IPdevices':'Invalid IP Address'
                }, status=200)

        # Scan IP Adresses
        for ip in address:
            if (scan(ip)):
                if DeviceCapibility.objects.filter(ip=ip).exists():
                    obj, created = TempIPDevice.objects.update_or_create(host=ip,defaults={'status': True, 'action':False},)
                else:
                    obj, created = TempIPDevice.objects.update_or_create(host=ip,defaults={'status': True, 'action':True},)
            else:
                obj, created = TempIPDevice.objects.update_or_create(host=ip,defaults={'status': False, 'action':False},)
        return JsonResponse({
            'IPdevices':'Devices Added. Please Refresh The Browser'
        }, status=200)

def AddDeviceIP(request):
    try:
        host = request.GET.get("host")
        print(host)
        obj = DeviceCapibility.objects.filter(ip=host).count()
        if obj>0:
            return JsonResponse({
                'data': "Device Already Added",
                'action': False
            })
        NEWdevice = DeviceCapibility(ip = host)
        NEWdevice.save()
        tempIP = TempIPDevice.objects.get(host=host)
        tempIP.action = False
        tempIP.save()
        msg = "New Device Added"
        return JsonResponse({
                'data': msg,
                'action': True,
                'error': False
            })
        return redirect('/asset/forms/')
    except Exception as e:
        return JsonResponse({
                'data': "Something went wrong: " + str(e),
                'action': True,
                'error': True
            })

# @login_required(redirect_field_name=None)
# def network(request):

#     # data = functionToGETSNMPDATA()
#     #data2 = views_snmp.getPortStatus("192.168.2.10" , "NETWORK@123" , 40)
    
#     devices = list(DeviceCapibility.objects.filter(is_snmp = True).values('id' , 'is_snmp' , 'name' , 'ip' , 'commString'))
    
    
#     print(devices)
#     data = {
#         #"networkGraph" : data2,
#         "snmpdevices" : devices,
#         #"totalDevices" : totalDevices
#     }
#     return render(request, 'dashboard/networkGraph.html' , data)


# def listSum(l1):
#     sum = 0
#     for i in l1:
#         sum = sum + int( i[:-2] )
    
#     return sum

# def getNetworkSummary(request):
#     totalDevices = len(DeviceCapibility.objects.all())
#     devices = DeviceCapibility.objects.filter(is_snmp = True).values('id' , 'is_snmp' , 'name' , 'ip' , 'commString')

#     totalOutbound = 0
#     totalInbound = 0

#     for device in devices:

#         if len(device["ip"]) == 0 or len(device["commString"]) == 0:
#             continue

#         data = views_snmp.getPortStatus(device["ip"] , device["commString"] , 40)

#         if(data["error"]):
#             continue
            
#         data = data["data"]

#         totalOutbound = totalOutbound + listSum(data["outbound"])
#         totalInbound = totalInbound + listSum(data["inbound"])

    
#     return JsonResponse( {"error" : False , "totalDevices" : totalDevices , "outbound" : totalOutbound , "inbound" : totalInbound} )


# def getNetworkDeviceData(request):
#     ID = request.GET["id"]
#     if(id == None):
#         return JsonResponse({"error" : True , "message" : "Device ID missing."})

#     try:
#         record = DeviceCapibility.objects.get(id = ID)
#     except Exception as err :
#         return JsonResponse({"error" : True , "message" : "No device found with the ID " + ID})
    
#     if not record.is_snmp :
#         return JsonResponse({"error" : True , "message" : "Device does not support SNMP"})
    
#     print(record.ip)
#     print(record.commString)

#     if(record.ip == None or record.commString == None or len(record.ip) == 0 or len(record.commString) == 0):
#         return JsonResponse({"error" : True , "message" : "Host / Community String is empty"})
        
#     data2 = views_snmp.getPortStatus(record.ip , record.commString , 40)
#     #data2 = views_snmp.getPortStatus("192.168.2.10" , "NETWORK@123" , 40)
#     return JsonResponse(data2)



@login_required(redirect_field_name=None)
def dbms(request):
    return render(request, 'dashboard/dbmsGraph.html')

@login_required(redirect_field_name=None)
def server(request):
    return render(request, 'dashboard/serverGraph.html')

@login_required(redirect_field_name=None)
def storage(request):
    return render(request, 'dashboard/storageGraph.html') 

@login_required(redirect_field_name=None)
def LogsNotif(request):
    logs = StatusLog.objects.all().order_by("-create_datetime")
    # data = Notif.objects.filter(user=request.user, is_delete=False).order_by("-date")
    return render(request, 'dashboard/logs.html', {'logs':logs})

# @login_required(redirect_field_name=None)
# def applianceDashboard(request):
#     if request.user.is_authenticated:
#         msg = request.GET.get('login','')
#         try:         
#             temperature = get_cpu_temp()   
#             p = running_process()            
#             time,download,upload = networkWriteInCV()
#             uptime = customUptime() 
#             iowat = iowatInfo()
#             cpuPercentage,usedRam,AvailRam,totalRam,usedSMemory,availSMemory,totalStorage,usedStorage,freeStorage = basicInfo()
#             colIOWait = ""
#             colCPU = ""
#             MemoryPoloCol = ""
#             if (iowat > 0) and (iowat <= 60):
#                 colIOWait = "green"
#                 colIOWait = "orange"
#             else:
#                 colIOWait = "red"
#             if (cpuPercentage > 0) and (cpuPercentage <= 60):
#                 colCPU = "green"
#             elif (cpuPercentage > 60) and (cpuPercentage <= 85):
#                 colCPU = "orange"
#             else:
#                 colCPU = "red"
#             if ((usedStorage/totalStorage)*100 > 0) and ((usedStorage/totalStorage)*100 <= 60):
#                 MemoryPoloCol = "green"
#             elif ((usedStorage/totalStorage)*100 > 60) and ((usedStorage/totalStorage)*100 <= 85):
#                 MemoryPoloCol = "orange"
#             else:
#                 MemoryPoloCol = "red"
#             return render(request, 'dashboard/appliance.html',{'msg':msg,'second':uptime,'cpuPercentage':cpuPercentage,'usedRam':usedRam,'AvailRam':AvailRam,'totalRam':totalRam,'totalStorage':totalStorage,'usedStorage':usedStorage,'freeStorage':freeStorage, 'cpuGaugeColor':colCPU, 'vmGaugeColor':colIOWait,'download':download,'upload':upload,'networkTime':time,'usedSMemory':usedSMemory, 'availSMemory':availSMemory,'runningProcess':p,'MemoryPoloCol':MemoryPoloCol,'temp':temperature,'iowat':iowat})
#         except Exception as e:
#             db_logger.exception(e)
#             path = request.path
#             return render(request, "dashboard/appliance.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
#     else:
#         return redirect('login_page')


@permission_required("dashboard.view_settings" , "/noperm/")
def nfs(request):
    return render(request, "dashboard/nfs.html")