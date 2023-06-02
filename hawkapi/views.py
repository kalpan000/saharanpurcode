from .serializers import *
from dashboard.models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from dashboard.models import DeviceCapibility
from dashboard.views_nms import runssh
# Create your views here.

class InformationView(APIView):
    def get(self, request, *args, **kwargs):
        dc = DeviceCapibility.objects.all()
        cctv = Product.objects.all()
        website = WebsiteLinks.objects.all()
        device = AddDevice.objects.all()
        dcData = DeviceCapabilitiSerializer(dc, many=True)
        cctvData = CCTVSerializer(cctv, many=True)
        webData = WebsiteSerializer(website, many=True)
        deviceData = DeviceSerializer(device, many=True)
        data = {
            "dc" : dcData.data,
            "device": deviceData.data,
            "cctv": cctvData.data,
            "website": webData.data
        }
        return Response(data, status=status.HTTP_200_OK)

class TerminalView(APIView):
    def get(self, request, *args, **kwargs):
        obj = DeviceCapibility.objects.get(ip = request.GET["ip"])
        cmd = request.GET["cmd"]
        try:
            sshclient = runssh(obj.ip,obj.user, obj.pwd,22)
            stdin, stdout, stderr = sshclient.exec_command(cmd)
            stat = stdout.channel.recv_exit_status()
            # if (input):
            #     stdin.write(input)
            #     stdin.flush()
            stat = stdout.channel.recv_exit_status()    
            if (stat == 0):
                res = stdout.read().decode('utf-8')
            else:
                res = str(stderr.read().decode('utf-8'))  
        except Exception as err:
            res = str(err)
        # TerminalLog.objects.create(cmd=cmd,output=res, device=str(obj.ip),user="Utility")

        data = {
            "result": res
        }
        return Response(data, status=status.HTTP_200_OK)

    # def post(self):
    #     pass