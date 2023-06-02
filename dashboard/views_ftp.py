import ftplib
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pysftp
from .models import StartApp


class FTP_HANDLER:

    def __init__(self , host , username , password , path , type = "sftp"):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = None
        # absolute path
        if path[0] != "/":
            path = "/" + path

        self.path = path

        self.type = type

    def connect(self):

        try:
            if self.type == "sftp":
                print("Trying SFTP")
                cnopts = pysftp.CnOpts()
                cnopts.hostkeys = None  
                # cnopts.knownhosts='known_hosts'

                srv = pysftp.Connection(host=self.host, username=self.username, password=self.password, cnopts=cnopts)
                srv.chdir(self.path)
                
                self.ftp = srv
                
            else:
                ftp = ftplib.FTP(self.host)
                ftp.login(user=self.username , passwd=self.password)
                ftp.cwd(self.path)
                self.ftp = ftp

            return False , {"error" : False, "message" : "connection successful"}
        except Exception as ex:
            self.ftp = None
            return True , {"error" : True, "message" : "Unable to establish connection to the FTP server. "+str(ex) , "errorMessage" : str(ex)}


    def reconnect(self):
        return self.connect()

    def upload(self , fileToUploadPath):
        
        try:
            # file path is relative here 
            if self.type == "sftp":
                print("uploading SFTP" , fileToUploadPath)
                self.ftp.put(fileToUploadPath)
            else:
                file = open(fileToUploadPath , "rb")
                name = os.path.basename(file.name)
                self.ftp.storbinary(name , file)

            return False , {"error" : False, "message" : "Upload Success"}
            
        except FileNotFoundError as err:
            return True , {"error" : True, "message" : "File not found" , "errorMessage" : str(err) }

        except Exception as err:
            # file.close()
            return True , {"error" : True, "message" : "Unable to upload. "+str(err) , "errorMessage" : str(err) }


    def close(self):
        try:
            if self.type == "sftp":
                self.ftp.close()
            else :
                self.ftp.quit()

            return False , {"error" : False , "message" : "Connectiion closed"}
        except Exception as err:
            return True , {"error" : True , "message" : "Unable to close connection. "+str(err) , "errorMessage" : str(err)}

@csrf_exempt
def uploadFile(request):

    host = request.POST.get("host",  "")
    username = request.POST.get("username" , "")
    password = request.POST.get("password" , "")
    path = request.POST.get("path" , "")
    type = request.POST.get("type" , "sftp")
    # fileToUploadPath = request.POST.get("filePath" , "")
    if path == "" or username == "" or password == "" or host == "":
        # obtain this info from DB
        return JsonResponse({"error" : True , "message" : "All fields are mandatory"})

    obj = StartApp.objects.get(id = 1)
    obj.nfs_host = host
    obj.nfs_user = username
    obj.nfs_pwd = password
    obj.nfs_loc = path
    obj.nfs_file = "/home/hawk/appliance.sh"
    obj.save()
    return JsonResponse({"error" : False , "message" : "Network Storage Data Saved."})
        
    # # fileToUploadPath = "/home/hawk/appliance.sh"
    # print(host , username , password , path , type , fileToUploadPath)
    # ftp = FTP_HANDLER(host , username , password , path , type)
    
    # error , msg = ftp.connect()
    # if error:
    #     return JsonResponse(msg)

    # error , msg = ftp.upload(fileToUploadPath)
    # if error:
    #     return JsonResponse(msg)

    # return JsonResponse(msg)

def uploadDBFIles(request, file):
    obj = StartApp.objects.get(id=1)
    host = obj.nfs_host
    username = obj.nfs_user
    password = obj.nfs_pwd
    path = obj.nfs_loc

    fileToUploadPath = "/home/hawk/AkusITSolutions/media/dbbackups/"+file+".json"

    if path == "" or username == "" or password == "" or host == "":
        return JsonResponse({"error" : True , "message" : "All fields are mandatory"})

    ftp = FTP_HANDLER(host , username , password , path)
    
    error , msg = ftp.connect()
    if error:
        return JsonResponse(msg)

    error , msg = ftp.upload(fileToUploadPath)
    if error:
        return JsonResponse(msg)

    return JsonResponse(msg)