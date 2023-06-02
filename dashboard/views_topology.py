from ncclient import manager
from pysnmp import hlapi
from dashboard import quicksnmp
import configparser
from .models import AddDevice, DeviceCapibility

import dashboard.topology.snmp.network_mapper



# # for netconf
# def getConfigNetconf(host , port , username,  password):

#     with manager.connect(host=host, port=port, username=username, password=password, hostkey_verify=False) as m:
#         intFilter = '''<interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces"> </interfaces>'''
#         reply = m.get_config('running', filter=('subtree', intFilter))

#         print(reply)

# for snmp
def getConfigSNMP(hosts , snmpCommunityStrings, types, subtype, category):
    content = """[DEFAULT]\nSnmpVersion = 2c\nSnmpCommunityString = [{0}]\nLogFile = dashboard/topology/snmp/NetworkMapper.log\nDebug = yes\n[DEVICES]\ndevices = [{1}]\n[TYPE]\ntypes = [{2}]\n[SUBTYPE]\ntypes = [{3}]\n[CATEGORY]\ntypes = [{4}]"""

    l = ', '.join(f'"{w}"' for w in hosts)
    l2 = ', '.join(f'"{w}"' for w in snmpCommunityStrings)
    l3 = ', '.join(f'"{w}"' for w in types)
    l4 = ', '.join(f'"{w}"' for w in subtype)
    l5 = ', '.join(f'"{w}"' for w in category)

    content = content.format(l2 , l, l3, l4, l5)

    print(l , l2, l3)
    config = open('dashboard/topology/snmp/config.ini' , "w")
    config.write(content)
    config.close()

    dashboard.topology.snmp.network_mapper.main_with_args()






def mainFunction():
    devices = DeviceCapibility.objects.all()
    all_devices = AddDevice.objects.all()
    snmpDevices = []
    snmpCommunityStrings = []
    types = []
    subtype = []
    category = []

    for device in devices:
        thisIP = device.ip
        isSnmp = device.is_snmp

        if isSnmp : 
            for d in all_devices:
                ip = str(d.IP_Address_col1) + "." + str(d.IP_Address_col2) + "." + str(d.IP_Address_col3) + "." + str(d.IP_Address_col4)
                if (thisIP == ip):
                    snmpDevices.append(ip)
                    snmpCommunityStrings.append(device.commString)
                    types.append(d.type_of_device) # Network, Server, VMS, LB, Storage, etc
                    subtype.append(d.network_device_category) # Router, Switch
                    category.append(d.network_sub_category) # AX, CORE, ToR, etx
                    break
            
        else: 
            print("Invalid Device")
    getConfigSNMP(snmpDevices, snmpCommunityStrings, types, subtype, category)



 
    

