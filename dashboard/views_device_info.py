from .models import AddDevice, DeviceCapibility
import logging
from django.http import JsonResponse
from django_db_logger.models import StatusLog
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage

# db_logger = logging.getLogger('db')
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))

def decommisionDevice(request):
    device = AddDevice.objects.filter(is_delete=False).order_by('id')
    maxDataToShow = request.GET.get('max')
    if not maxDataToShow:
        maxDataToShow = 10
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

def retrieveDevice(request):
    device = DeviceCapibility.objects.get(id=int(request.POST["id"]))
    return JsonResponse({
        'device':device.name,
        'host': device.ip,
        'is_snmp': device.is_snmp,
        'is_netconf': device.is_netconf,
        'is_restconf': device.is_restconf,
        'snmp': device.snmp,
        'netconf': device.netconf,
        'restconf': device.restconf,
        'created': device.created,
        'updated': device.updated
    })