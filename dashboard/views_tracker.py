from django.http import JsonResponse
from tracking_analyzer.models import Tracker
from django.shortcuts import render
from django.db.models import Count
from django_countries import countries
from seoanalyzer import analyze
import findcdn
import json

def stats(request):

    COUNTRY_DICT = dict(countries)

    exclude_list = ['127.0.0.1', '192.168.1.120','103.95.83.123']
    obj = Tracker.objects.all().exclude(ip_address__in = exclude_list)
    total_users = obj.distinct("ip_address").count()
    total_countries = obj.distinct("ip_country").count()

    new_data = []

    top_countries = []

    t = {}
    for d in obj:
        
        if not d.ip_country.code in t:
            t[d.ip_country.code] = {
                "name": d.ip_country.name,
                "count": 1
            }
        else:
            count = 1
            t[d.ip_country.code]["count"] += count
            count += 1
    
    for d in t:
        temp = []
        temp.append(t[d]["count"])
        temp.append(t[d]["name"])
        temp.append(d)
        new_data.append(temp)

    top_countries = obj.values("ip_country").annotate(total=Count('ip_country')).order_by('-total')[:5]

    # print(top_countries)
    top_browsers = obj.values("browser").annotate(total=Count('browser')).order_by('-total')[:5]
    top_devices = obj.values("device_type").annotate(total=Count('device_type')).order_by('-total')[:5]
    most_in_a_day = obj.values("timestamp").annotate(total=Count('timestamp')).order_by('-total')[:5]

    # datetime field : 16/09/22 1:05
    # datetime field : 16/09/22 2:05

    most_in_a_day = obj.extra(select={'day': "TO_CHAR(timestamp, 'YYYY-MM-DD')"}).values('day').order_by('day').annotate(visits=Count('timestamp'))

    temp = {
        "countries": {
            "labels": [],
            "data": []
        },
        "browsers": {
            "labels": [],
            "data": []
        },
        "devices": {
            "labels": [],
            "data": []
        },
        "most_visit": {
            "labels": [],
            "data": []
        }
    }

    for country in top_countries:
        temp["countries"]["labels"].append(country["ip_country"])
        temp["countries"]["data"].append(country["total"])

    for browser in top_browsers:
        temp["browsers"]["labels"].append(browser["browser"])
        temp["browsers"]["data"].append(browser["total"])

    for device in top_devices:
        temp["devices"]["labels"].append(device["device_type"])
        temp["devices"]["data"].append(device["total"])

    for visit in most_in_a_day:
        temp["most_visit"]["labels"].append(visit["day"])
        temp["most_visit"]["data"].append(visit["visits"])

    # print(temp)
    data = {
        "obj":obj,
        "total_users": total_users,
        "total_countries": total_countries,
        "new_data": new_data,
        "top_countries":temp
    }

    return render(request, "stats.html", data)

def cdn(request):
    return render(request, "cdn.html")

def cdnfind(request):
    url = request.GET.get("url", None)
    resp_json = findcdn.main([url], double_in = True)
    return JsonResponse(json.loads(resp_json))
    
def crawl(request):
    url = request.GET.get("url", None)
    if url is None:
        return JsonResponse({"pages": ""})

    output = analyze(url)
    return JsonResponse(output)