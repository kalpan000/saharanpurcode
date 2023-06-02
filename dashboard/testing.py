import subprocess
import datefinder

def get_syslog():
    return subprocess.check_output("cat /var/log/syslog".split(" ") , stderr= subprocess.STDOUT).decode("utf-8").split("\n")[-1000 : 0]
    
    
def get_kernlog():
    return subprocess.check_output("cat /var/log/kern.log".split(" ") , stderr= subprocess.STDOUT).decode("utf-8").split("\n")[-1000 : 0]

def get_authlog():
    return subprocess.check_output("cat /var/log/auth.log".split(" ") , stderr= subprocess.STDOUT).decode("utf-8").split("\n")[-1000 : 0]



a = ["Jun 23 04:46:58 hawk systemd[1]: startServer.service: Failed with result 'exit-code'." , "Jun 23 04:46:58 hawk systemd[1]: startServer.service: Failed with result 'exit-code'." , "Jun 23 04:46:58 hawk systemd[1]: startServer.service: Failed with result 'exit-code'." , "Jun 23 04:46:58 hawk systemd[1]: startServer.service: Failed with result 'exit-code'." , "Jun 23 04:46:58 hawk systemd[1]: startServer.service: Failed with result 'exit-code'." , "Jun 23 04:46:58 hawk systemd[1]: startServer.service: Failed with result 'exit-code'." , "Jun 23 04:46:58 hawk systemd[1]: startServer.service: Failed with result 'exit-code'." , "Jun 23 04:46:58 hawk systemd[1]: startServer.service: Failed with result 'exit-code'."]


def get_logs(request , type = "sys"):

    logList = []
    if type == "sys":
        logList = get_syslog()
    elif type == "kern":
        logList = get_kernlog()
    else:
        logList = get_authlog()


    output = []

    for i in logList:
        dates = list(datefinder.find_dates(i))
        if len(dates) > 0:
            output.append({
                "date" : dates[0].strftime("%m/%d/%Y, %H:%M:%S"),
                "log" : i
            })
        else:
            output.append({
                "date" : "",
                "log" : i
            })


    data = {
        "data" : output
    }
    
    return JsonResponse(data)



output = []

logList = a

for i in logList:
    dates = list(datefinder.find_dates(i))
    if len(dates) > 0:
        output.append({
            "date" : dates[0].strftime("%m/%d/%Y, %H:%M:%S"),
            "log" : i
        })
    else:
        output.append({
            "date" : "",
            "log" : i
        })

# found = list(datefinder.find_dates(a))
print(output)
