import itertools 
from datetime import datetime
import datetime as DATETIME
from .models import *
from django.http import JsonResponse
from .views_apm import CPU
from dashboard.views import basicInfo, iowatInfo, usage_analytics, running_process, get_cpu_temp, networkspeed

# # for 1 day data showing minutes wise
def date_min(timestamp):
    return timestamp.strftime("%x %H:%M") # make groups based on a date and minutes 

# for 1 month data showing hour wise 
def date_hour(timestamp):
    return timestamp.strftime("%x %H") # make groups based on dates and hours 

# for 1+ months showing day wise
def date_days(timestamp):
    return timestamp.strftime("%x") # make groups based on a date

def listsum(l1 , l2):
    leng1 = len(l1)
    leng2 = len(l2)

    if leng1 != leng2:
        return [0] * max(leng1 , leng2)
        
    output = []
    for i in range(0 , leng1):
        output.append(l1[i] + l2[i])

    return output    


def str2list(s):
    arr = s.split(",")
    return list(map(float , arr))

# duration = day , months => range = 1 month
# start and end_date are datetime objs datetime(2021 , 10 , 25) 

def sum(match):
    s = 0

    sumArr = []
    runOnce = True
    
    if not match.valueArr or match.valueArr == None or match.valueArr == "":
        return s + match.value
        
    else:
        l = str2list(match.valueArr)
        if runOnce:
            sumArr = [0] * len(l)
            runOnce = False
        return (l , sumArr)


def max(matches):
    m = 0
    for match in matches:
        if m > match.value:
            m = match.value
    return m

def min(matches):
    m = 0
    for match in matches:
        if m < match.value:
            m = match.value
    return m

def avg(matches):
    s = 0
    l = 0

    sumArr = []
    runOnce = True
    for match in matches:
        l = l + 1
        if not match.valueArr or match.valueArr == None or match.valueArr == "":
            s = s + match.value
        else:
            l = str2list(match.valueArr)
            if runOnce:
                sumArr = [0] * len(l)
                runOnce = False
            sumArr = [sum(i) for i in zip(sumArr, l)]
    
    if runOnce:
        return s / l
    else:
        return [i / l for i in sumArr]  



def realtime(model , type , totalRecordstoReturn):
    records = model.objects.filter(type=type).order_by("-created_at")[:totalRecordstoReturn]
    
    output = []
    onceOnly = True
    for record in records:
        if not record.valueArr or record.valueArr == None or record.valueArr == "":
            output.append(record.value)
        else:
            l = str2list(record.valueArr)
            if onceOnly:
                output = [ [] for i in l] # creates len(l) elements in output variable 
                onceOnly = False

            index = 0
            for i in l:
                output[index].append(i)
                index = index + 1

    return output



    

def getData(model , type , totalRecordstoReturn , duration = "Live" , start_date = None, end_date = None , aggregate = sum , ):

    if duration == "Live":
        return realtime(model , type , totalRecordstoReturn)
        
    # print("Duration and Type" , duration , type)
    records = model.objects.filter(type = type , created_at__range = (start_date , end_date)).order_by("-created_at")
    if duration == "1D":
        groups = itertools.groupby(records , lambda record : date_min(record.created_at))
    if duration == "1W":
        groups = itertools.groupby(records , lambda record : date_hour(record.created_at))
    if duration == "1M":
        groups = itertools.groupby(records , lambda record : date_hour(record.created_at))
    if duration == "year" or duration == "6M" or duration == "12M":
        groups = itertools.groupby(records , lambda record : date_days(record.created_at))

    output = []
    dateOutputs = []
    finalOutput = []
    
    for group , matches in groups:
        # print("Group is " , group)
        s = 0
        runOnce = True
        sumArr = []
        dateOutputs.append(str(group))

        for match in matches:
            
            if match.valueArr == None or match.valueArr == "":
                s = s + match.value
            else:
                l = str2list(match.valueArr)
                if runOnce:
                    sumArr = [0 for i in l]
                    runOnce = False
                sumArr = listsum(sumArr , l)
                
        output.append(sumArr)

    indexI = 0

    # [ [1,2,3] , [4,5,6] , [7,8,9] ] # output
    # [ [1 , 4 , 7] , [2 , 5 , 8] , [3 , 6 , 9] ] finalOutput
    for i in output[0]:
        finalOutput.append([ j[indexI] for j in output ])
        indexI = indexI + 1

    return finalOutput , dateOutputs


def fronendfunc(request , firstRun = 1 , duration = "Live" , type = ""):
    # cpuPercentage,usedRam,AvailRam,totalRam,usedSMemory,availSMemory,totalStorage,usedStorage,freeStorage = basicInfo()
    # temperature = get_cpu_temp()
    # process = running_process()   
    # iowat = iowatInfo()

    totalRecordsToReturn = (60 * 5) / 5 # 60 seconds * 10 aka 10 minutes divided by retrival time 
    mode = "multi"
    if firstRun == 0:
        totalRecordsToReturn = 1
        mode = "single"

    if type != "":
        day = 1
        if duration == "Live":
            print("Duration shouldnt be Live")
            return JsonResponse({"error" : True , "message" :"Duration shouldnt be Live"})
        elif duration == "1D":
            day = 1
        elif duration == "1W":
            day = 7
        elif duration == "1M":
            day = 30
        elif duration == "6M":
            day = 180
        elif day == "12M":
            day = 365
        
        startDate = DATETIME.datetime.today() - DATETIME.timedelta(days=day)
        endDate = DATETIME.datetime.today()
        data , dateGroups = getData(TestModal , type , totalRecordsToReturn , duration , start_date=startDate , end_date=endDate)
        # print(data)
        return JsonResponse({"error" : False , "mode" : mode , "data" : data , "dateGroups" : dateGroups})
    
    network = getData(TestModal , "network" , totalRecordsToReturn , duration)
    cpuUsage = getData(TestModal , "cpu" , totalRecordsToReturn , duration)
    cpuAvg = getData(TestModal , "cpuUtil" , 1 , duration)
    ram = getData(TestModal , "ram" , 1 , duration)
    iowait = getData(TestModal , "iowait" , 1 , duration)
    storage = getData(TestModal , "storage" , 1 , duration)
    swap = getData(TestModal , "swap" , 1 , duration)

    cpuLabels = []
    indexI = 0
    for i in cpuUsage:
        cpuLabels.append("Core " + str(indexI))
        indexI += 1
    # print("Function output" , cpuUsage)
    return JsonResponse({
        "error" : False , "mode" : mode ,
        "data" : 
        {
            "network" :{
                "data": network,
                # "labels": ["0"],
                "barlabel": ["Download", "Upload"]
                },
            "cpu" :{
                "data": cpuUsage,
                "barlabel": cpuLabels
                },
            "cpuUtil":{
                "data":cpuAvg,
                "labels": ["AVG"]
                },
            "ram":{
                "data":ram,
                "labels": ["Used", "Free"]
                },
            "swap":{
                "data" : swap,
                "labels" : ["Used" , "Available"],
                },
            "storage":{
                "data":storage,
                "labels": ["Used", "Available"]
                },
            "iowait":{
                "data":iowait,
                "labels": ["IOWAIT"]
                }
        }
        })



# for i in range(0 , 100):
#     l = [str(random.randint(0 , 100)) , str(random.randint(0 , 100)) , str(random.randint(0 , 100)) , str(random.randint(0 , 100)) , str(random.randint(0 , 100)) , str(random.randint(0 , 100)) , str(random.randint(0 , 100)) , str(random.randint(0 , 100))  ]
#     TestModal.objects.create(value = -1 , type="cpu" , valueArr = ",".join(l))
#     time.sleep(1)