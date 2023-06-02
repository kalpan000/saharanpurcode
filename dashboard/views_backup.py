from sys import stdout
from django.core.management import call_command 
from optparse import OptionParser
from django.http import JsonResponse
from django.shortcuts import render
import os
from django.utils.decorators import method_decorator    
from django.contrib.auth.decorators import permission_required
from .views_ftp import uploadDBFIles


def backupDB(request , name):
    try:
        if not request.user.has_perm("dashboard.add_settings"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        # parser = OptionParser()
        # parser.add_option("-f", dest="output_filename", help="backup filename")
        with open("media/dbbackups/"+name+".json", 'w', encoding='utf-8') as my_file:
            call_command("dumpdata" , stdout = my_file)

        return JsonResponse({"error" : False, "message" : "Backup Successful"})
    except Exception as err:
        print("Error " + str(err))
        
        return JsonResponse({"error" : True, "message" : "Something went wrong" , "error" : err})

def factoryReset(requst):
    try:
        call_command("flush" , interactive=False)
        return JsonResponse({"error" : False, "message" : "Database has been reset"})
    except Exception as err:
        return JsonResponse({"error" : True, "message" : "Something went wrong" , "error" : err})


def restoreDB(request , name):
    try:
        if not request.user.has_perm("dashboard.add_settings"):
            return JsonResponse({"error" : True , "redirectError" : "noperm"})
        checked = request.GET["checked"]
        # print("checked is " + checked)
        msg = ""
        # print("error here")
        if checked == "true":
            # print("error here 2")
            
            try:
                call_command("flush" , interactive=False)
                msg = "Database has been reset and "
            except Exception as err:
                return JsonResponse({"error" : True, "message" : "Something went wrong" , "error" : err})



        # print("error here 4")
        # parser = OptionParser()
        # parser.add_option("-i", dest="input_filename", help="restore backup filename")
        call_command("loaddata" , "media/dbbackups/"+name)
        return JsonResponse({"error" : False, "message" : msg + "Restore Successful"})
    except Exception as err:
        return JsonResponse({"error" : True, "message" : "Something went wrong" , "error" : err})

@permission_required("dashboard.view_settings" , "/noperm/")
def loadTemplate(request):
    text_files = [f for f in os.listdir("media/dbbackups") if f.endswith('.json')]
    data = {
        "files" : text_files,
    }
    return render(request, "dashboard/backupandrestore.html" , data)