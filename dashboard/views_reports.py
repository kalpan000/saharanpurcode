from django.http import JsonResponse
from django.shortcuts import render
from django.apps import apps
from django.core import serializers
from django.http import HttpResponse
import json
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required


def loadData(request):
    # start = int(request.GET["start"])
    # end = int(request.GET["end"])
    name = request.GET["name"]    
    fields = request.GET["fields"]
    fields = fields.split(",")
    # print(fields)
    l = apps.all_models['dashboard']

    # if start < 0 or end < 0:
    #     return JsonResponse({"error" : True , "message" : "Range must be a positive number"})
    


    try:
        model = l[name]
        # print(model)
        records = model.objects.all().count()
        # print(records)
        if records == 0:
            return JsonResponse({"error" : True , "message" : "No records found"})

        # if end >= len(records):
        #     end = len(records) 

        
        # if start >= len(records):
        #     start = len(records) - 1

        # print(model.objects.all())
        # records = serializers.serialize("json", model.objects.all()[start : end])
        records = list(model.objects.values_list(*fields))
        # records = serializers.serialize("json", model.objects.values_list(*fields))
        print(records)
        # return HttpResponse(records, content_type='application/json')
        return JsonResponse({"error" : False , "message" : "successfull" , "data" : records})

    except Exception as err:
        return JsonResponse({"error" : True , "message" : "Model doesnt exist" , "errorMessage" : str(err)})

    

def loadFieldName(request): 
    l = apps.all_models['dashboard']
    model = l[request.GET["name"]]
    fields = [field.name for field in model._meta.get_fields()]
    data = list(model.objects.all().values())
    return JsonResponse({"error" : False , "message" : "successfull" ,"fields":fields, "data" : data})

@permission_required("dashboard.view_reports" , "/noperm/")
def loadTemplate(request):
    l = apps.all_models['dashboard']
    # ['tempipdevice', 'product', 'cameramonitor', 'websitelinks', 'datacenterstate', 'userprofile', 'adddatacenter', 'adddatacenterrow', 'adddatacenterrackcabinet', 'adddevice', 'devicetemplate', 'devicedetails', 'notif', 'patchpanel', 'patchpanelport', 'pduportform', 'devicecapibility', 'contactus', 'raiseticket','ansibleoutput', 'sshservers', 'cabels', 'appliancedatacollection', 'dashboarddatacollection', 'testmodal', 'snmpdatacollection','snmpinterfacedatacollection','license']

    data = {}
    data = {
        "Users": [
            {"User Profile":"userprofile"},
            {"License":"license"},
            {"Tickets":"raiseticket"},
        ],
        "Devices": [
            {"CCTV":"cameramonitor"},
            {"IP Camera":"product"},
            {"Website Link":"websitelinks"},
            {"Cables":"cabels"}
        ],
        "Network": [
            {"Device Capability":"devicecapibility"},
            {"Cron IP Devices":"tempipdevice"}
        ],
        "Managemment": [
            {"Notifications":"notif"},
            {"Patch Panel": "patchpanel"},
            {"PDU Ports": "pduportform"},
            {"SSH Servers": "sshservers"}
        ],
        "Data":[
            {"Appliance Data":"testmodal"},
            {"Dashboard Data": "dashboarddatacollection"},
            {"SNMP Data": "snmpdatacollection"},
            {"Contact Us": "contactus"}
        ],
        "Datacenter": [
            {"Devices":"adddevice"},
            {"Datacenter Rows": "adddatacenterrow"},
            {"Datacenter Racks": "adddatacenterrackcabinet"},
            {"Datacenter": "adddatacenter"}
        ]
    }



    # print(data)
    data = {
        "models" : data
    }
    return render(request, "dashboard/reports.html" , data)