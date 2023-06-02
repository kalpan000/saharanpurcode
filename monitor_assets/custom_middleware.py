import imp
from wsgiref.util import request_uri
from dashboard.models import UserProfile
import re
from django.shortcuts import render, HttpResponse
from django.shortcuts import redirect
from django.http import JsonResponse, response

class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # print("USer is " , request.user.id)
        if request.user.id == None:    
            response = self.get_response(request)
            # Code to be executed for each response after the view is called
            return response
        
        profile = None
        userType = None
        try:
            profile = UserProfile.objects.get(user=request.user)
            userType = profile.staff_type
        except Exception as ex:
            response = self.get_response(request)
            # Code to be executed for each response after the view is called
            return response


        requestedURL = request.path

        if len(requestedURL) > 1:
            if requestedURL[0] == "/":
                requestedURL = requestedURL[1:]
            
            if requestedURL[-1] == "/":
                requestedURL = requestedURL[:-1]

        requestType = request.method
        isAjax = False

        requested_html = re.search(r'^text/html', request.META.get('HTTP_ACCEPT'))
        if not requested_html:
            isAjax = True


        # print("Perm" , userType , "requestType" , requestType , isAjax  , "requestedURL" , requestedURL)

        DCNotAllowed = ["asset/datacenter/hall/delete" , "web/monitoring/delete" , "deleterecordings" , "cctv/delete/camera" , 
        "cctv/delete/cctv" , "notificationDelet" , "asset/datacenter/information/hall/device/delete" , 
        "device/capability/delete" , "asset/datacenter/information/hall/delete" , "asset/forms/device/delete" , 
        "deleterecordings" , "backupandrestore/backup" , "backupandrestore/restore" , "backupandrestore/reset"]

        # started from 41
        staffNotAllowed = ["deleterecordings"  , "asset/forms/add" , "backupandrestore/backup", "asset/forms/post" ,
        'asset/forms/add/schedule', 'asset/forms/add/addcap', 'asset/forms/add/datacenter', 'asset/forms/add/row', 
        'asset/forms/add/rack', 'asset/forms/add/device', 'asset/forms/add/devicetemplate' , "asset/forms/rack/edit" , 
        "device/capability/edit" , "asset/forms/edit/datacenter"]

        staffNotAllowed = staffNotAllowed + DCNotAllowed

        if requestedURL == "noperm" or requestedURL == "" or requestedURL == "/":
            pass

        elif userType == "STAFF" :
            for url in staffNotAllowed:
                modifiedURL = requestedURL.split("/")[:-1]
                if len(modifiedURL) == 0:
                    modifiedURL = requestedURL
                else: modifiedURL = "/".join(modifiedURL)

                if requestedURL == url or modifiedURL == url:
                    print("Staff Not Allowed for URL" , requestedURL , "modified" , modifiedURL)
                    if isAjax:
                        return JsonResponse({"error" : True , "redirectError" : True , "data" : "User is not authorized to access this function."})
                    return redirect("/noperm/")
            
        elif userType == "DC" :
            for url in DCNotAllowed:
                modifiedURL = requestedURL.split("/")[:-1]
                if len(modifiedURL) == 0:
                    modifiedURL = requestedURL
                else: modifiedURL = "/".join(modifiedURL)

                if requestedURL == url or modifiedURL == url:
                    print("DC Not Allowed for URL" , requestedURL , "modified" , modifiedURL)
                    if isAjax:
                        return JsonResponse({"error" : True , "redirectError" : True , "data" : "User is not authorized to access this function."})
                    return redirect("/noperm/")
        
        response = self.get_response(request)
	    # Code to be executed for each response after the view is called
        return response