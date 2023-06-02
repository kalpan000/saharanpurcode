import json

from structlog import dev
from .models import DeviceSetting, UserProfile, addDataCenter, addDataCenterRow, AddDataCenterRackcabinet, AddDevice, Notif, DeviceDetails, PatchPanel, PatchPanelPort, DeviceTemplate, DeviceCapibility, CameraMonitor, ContactUs, RaiseTicket, Cabels, TempIPDevice, PduPortForm, DataCenterState
import logging
from django.views import View
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
from django.core import serializers
from django.db.models import Sum

import pandas as pd
from django_db_logger.models import StatusLog
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required


# db_logger = logging.getLogger('db')
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))

def getMapDetails(file="states_india.geojson"):
    f = open("static/"+file)
    data = json.load(f)

    if(len(data["features"])) <= DataCenterState.objects.filter().count():
        return
    for i in data['features']:
        try:
            state = i["properties"]["state"]
            # print(state)
            updated, created = DataCenterState.objects.update_or_create(
                state_name=state, defaults={'state_name': state})
        except Exception as ex:
            print("Error is " + str(ex))

    f.close()
def datepick(request):
    data = {key: value.strip() for key, value in request.POST.items()}
    id = int(data["deviceinfo"])
    device = AddDevice.objects.get(id=id)
    date = data.get("datepick", "")
    device.expiryDate = date
    device.save()

    msg = "Device Renew"
    messages.success(request, msg)
    return redirect('/asset/forms/')
    
class assetsForms(View):

    @method_decorator(permission_required("dashboard.view_assetpage" , "/noperm/"))
    def get(self, request):
        try:
            availDevice = []
            returnData = {}
            try:
                map = DeviceSetting.objects.get(id=1)
            except:
                map = DeviceSetting.objects.update_or_create(id = 1)
            if map.country == "india":
                mapView = "states_india.geojson"
            elif map.country == "uae":
                mapView = "uae.geojson"
            else:
                mapView = ""
            getMapDetails(mapView)
            dc = addDataCenter.objects.all().count()
            total_records_to_Show = 2
            returnData["total_records_to_Show"] = total_records_to_Show
            returnData["mapView"] = mapView
            
            returnData["states"] = DataCenterState.objects.all()
            returnData["datacenter"] = addDataCenter.objects.all()
            returnData["all_device"] = AddDevice.objects.all()
            
            returnData["lmsDeviceCount"] = returnData["all_device"].filter(is_delete=False).count()

            returnData["lmsArchieveDevice"] = returnData["all_device"].filter(is_delete=True)
            returnData["lmsArchieveDeviceCount"] = returnData["lmsArchieveDevice"].count()
            returnData["load_balancer"] = returnData["all_device"].filter(type_of_device='Load Balancer').count()
            returnData["devicetemplate"] = DeviceTemplate.objects.all()

            device = DeviceCapibility.objects.all().order_by("-created")
            
            tempdevicePage = Paginator(device, total_records_to_Show)
            returnData["devicePage_count"] = tempdevicePage.count

            returnData["IPdevice"] = tempdevicePage.page(1)
            for i in device:
                tempDevice = {}
                ippart = i.ip.split(".")
                tempDevice["ip"] = i.ip
                tempDevice["id"] = i.id
                tempDevice["name"] = i.name
                tempDevice["created"] = i.created 
                tempDevice["updated"] = i.updated
                tempDevice["is_snmp"] = i.is_snmp
                tempDevice["is_netconf"] = i.is_netconf
                tempDevice["is_restconf"] = i.is_restconf
                tempDevice["user"] = i.user
                tempDevice["pwd"] = i.pwd
                tempDevice["commString"] = i.commString
                try:
                    AddDevice.objects.get(IP_Address_col1=ippart[0],IP_Address_col2=ippart[1],IP_Address_col3=ippart[2],IP_Address_col4=ippart[3])
                    tempDevice["is_there"] = True
                except:
                    tempDevice["is_there"] = False
                availDevice.append(tempDevice)
            # print(availDevice)
            returnData["availDevice"] = availDevice
            returnData["IPdeviceDict"] = device
            tempipdevice = TempIPDevice.objects.filter(status=True).order_by("created").distinct()
            
            tempipdevicePage = Paginator(tempipdevice, total_records_to_Show)
            returnData["tempipdevicePage_count"] = tempipdevicePage.count

            returnData["tempIPDevice"] = tempipdevicePage.page(1)

            returnData["pue"] = 0
            if returnData["datacenter"].count() >= 1 and returnData["all_device"].count() >= 1:
                try:
                    total_power = addDataCenter.objects.aggregate(Sum('Capacity_in_MW'))
                    power_utilization = AddDevice.objects.aggregate(Sum('deviceWatt'))
                    returnData["pue"] = round(total_power["Capacity_in_MW__sum"] / power_utilization["deviceWatt__sum"], 2)
                except Exception as err:
                    returnData["pue"] = 0
            
            if addDataCenter.objects.all().count() >= 1: 
                df = pd.DataFrame(list(addDataCenter.objects.all().values('Add_state', 'Capacity_in_MW', 'sqr_mtr', 'DataCenterName')))
                df["Capacity"] = pd.to_numeric(df["Capacity_in_MW"])
                df["Sqr Mtr"] = pd.to_numeric(df["sqr_mtr"])
                returnData["labels"] = ['Add_state', 'Capacity_in_MW', 'sqr_mtr','DataCenterName', 'capacity_in_mw', 'sqr_mtr']
            else:
                df = pd.DataFrame(list(DataCenterState.objects.all().values('state_name')))
                df["Capacity"] = pd.to_numeric(0)
                returnData["labels"] = ['state_name', '0', '0']
            
            # Cables Data

            returnData["allData"] = df.values.tolist()
            records = Cabels.objects.all()
            
            returnData["cablesData"] = {}

            for record in records:
                returnData["cablesData"][record.name] = record.quantity

            queries = PatchPanelPort.objects.distinct("patchpanel")
            returnData["deviceData"] = []
            for query in queries:
                returnData["deviceData"].append({"port": query.port, "id": query.patchpanel.id,"name": query.patchpanel.Device_Asset_Tag})
            
            return render(request, "dashboard/assets_forms.html", returnData)
            #return render(request, "dashboard/assets_forms.html", {'states': states, 'datacenter': data_center, 'devicetemplate': devicetemplate, 'all_devices': all_devices, 'labels': labels, 'allData': df.values.tolist(), "cablesData": j, "deviceData": devices, 'IPdevice': devicePage, 'devicePage_count': devicePage_count, 'IPdeviceDict': deviceDict, 'load_balancer': load_balancer, 'pue': pue, 'tempIPDevice': ipdevice, 'tempipdevicePage_count': tempipdevicePage_count,'lmsArchieveDeviceCount': lmsArchieveDeviceCount,'lmsDeviceCount': lmsDeviceCount,'total_records_to_Show': total_records_to_Show})
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/assets_forms.html", {"exceptionRaise": "exceptionRaise", "Curpath": path, "errTitle": "Page can't be opened", 'errOutput': str(e)})

    @method_decorator(permission_required("dashboard.add_assetpage" , "/noperm/"))
    def post(self, request):
        try:
            if request.POST.get("form_type") == 'datepick':
                return datepick(request)            
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/assets_forms.html", {"exceptionRaise": "exceptionRaise", "Curpath": path, "errTitle": "Page can't be opened", 'errOutput': str(e)})


@login_required(redirect_field_name=None)
def top(request, id):
    obj={}
    maxLen = 0
    try:
        try:
            datacenter = addDataCenter.objects.get(id=id)
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/topview.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
        rows = addDataCenterRow.objects.filter(data_center=datacenter)
        for r in rows:
            obj[r.RackRow] = []
        racks = AddDataCenterRackcabinet.objects.filter(datacenter=datacenter, is_delete=False)
        for r in racks:
            # print(r.date_center_row.RackRow, r.Rack_Label_Tag)
            obj[r.date_center_row.RackRow].append(r.Rack_Label_Tag)
            l = len(obj[r.date_center_row.RackRow])
            if (maxLen < l):
                maxLen = l
        data = {
            "data" : obj,
            "maxLen" : maxLen
        }
        # print(data)
        return render(request, "dashboard/topview.html", {'data':data})
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/topview.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})


@login_required(redirect_field_name=None)
@permission_required("dashboard.view_assetpage" , "/noperm/")
def datacenter_page(request, id):
    
    try:
        # totalDevice=[]
        try:
            datacenter = addDataCenter.objects.get(id=id)
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/dc.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
        rows = addDataCenterRow.objects.filter(data_center=datacenter)
        rowsTotal = rows.count()
        racks = AddDataCenterRackcabinet.objects.filter(datacenter=datacenter, is_delete=False)
        # rack_occupied = racks.device_height_array.split(',')
        # print(rack_occupied)
            
        racksTotal = racks.count()
        device = AddDevice.objects.filter(datacenter=datacenter)
        total=device.exclude(type_of_device="PDU").count()
        # for r in racks:
            # total_device=AddDevice.objects.filter(data_center_rack=r)
            # totalDevice.append(total_device.count) 

        # device = AddDevice.objects.filter(datacenter=datacenter).values_list('Unit_Location', flat=True)
        # print(device) 
        return render(request, "dashboard/dc.html", {'datacenter':datacenter, 'datacenterrows':rows, 'datacenterracks':racks, 'device':device,'rowsTotal':rowsTotal,'racksTotal':racksTotal,'total':total})
        # return HttpResponse("Open Datacenter "+str(id))
    except Exception as e:
        path = request.path
        return render(request, "dashboard/dc.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

@login_required(redirect_field_name=None)
@permission_required("dashboard.delete_assetpage" , "/noperm/")
def deleteDC(request, id):
    try:
        try:
            dc = addDataCenter.objects.get(id=id)
        except Exception as e:
            db_logger.exception(e)
            return render(request, "dashboard/assets_forms.html",{"exceptionRaise":"exceptionRaise","errTitle":"Page can't be opened",'errOutput':str(e)})
        dc.delete()
        msg = "Datacenter Deleted"
        messages.success(request, msg)
        return redirect('/asset/forms/')
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/assets_forms.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})

@permission_required("dashboard.change_assetpage" , "/noperm/")
def editDC(request,id):
    try:
        data_center = addDataCenter.objects.get(id=id)
        msg = ""
        if request.method == "POST":
            data = {key:value.strip() for key, value in request.POST.items()}
            # print(data)
            data_center.dataCenterTag = data["data_center_tag"]
            data_center.DataCenterName = data["data_center_name"]
            data_center.sqr_mtr = data["sqr_mtr"]
            data_center.Add_country = data["address_country"]
            data_center.Add_state = data["address_state"]
            data_center.Address = data["address_text"]
            data_center.Contact = data["contact"]
            data_center.PersonalDet_fname = data["full_name"]
            data_center.PersonalDet_email = data["email_contact"]
            data_center.phone = data["phone_contact"]
            data_center.Capacity_in_MW = data["capacity"]
            data_center.save()
            msg = "DataCenter Edited"
            messages.success(request, msg)
            return redirect("/asset/forms/")
        else:
            return render(request, 'dashboard/editDC.html', {'datacenter':data_center,'msg':msg})
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/editDC.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})