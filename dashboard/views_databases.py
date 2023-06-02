from django.http import JsonResponse
from django.shortcuts import render

from .models import addDataCenter , AddDevice , AddDataCenterRackcabinet


def loadAll(request , datacenter):
    try:
        center = addDataCenter.objects.get(DataCenterName = datacenter)
        devices = AddDevice.objects.filter(datacenter = center)
        racks = AddDataCenterRackcabinet.objects.filter(datacenter = center)
        
        devices = list(devices.values("Device_Asset_Tag" , "Device_Description" , "type_of_device" , "deviceModel" , "deviceMake" , "installDate" , "expiryDate" , "deviceOwner" , "IP_Address_col1" , "IP_Address_col2" , "IP_Address_col3" , "IP_Address_col4"))
        cabinets = list(racks.values())    

        datacenterDetails = {
            "name" : center.DataCenterName,
            "country" : center.Add_country,
            "state" : center.Add_state,
            "address" : center.Address,
            "contact" : center.Contact
        }

        data = {
            "datacenter" : datacenterDetails,
            "devices" : {
                "total" : len(devices),
            },
            "cabinets" : {
                "total" : len(cabinets)
            }
        }

        return JsonResponse({"error" : False , "message" : "message" , "data" : data})
    except Exception as err:
        return JsonResponse({"error" : True , "message" : "Something went wrong" , "errorMsg" : str(err)})


def loadTemplate(request):
    records = addDataCenter.objects.all().values("DataCenterName")
    print(records)
    data = {
        "datacenters" : records
    }
    return render(request, "dashboard/viewalldbinformation.html" , data)
