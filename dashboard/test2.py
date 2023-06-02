from re import L
from black import out


data = {
  "DC-DELHI": {
    "Server": [
      "192.168.1.40",
      "192.168.1.123",
      "127.0.0.1",
      "192.168.1.120"
    ],
    "network": [
      "192.168.1.110159",
      "177.17.0.1159",
      "156.65.57.9159"
    ]
  },
  "DC-MUMBAI": {
    "Server": [
      "192.168.1.1101",
      "177.17.0.11",
      "156.65.57.91"
    ],
    "network": [
      "192.168.1.11015",
      "177.17.0.115",
      "156.65.57.915"
    ]
  },
  "DC-KERELA": {
    "Server": [
      "192.1638.1.1101",
      "177.147.0.11",
      "156.615.57.91"
    ],
    "network": [
      "192.168.13.11053",
      "177.17.0.115532",
      "156.65.257.915"
    ]
  },
  "DC-PUNJAB": {
    "Server": [
      "1922.1638.1.1101",
      "1737.147.0.11",
      "1546.615.57.91"
    ],
    "network": [
      "13192.168.13.11053",
      "11177.17.0.115532",
      "12256.65.257.915"
    ]
  },
}

def getProperResponse(data):
	output = {"nodes": [], "links": []}

	for dc in data:

		output["nodes"].append({"id": dc, "name": dc, "type": "datacenter"})

		output["nodes"].append({"id" : dc + "network" , "name" : dc + "network" , "type" : "networktype"})
		output["nodes"].append({"id" : dc + "server" , "name" : dc + "server" , "type" : "servertype"})

		output["links"].append({"source" : dc + "network" , "target" : dc , "type" : "networktype"}) 
		output["links"].append({"source" : dc + "server" , "target" : dc , "type" : "servertype"}) 
		
		
		
		for type in data[dc]:
			for ip in data[dc][type]:

				output["nodes"].append({"id" : ip , "name" : ip , "type" : type.lower()})

				if type == "network":
					output["links"].append({"source" : dc + "network" , "target" : ip , "type" : type.lower()}) 
				else:
					output["links"].append({"source" : dc + "server" , "target" : ip , "type" : type.lower()}) 

		
	lastDC = None
	for node in output["nodes"]:

		if node["type"] == "datacenter":
			if lastDC != None:
				output["links"].append({"source" : node["id"] , "target" : lastDC["id"] , "type" : "datacenter"}) 
			lastDC = node

	if lastDC != None:
		output["links"].append({"source" : lastDC["id"] , "target" : output["nodes"][0]["id"] , "type" : "datacenter"}) 

	return output



data = {
	
	"192.168.1.1" : {
		"type" : "network"
	},
	"192.168.1.7" : {
		"type" : "network"
	},
	"192.168.1.8" : {
		"type" : "server"
	},
	"192.168.1.9" : {
		"type" : "server"
	},
	"192.168.1.10" : {
		"type" : "network"
	}

}



def makeConnections(data):
	
	output = {"nodes" : [] , "links" : []}
	lastNodeIP = None

	for ip in data:
		output["nodes"].append( {"ip" : ip , "type" : data[ip]["type"]} )
		

		if lastNodeIP != None:
			output["links"].append(  {"from" : ip , "to" : lastNodeIP} )

		lastNodeIP = ip

	
	a = list(data.items())

	firstDeviceIP = a[0][0]
	lastDeviceIP = a[-1][0]

	output["links"].append( {"from" : firstDeviceIP , "to" : lastDeviceIP} )

	return output

print(makeConnections(data))
# print(getProperResponse(data))
# print(output)