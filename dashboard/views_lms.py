from django.template import base
from .models import AddDevice, WebsiteLinks
import logging
from django.http import JsonResponse
from django_db_logger.models import StatusLog
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
from urllib.request import Request, urlopen, ssl, socket
from urllib.error import URLError, HTTPError
import json

# db_logger = logging.getLogger('db')
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))

def lmsDevice(request):
    device = AddDevice.objects.filter(is_delete=False).order_by('expiryDate')
    # remaining = (device.expiryDate - datetime.datetime.now().date()).days
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

def lmsarchieveDevice(request):
    device = AddDevice.objects.filter(is_delete=True).order_by('id')
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


def websiteLMS(reqest):
    # base_url = reqest.GET.get("url",None)

    websites = WebsiteLinks.objects.all()
    data = {}
    for website in websites:
        url = website.website_name.split("//")[1]
        if url[-1] == "/":
            url = url[0:-1]
        if url:
            port = '443'
            try:
                hostname = url
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port)) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        data[url] = {"status":True, "data":ssock.getpeercert()}
            except ssl.SSLError as err:
                data[url] = {"status":False, "data":"Certificate Expired"}
            except socket.gaierror as err:
                data[url] = {"status":False, "data":"Host not reachable"}
            except Exception as err:
                data[url] = {"status":False, "data":str(err)}
    return JsonResponse(data)