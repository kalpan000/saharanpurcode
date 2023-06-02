from io import BytesIO #A stream implementation using an in-memory bytes buffer
                       # It inherits BufferIOBase
 
from django.http import HttpResponse
from django.template.loader import get_template
 
#pisa is a html2pdf converter using the ReportLab Toolkit,
#the HTML5lib and pyPdf.
 
from xhtml2pdf import pisa  
#difine render_to_pdf() function

def removeSpacesFromRow(row , ignoreFirstRow = False):    
    row = row.split(" ")
    output = []
    for item in row:
        if item != "":
            output.append(item)  

    if output[0][-1] == ":":
        output[0] = output[0][:-1]      
    return output    
def fan_rate():
    return 0

def memory(data):
    data = data.split("\n")
    output = []
    for row in data[:17]:
        output.append(removeSpacesFromRow(row))

    finalOutput = {}
    index = 0
    for item in output:
        if item[0].lower() == "swaptotal":
            finalOutput["swapTotal"] = int(output[index][1])
        
        elif item[0].lower() == "swapfree":
            finalOutput["swapFree"] = int(output[index][1])

        elif item[0].lower() == "memtotal":
            finalOutput["total"] = int(output[index][1])
        
        elif item[0].lower() == "memfree":
            finalOutput["free"] = int(output[index][1])
        
        index += 1

    finalOutput["used"] = finalOutput["total"] - finalOutput["free"]
    finalOutput["swapUsed"] = finalOutput["swapTotal"] - finalOutput["swapFree"]

    try:
        finalOutput["used%"] = (finalOutput["used"] / finalOutput["total"]) * 100
        finalOutput["swapUsed%"] = (finalOutput["swapUsed"] / finalOutput["swapTotal"]) * 100
    except:
        finalOutput["used%"] = 0
        finalOutput["swapUsed%"] = 0 
    
    return finalOutput
  

def storage(data):
    data = data.split("\n")[:-1]
    firstRun = True
    output = []
    for row in data:
        if firstRun:
            firstRun = False
            continue        
        rowArray = row.split(" ")
        correctRow = []

        for item in rowArray:
            if item != "":
                correctRow.append(item)
        
        if correctRow[0] != "root" and correctRow[0] != "rootfs" and correctRow[0] != "none" and correctRow[0] != "tmpfs":
            output.append({"name" : correctRow[0] , "total" : (int(correctRow[2]) + int(correctRow[3])) , "used" : int(correctRow[2]) , "available" : int(correctRow[3]) , "used%" : float(correctRow[4][:-1]) })    

    return output      

def cpu(data):
    data = data.split("\n")

    cpuAvg = removeSpacesFromRow(data[0])
    temp = sum( list(map(int , cpuAvg[1:])) )
    try:
        idle = (int(cpuAvg[4]) * 100) / temp
    except:
        idle = 0
    cpuUsage = 100 - idle
    totalProcess = 0
    runningProcess = 0
    cores = {}
    iowait = 100 / float(cpuAvg[5])

    data = data[1:]
    index = 0
    for row in data:
        if row[:3] == "cpu":
            cpuAvg = removeSpacesFromRow(row)
            temp = sum( list( map(int , cpuAvg[1:]) ) )
            try:
                cores["core "+str(index)] = round(100 - (int(cpuAvg[4]) * 100 / temp) , 2)
            except:
                continue
            index = index + 1

        elif row[:7] == "process":
            totalProcess = removeSpacesFromRow(row)[1]
        elif row[:13] == "procs_running":
            runningProcess = removeSpacesFromRow(row)[1]  


    return {"used" : round(cpuUsage , 2) , "totalProcess" : int(totalProcess) , "runningProcess" : int(runningProcess) , "iowait" : iowait , "cores" : cores}

def systeminfo(data):
    data = data.split("\n")
    data = data[0].split(" ")
    # return {"kernalname":data[0], "host":data[1], "release":data[2], "version":data[3]+" "+data[4]+" "+data[5]+" "+data[6]+" "+data[7]+" "+data[8]+" "+data[9], "machine": data[10], "processor":data[11], "platform":data[12], "os":data[13]}
    return {"kernalname":data[0], "host":data[1], "release":data[2], "version":data[3], "machine": data[10], "processor":data[11], "platform":data[12], "os":data[13]}

def uptime(data):
    data = data.split("\n")
    arr = data[0].split(" ")
    return {"uptime" : str(arr[0]).replace(".","")}
    
def network(data):
    data = data.split("\n")[2:-1]
    output = []
    for row in data:
        t = removeSpacesFromRow(row)
        output.append({
            "name" : t[0][:-1],
            "rbytes" : int(t[1]),
            "rpackets" : int(t[2]),
            "sbytes" : int(t[9]),
            "spackets" : int(t[10]),
        })
    return output

def loadavg(data):
    data = data.split(" ")
    return {"one":float(data[0]), "five":float(data[1]), "fifteen":float(data[2])}

def cpu_temp(data):
    try:
        start = '+'
        end = '°C  ('
        s = data.split("\n")[2]
        return s[s.find(start)+len(start):s.rfind(end)]
    except Exception as err:
        return 0

        
def render_to_pdf(template_src, context_dict={}):
     template = get_template(template_src)
     html  = template.render(context_dict)
     result = BytesIO()
 
     #This part will create the pdf.
     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
     if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     return None