import socket
from .models import DeviceCapibility, TempIPDevice
import os, re, ipcalc

import subprocess, platform

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


# def scan(addr):
#     s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#     socket.setdefaulttimeout(1)
#     result = s.connect_ex((addr,443))
#     if result == 0:
#         return 1
#     else :
#         return 0


def scan(addr):
    # if this EVER GIVES any issue ? then try replacing this with subprocess;. 
    # response = os.system("ping -c 1 -W 1 " + addr)

    if platform.system().lower() == "windows":
        response = os.popen(f"ping -n 1 {addr}").read()
        if "Destination host unreachable" in response or "Request timed out" in response:
            return False
        else:
            return True
    else:
        response = os.popen(f'ping -c 1 {addr}').read()
        if "1 received" in response:
            return True
        else:
            return False
    # param = '-n' if platform.system().lower()=='windows' else '-c'
    # response = os.system(f'ping {param} 1 {addr}')


        
def job(ip1,ip2,ip3,ip4,sub):
    print("<--Running Schedule Job-->\n--IP Scanning--")
    regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
    part_ip = f"{str(ip1)}.{str(ip2)}.{str(ip3)}.{str(ip4)}/{str(sub)}"
    print(part_ip)
    address = []
    if "/" in part_ip:
        try:
            for x in ipcalc.Network(part_ip):
                address.append(str(x))
        except:
            pass
    else:
        if(re.search(regex, part_ip)):
            address = [part_ip]

    # Scan IP Adresses
    for ip in address:
        if (scan(ip)):
            if DeviceCapibility.objects.filter(ip=ip).exists():
                obj, created = TempIPDevice.objects.update_or_create(host=ip,defaults={'status': True, 'action':False},)
            else:
                obj, created = TempIPDevice.objects.update_or_create(host=ip,defaults={'status': True, 'action':True},)
        else:
            obj, created = TempIPDevice.objects.update_or_create(host=ip,defaults={'status': False, 'action':False},)
    print("IP Scanning Complete")