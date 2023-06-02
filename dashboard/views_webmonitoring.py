import time
from django.shortcuts import redirect
from django.http.response import JsonResponse , HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import WebsiteLinks
from django_db_logger.models import StatusLog
import requests
from datetime import datetime
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
import logging

try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))


@login_required(redirect_field_name=None)
@permission_required("dashboard.view_webmonitoring" , "/noperm/")
def hexbin_graph(request):
    if request.user.is_authenticated:
        try:
            total_records_to_Show = 8
            websites_pack = WebsiteLinks.objects.all().order_by("-is_favorite")
            totalWebsite = websites_pack.count()
            websites_pack = websites_pack[:total_records_to_Show]
            if request.method == 'POST':
                if not request.user.has_perm("dashboard.add_webmonitoring"):
                    return redirect("@redirectloginurl")
                try:
                    data = []
                    total = 0
                    down = 0
                    if request.POST.get('website_name'):
                        website = request.POST.get('protocol')+request.POST.get('website_name')
                        if WebsiteLinks.objects.filter(website_name=website):
                            return redirect("/web/monitoring?msg=error")                  
                        websites = WebsiteLinks()
                        websites.website_name = website
                        websites.save()
                        return redirect('hexbin_graph')
                except Exception as e:
                    db_logger.exception(e)
                    path = request.path
                    return render(request, "dashboard/heatmap.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
            else:
                msg = request.GET.get('msg','')
                data = []
                rt = []
                total = 0
                down = 0
                for url in websites_pack:
                    state = False
                    # webObjects = WebsiteLinks.objects.get(website_name = url.website_name)
            #         startTime = time.time()
                    # try:
                    #     r = requests.get(url.website_name).status_code
                    # except ConnectionError as err:
                    #     db_logger.exception(err)
                    #     r = 0
                    # except requests.exceptions.RequestException as err:
                    #     db_logger.exception(err)
                    #     r = 0
                    # if r == 200:
                    #     state = True
                    #     total = total + 1
                    # else:
                    #     state=False
                    #     down = down + 1
            #         endTime = time.time()
                    # if webObjects.response_time != '':
                    #     webObjects.response_time = str(webObjects.response_time) + "," + str(round((endTime - startTime),2))
                    # else:
                    #     webObjects.response_time = str(round((endTime - startTime),2))
                    # webObjects.save()
            #         then = datetime.fromisoformat(url.website_up)
            #         now  = datetime.now()
            #         duration = now - then
            #         duration_in_s = duration.total_seconds() 
                    data.append({
                        'id':url.id,
                        'website':url.website_name,
                        'status':state,
                        # 'time': round((endTime - startTime),2),
                        # 'uptime':duration_in_s,
                        'is_favorite':url.is_favorite,
                    })
            #         Rtime = webObjects.response_time
            #         r = Rtime.split(',')
            #         map_object = map(float, r)
            #         rst = list(map_object)
            #         rt.append({
            #             'id':url.id,
            #             'rs': rst
            #         })
                # print(rt)
                context = {
                    'website_pack': data, 'total':total, 'down':down,'totalWebsite':totalWebsite, 'responseTime':rt,'total_records_to_Show':total_records_to_Show
                }
                return render(request, 'dashboard/heatmap.html', context)
        except Exception as e:
            db_logger.exception(e)
            path = request.path
            return render(request, "dashboard/heatmap.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
    else: 
        return redirect('/')



def responseTime(request):
    url = request.GET.get("url")
    state = False
    startTime = time.time()
    try:
        r = requests.get(url, timeout=10).status_code
    except ConnectionError as err:
        db_logger.exception(err)
        r = 0
    except requests.exceptions.RequestException as err:
        db_logger.exception(err)
        r = 0
    if r == 200:
        state = True
    else:
        state=False
    endTime = time.time()
    return JsonResponse({
        "url":url,
        "state":state,
        "response_time":str(round((endTime - startTime),2))
    })

def WemMonitoring(request):
    user_li = WebsiteLinks.objects.all().order_by("-is_favorite")
    total_records_to_Show = 8
    user_li = WebsiteLinks.objects.all().order_by("-is_favorite")[:total_records_to_Show]
    # # print(user_li)
    # maxDataToShow = request.GET.get('max')
    # if not maxDataToShow:
    #     maxDataToShow = 10
    # paginator = Paginator(user_li, maxDataToShow)
    # page = request.GET.get('page')
    
    # try:
    #     users = paginator.page(page)
    # # If the number of pages is not an integer, return to the first page
    # except PageNotAnInteger:
    #     users = paginator.page(1)
    # # If the number of pages does not exist / is illegal, return to the last page
    # except InvalidPage:
    #     users = paginator.page(paginator.num_pages)
    # # user_li = list(users.object_list.values())
    # websites_pack = list(users.object_list.values())   
    
    data = []
    rt = []
    total = 0
    down = 0

    for url in user_li:
        # print("*" * 100)
        # print(url)
        state = False
        startTime = time.time()
        webObjects = WebsiteLinks.objects.get(website_name = url.website_name)
        try:
            r = requests.get(url.website_name, timeout=1).status_code
        except ConnectionError as err:
            db_logger.exception(err)
            r = 0
        except requests.exceptions.RequestException as err:
            db_logger.exception(err)
            r = 0
        if r == 200:
            state = True
            total = total + 1
        else:
            state=False
            down = down + 1
        endTime = time.time()
        if webObjects.response_time != '':
            webObjects.response_time = str(webObjects.response_time) + "," + str(round((endTime - startTime),2))
        else:
            webObjects.response_time = str(round((endTime - startTime),2))
        webObjects.save()
        Rtime = webObjects.response_time
        r = Rtime.split(',')
        map_object = map(float, r)
        rst = list(map_object)
        then = datetime.fromisoformat(url.website_up)
        now  = datetime.now()
        duration = now - then
        duration_in_s = duration.total_seconds() 
        data.append({
            'id':url.id,
            'website':url.website_name,
            'status':state,
            'time': round((endTime - startTime),2),
            'rs':rst,
            'is_favorite':url.is_favorite,
            'uptime':duration_in_s
        })
        # print(data)
    return JsonResponse({
        'website_pack': data,
        'total':total,
        'down':down,
    })



@login_required(redirect_field_name=None)
@permission_required("dashboard.delete_webmonitoring" , "/noperm/")
def delete_web_monitor(request, id):
    
    try:
        website = WebsiteLinks.objects.get(id=id)
        website.delete()
        msg = "Deleted Successfully"
        return redirect('hexbin_graph')
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/heatmap.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})



def changeWebFav(request):
    id = int(request.GET.get("id"))
    isFavorite = request.GET.get("isFavorite")
    obj = WebsiteLinks.objects.get(id=id)
    print(id, isFavorite, obj)
    if isFavorite == False or isFavorite == "false" :
        obj.is_favorite = True
    else:
        obj.is_favorite = False
    obj.save()
    return JsonResponse({
        "error":False
    })


def AjaxWeb(request):
    device = WebsiteLinks.objects.all().order_by("-is_favorite")
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



    