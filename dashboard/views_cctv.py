import platform
from django.shortcuts import render
import numpy as np
import os, signal
import psutil
import threading
import subprocess
import time
import ctypes
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Product
import logging
from django_db_logger.models import StatusLog
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from .models import CameraMonitor
import requests
from django.core.paginator import Paginator, PageNotAnInteger, InvalidPage
from pathlib import Path
from .schedulejobs import scan
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))

THREAD_HOLDER = {}
RECORDING_THREAD_HOLDER = {}
LAST_SIGNAL_WHEN = 0
RUN_FUNCTION_TIME = 240 # 2 mins 
STOP_THREADS_WHEN_DIFF = 200 # 1 min 40 sec
SIGNAL_CHECK_RUNNING = False
CHECK_FOR_RUNNING_RECORDINGS = 5
RECORDING_CHECK_RUNNING = False

class Streaming(threading.Thread):
    def __init__(self, url , path , thread_name , thread_id , duration = None):
        threading.Thread.__init__(self)
        self.url = url
        self.path = path
        self.thread_name = thread_name
        self.thread_id = thread_id
        self.duration = duration
        self.sp = None

    def run(self):
        print(" ------------------------ Running Thread " + self.thread_name)
        if self.duration == None:
            # streaming
            print(" ------------------------ Streaming Started " + self.thread_name)
            # self.sp = subprocess.Popen("ffmpeg -loglevel quiet -rtsp_transport tcp -i "+ self.url +" -hls_time 2 -y " + self.path, shell=True) 
            self.sp = subprocess.Popen("ffmpeg -rtsp_transport tcp -i "+ self.url +" -hls_time 2 -y " + self.path, shell=True) 
        else:
            # recording
            print(" ------------------------ Recording Started " + self.thread_name)
            self.sp = subprocess.Popen("ffmpeg -loglevel quiet -rtsp_transport tcp -i "+ self.url +" -t " + self.duration + " -y " + self.path, shell=True) 
            

    def stopProcess(self):
        print(" ------------------------ Terminating Process " + self.thread_name)
        # self.sp.terminate()
        if platform.system().lower()=='windows':
            subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid = self.sp.pid))
        else:
            os.system("kill -9 %s"%self.sp.pid)
        # print(self.sp.pid)
        # p = psutil.Process(self.sp.pid)
        # p.terminate()  #or p.kill()


    def isRunning(self):
        if self.sp == None:
            return True
        if self.sp.poll() == None:
            # running
            return True
        else:
            # done running

            fileName = self.path.split("/")[-1]
            path = self.path[ : len(self.path) - len(fileName)]
            path = path + "completed-" + fileName

            os.rename(self.path , path)
            return False

        

    def raise_exception(self):
        print("Entered into exception")
        self.stopProcess()

        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(self.thread_id,ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(self.thread_id, 0)
            print('Exception raise failure')

        print(" ------------------------ Thread Ended " + self.name )







def checkLastSignal():
    global SIGNAL_CHECK_RUNNING
    global STOP_THREADS_WHEN_DIFF

    if len(THREAD_HOLDER) == 0:
        # print("Signal check ended")
        SIGNAL_CHECK_RUNNING = False
        stopAllStream()
        return

    SIGNAL_CHECK_RUNNING = True
    rn = time.time()

    print("Diff is " + str(rn - LAST_SIGNAL_WHEN))
    if LAST_SIGNAL_WHEN != 0 and rn - LAST_SIGNAL_WHEN >= STOP_THREADS_WHEN_DIFF:
        stopAllStream()
    
    # print("Signal check running")
    threading.Timer(RUN_FUNCTION_TIME , checkLastSignal).start()



def startLastSignalCheck(request = None):
    global LAST_SIGNAL_WHEN

    LAST_SIGNAL_WHEN = time.time()
    if not SIGNAL_CHECK_RUNNING: 
        checkLastSignal()

    if request != None:
        return JsonResponse({"error" : False , "message" : "success"})


@csrf_exempt
def startStream(request) :
    global LAST_SIGNAL_WHEN
    global SIGNAL_CHECK_RUNNING
    #ffmpeg -i rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4 -hls_time 2 -y index.m3u
    #ip = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4"

    # url format : rtps://admin:password@ip 
    url = request.POST.get("url")
    id = request.POST.get("id")

    id = str(id)

    if(not Path("media/cctv/").exists()):
        Path("media/cctv/").mkdir(parents=True , exist_ok=True)

    path = "media/cctv/" + id + "video" + id + ".m3u8"

    if id in THREAD_HOLDER.keys():
        print(" ------------------------ Thread with ID " + id + " Already exists")
    else:
        THREAD_HOLDER[id] = Streaming(url , path , "Thread Name " + id , id)
        THREAD_HOLDER[id].start()

    startLastSignalCheck()
    # if not SIGNAL_CHECK_RUNNING :
    #     LAST_SIGNAL_WHEN = time.time()
    #     checkLastSignal()
        
    return JsonResponse({"error" : False, "message" : path})

def stopStream(request , id):
    id = str(id)
    if id in THREAD_HOLDER.keys():
        THREAD_HOLDER[id].raise_exception()
        del THREAD_HOLDER[id]

    
    deleteAllFiles(id + "video")
    return JsonResponse({"error" : False, "message" : "Video stopped"})

def deleteAllFiles(matching = None , folder = "media/cctv/"):
    
    #folder = 'media/cctv/'
    matchingLen = 0
    if matching != None: 
        matchingLen = len(matching)

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if matching != None and matching == filename[ : matchingLen] :
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)

            elif matching == None:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            
        except Exception as err:
            print(str(err))

def stopAllStream():
    global THREAD_HOLDER
    for key in THREAD_HOLDER:
        THREAD_HOLDER[key].raise_exception()

    deleteAllFiles()
    THREAD_HOLDER = {}
 

def checkIfRecordingIsRunning():
    global RECORDING_CHECK_RUNNING

    if len(RECORDING_THREAD_HOLDER) == 0:
        RECORDING_CHECK_RUNNING = False
        print("No on going recording")
        return

    RECORDING_CHECK_RUNNING = True
    try:
        for key in RECORDING_THREAD_HOLDER.keys():
            if not RECORDING_THREAD_HOLDER[key].isRunning():
                print("Ending Thread " + key)
                RECORDING_THREAD_HOLDER[key].raise_exception()
                del RECORDING_THREAD_HOLDER[key]
                    
        print("Searching for ongoing recordings")
        threading.Timer(CHECK_FOR_RUNNING_RECORDINGS , checkIfRecordingIsRunning).start()
    except Exception as ex:
        print("Something went wrong")
        print("Searching for ongoing recordings")
        threading.Timer(CHECK_FOR_RUNNING_RECORDINGS , checkIfRecordingIsRunning).start()


@csrf_exempt
def startRecording(request) :
    #ffmpeg -i rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4 -hls_time 2 -y index.m3u
    #ip = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mp4"
    print("Running recording function")
    # url format : rtps://admin:password@ip 
    url = request.POST.get("url")
    id = request.POST.get("id")
    duration = str(request.POST.get("duration"))

    id = str(id)


    if(not Path("media/cctvrecording/").exists()):
        Path("media/cctvrecording/").mkdir(parents=True , exist_ok=True)

    path = "media/cctvrecording/" + id + "-video-" + str(int(time.time())) + ".avi"

    if id in RECORDING_THREAD_HOLDER.keys():
        print(" ------------------------ RECORDING Thread with ID " + id + " Already exists")        
        return JsonResponse({"error" : False, "message" : "This Camara is already under recording"})
    else:
        RECORDING_THREAD_HOLDER[id] = Streaming(url , path , "Thread Name " + id , id , duration)
        RECORDING_THREAD_HOLDER[id].start()


        if not RECORDING_CHECK_RUNNING:
            checkIfRecordingIsRunning()
        
    return JsonResponse({"error" : False, "message" : "Recording Started"})

@csrf_exempt
def stopRecording(request):
    file = str(request.POST.get("file"))
    id = str(request.POST.get("id"))
    
    try:
        print("trying to delete " + id + " file name " + file)
        if id in RECORDING_THREAD_HOLDER.keys():
            RECORDING_THREAD_HOLDER[id].raise_exception()
            del RECORDING_THREAD_HOLDER[id]
            time.sleep(5)
            deleteAllFiles(file, "media/cctvrecording/")
            return JsonResponse({"error" : False, "message" : "Video Stopped."})
        else:
            deleteAllFiles(file, "media/cctvrecording/")
            return JsonResponse({"error" : False , "message" : "Video Stopped."})
    except Exception as ex:    
        deleteAllFiles(file, "media/cctvrecording/")
        return JsonResponse({"error" : False, "message" : "Something went wrong"})

@csrf_exempt
def deleteRecording(request):
    file = str(request.POST.get("file"))
    # print(file)
    deleteAllFiles(file , "media/cctvrecording/")

    return JsonResponse({"error" : False , "message" : "Recording deleted successfully"})



def allRecordingAJAX(request):
    path = "media/cctvrecording/"
    recorderdata = os.listdir(path)
    # print(recorderdata)
    # data = []
    data = {
        "ongoing":[],
        "finished":[]
    }
    # data = {
    #     "data":[]
    #     }
    for value in recorderdata:
        # print(value)
        done = {}
        notDone = {}
        if value[ : 9 ] == "completed":
            # notDone["id"] = value.split('-')[1]
            notDone["value"] = value.split('.')[0]
            data["finished"].append(notDone)
        else:
            # done["id"] = value.split('-')[0]
            done["value"] = value.split('.')[0]
            data["ongoing"].append(done)
    return JsonResponse({"error" : False , "message" : "Fetched Records", "data":data})
    
def allRecording(request):
    # print(RECORDING_THREAD_HOLDER)
    
    # recordedData = []
    # path = "media/cctvrecording/"
    # recorderVideos = os.listdir(path)
    # for videos in recorderVideos:
    #     recordedData = videos.split('v')[0]
    # try:
    #     cctv = Product.objects.get(id=recorderVideos.split('v')[0])
    # except Exception as notFoundErr:
    #     print(str(notFoundErr))
    #     cctv = None
    # # id = re
    # context = {
    #     "data" : cctv,
    # }
    path = "media/cctvrecording/"
    recorderdata = os.listdir(path)[1:]
    # print(recorderdata)
    # data = []
    data = {
        "ongoing":[],
        "finished":[]
    }
    # data = {
    #     "data":[]
    #     }
    for value in recorderdata:
        # print(value)
        done = {}
        notDone = {}
        if value[ : 9 ] == "completed":
            notDone["id"] = value.split('-')[1]
            notDone["value"] = value.split('.')[0]
            data["finished"].append(notDone)
        else:
            done["id"] = value.split('-')[0]
            done["value"] = value.split('.')[0]
            data["ongoing"].append(done)
    # print(data)
    context = {
        "data" : data,
    }
    # return JsonResponse({"error" : False , "message" : "Recording deleted successfully", "data":data})
    return render(request, "dashboard/recordings.html", context)



@permission_required("dashboard.delete_cctv" , "/noperm/")
def delete_cctv(request, id):
    
    try:
        cctv = Product.objects.get(id=id)
        cctv.delete()
        msg = "Deleted Successfully"
        return redirect('cctv')
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/heatmap.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})



@login_required(redirect_field_name=None)
@permission_required("dashboard.delete_cctv" , "/noperm/")
def delete_camera(request, id):
    
    try:
        camera = CameraMonitor.objects.get(id=id)
        camera.delete()
        msg = "Deleted Successfully"
        return redirect('cctv')
    except Exception as e:
        db_logger.exception(e)
        path = request.path
        return render(request, "dashboard/heatmap.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})


def ip_camera_ajax_page(request):
    cameras = CameraMonitor.objects.filter().order_by("url")
    
    maxDataToShow = request.GET.get('max')
    if not maxDataToShow:
        maxDataToShow = 10
    paginator = Paginator(cameras, maxDataToShow)
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


def cctv_ajax_page(request):
    cameras = Product.objects.filter().order_by("-is_favorite")
    
    maxDataToShow = request.GET.get('max')
    if not maxDataToShow:
        maxDataToShow = 10
    paginator = Paginator(cameras, maxDataToShow)
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


def changeCCTVFav(request):
    id = int(request.GET.get("id"))
    isFavorite = request.GET.get("isFavorite")
    cam_type= request.GET.get("type") 
    print(id, isFavorite, cam_type)
    if cam_type == "CCTV":
        obj = CameraMonitor.objects.get(id=id)
    else:
        obj = Product.objects.get(id=id)
    if isFavorite == "False" or isFavorite == False or isFavorite == "false":
        obj.is_favorite = True
    else:
        obj.is_favorite = False
    obj.save()
    return JsonResponse({
        "error":False
    })




@login_required(redirect_field_name=None)
@permission_required("dashboard.view_cctv" , "/noperm/")
def cctv(request):
    if request.user.is_authenticated:   
        total_records_to_Show = 10
        camera_links = CameraMonitor.objects.filter().order_by("-is_favorite")
        cctv_links = Product.objects.filter().order_by("-is_favorite")

        camera_count = len(camera_links)
        cctv_count = len(cctv_links)

        camera_links = camera_links[:total_records_to_Show]
        cctv_links = cctv_links[:total_records_to_Show]

        if request.method == 'POST':
            if not request.user.has_perm("dashboard.add_cctv"):
                return redirect("@redirectloginurl")
            if request.POST.get("form_type") == 'formTwo':
                try:
                    if request.POST.get('name'):
                        cctv_websites = Product()
                        cctv_websites.name = request.POST.get('name')
                        cctv_websites.username = request.POST.get('username')
                        cctv_websites.password = request.POST.get('password')
                        cctv_websites.cameraname = request.POST.get('cname')
                        cctv_websites.save()
                        cameraTotal = 0
                        cameraDown = 0
                        cctvTotal = 0
                        cctvDown = 0
                        cameraObject = CameraMonitor.objects.filter().order_by("url")[:3]
                        for url in cameraObject:
                            try:
                                r = requests.get(url.url).status_code
                            except ConnectionError as err:
                                db_logger.exception(err)
                                r = 0
                            except requests.exceptions.RequestException as err:
                                db_logger.exception(err)
                                r = 0
                            if r == 200:
                                cameraTotal = cameraTotal + 1
                            else:
                                cameraDown = cameraDown + 1
                        cctvObject = Product.objects.all()
                        for url in cctvObject:
                            try:
                                r = scan(url.name)
                            except Exception as err:
                                db_logger.exception(err)
                                r = False
                            except requests.exceptions.RequestException as err:
                                db_logger.exception(err)
                                r = False
                            if r:
                                cctvTotal = cctvTotal + 1
                            else:
                                cctvDown = cctvDown + 1
                        context = {'cctv_links': cctv_links , "cctv_links_count" : cctv_count, "camera_cctv_count" : camera_count ,'camera_links':camera_links,'cameraTotal':cameraTotal,'cctvTotal':cctvTotal,'cameraDown':cameraDown,'cctvDown':cctvDown,'total_records_to_Show':total_records_to_Show}
                        return render(request, 'dashboard/cctv.html', context)
                except Exception as e:
                    db_logger.exception(e)
                    path = request.path
                    return render(request, "dashboard/cctv.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
            if request.POST.get("form_type") == 'formOne':
                try:
                    if request.POST.get('name'):
                        cctv_websites = CameraMonitor()
                        cctv_websites.url = request.POST.get('name')
                        cctv_websites.username = request.POST.get('username')
                        cctv_websites.password = request.POST.get('password')
                        cctv_websites.save()
                        cameraTotal = 0
                        cameraDown = 0
                        cctvTotal = 0
                        cctvDown = 0
                        cameraObject = CameraMonitor.objects.all()
                        for url in cameraObject:
                            try:
                                r = requests.get(url.url).status_code
                            except ConnectionError as err:
                                db_logger.exception(err)
                                r = 0
                            except requests.exceptions.RequestException as err:
                                db_logger.exception(err)
                                r = 0
                            if r == 200:
                                cameraTotal = cameraTotal + 1
                            else:
                                cameraDown = cameraDown + 1
                        cctvObject = Product.objects.all()
                        for url in cctvObject:
                            try:
                                r = scan(url.name)
                            except ConnectionError as err:
                                db_logger.exception(err)
                                r = False
                            except requests.exceptions.RequestException as err:
                                db_logger.exception(err)
                                r = False
                            if r == 200:
                                cctvTotal = cctvTotal + 1
                            else:
                                cctvDown = cctvDown + 1
                        context = {'cctv_links': cctv_links , "cctv_links_count" : cctv_count, "camera_cctv_count" : camera_count ,'camera_links':camera_links,'cameraTotal':cameraTotal,'cctvTotal':cctvTotal,'cameraDown':cameraDown,'cctvDown':cctvDown,'total_records_to_Show':total_records_to_Show}
                        return render(request, 'dashboard/cctv.html', context)
                except Exception as e:
                    db_logger.exception(e)
                    path = request.path
                    return render(request, "dashboard/cctv.html",{"exceptionRaise":"exceptionRaise","Curpath":path,"errTitle":"Page can't be opened",'errOutput':str(e)})
        else:
            cameraTotal = 0
            cameraDown = 0
            cctvTotal = 0
            cctvDown = 0
            cameraObject = CameraMonitor.objects.all()
            for url in cameraObject:
                try:
                    r = requests.get(url.url).status_code
                except ConnectionError as err:
                    db_logger.exception(err)
                    r = 0
                except requests.exceptions.RequestException as err:
                    db_logger.exception(err)
                    r = 0
                if r == 200:
                    cameraTotal = cameraTotal + 1
                else:
                    cameraDown = cameraDown + 1
            cctvObject = Product.objects.all()
            for url in cctvObject:
                try:
                    r = scan(url.name)
                except ConnectionError as err:
                    db_logger.exception(err)
                    r = False
                except requests.exceptions.RequestException as err:
                    db_logger.exception(err)
                    r = False
                if r == 200:
                    cctvTotal = cctvTotal + 1
                else:
                    cctvDown = cctvDown + 1
            context = {'cctv_links': cctv_links  , "cctv_links_count" : cctv_count, "camera_cctv_count" : camera_count , 'camera_links':camera_links,'cameraTotal':cameraTotal,     'cctvTotal':cctvTotal,'cameraDown':cameraDown,'cctvDown':cctvDown,'total_records_to_Show':total_records_to_Show}
            return render(request, 'dashboard/cctv.html', context)
    else:
        return redirect('/')
