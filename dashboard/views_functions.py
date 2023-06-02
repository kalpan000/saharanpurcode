import plotly
import glob
import json
import os
import pandas as pd
import plotly.express as px
import numpy as np
import xmltodict
import ruamel.yaml
import pygal
from .models import DataCenterState
from socket import *
import time
import requests
from . import views_snmp
from ncclient import manager
from pysnmp import hlapi
from .models import addDataCenter
import logging
try:
    db_logger = logging.getLogger('django')
except Exception as err:
    print(str(err))


class CapabilityModules(object):
    def __init__(self):
        pass

    def restconf(self, router, port):
        try:
            myheaders = {'content-type': 'application/json-rpc'}
            l = "show run"
            print(l)
            payload = [
                {
                    "jsonrpc": "2.0",
                    "method": "cli",
                    "params": {
                        "cmd": l,
                        "version": 1
                    },
                    "id": 1
                }
            ]
            # print(payload)
            response = requests.post(router["ip"], data=json.dumps(
                payload), headers=myheaders, auth=(router["user"], router["password"])).json()

            # date_time = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
            return (200, response)
            # return (response.status_code, "Success!")
        except Exception as e:
            db_logger.exception(e)
            return (500, f"system error occuered! Error is {e}")

    def netconf(self, router, port):
        # https://ncclient-fredgan.readthedocs.io/_/downloads/en/sphinx_version/pdf/
        try:
            with manager.connect(host=router["ip"], port=port, username=router["user"], password=router["password"], hostkey_verify=False) as connection:
                if router["functionname"] == "capabilities":
                    resp = connection.get_capabilities
                    return (200, str(resp))
                elif router["functionname"] == "config":
                    resp = connection.get_config(source='running')
                    return (200, str(resp))

                resp = connection.get_config(source='running')

            return (200, json.dumps(xmltodict.parse(resp)))
        except Exception as e:
            db_logger.exception(e)
            return (500, f"system error occuered! Error is {e}")

    def snmpconf(self, router, port):
        try:
            # print(router["ip"],router["communitystring"])
            res = views_snmp.runthis(router["ip"], "none", port)
            return (200, res)
        except Exception as e:
            db_logger.exception(e)
            return (500, f"Server Error! Error is:{e}")


# class AssetsFormsVF():
#     def __init__(self):
#         pass

#     def d_s_return(self):
#         # countries = DataCenterCountry.objects.all()
#         states = DataCenterState.objects.all()
#         return states

#     def hostscan(self, target, port):
#         """
#         Accepts IP Address
#         Then check for the 830 Port
#         return port status(Open or closed) and Time Taken in scanning
#         """
#         try:
#             startTime = time.time()
#             t_IP = gethostbyaddr(target)
#             print(t_IP[0])
#             s = socket(AF_INET, SOCK_STREAM)
#             conn = s.connect_ex((t_IP[0], port))
#             s.close()
#             if(conn == 0):
#                 return ("Port is opened", time.time() - startTime)
#             else:

#                 return ("Port is not opened", time.time() - startTime)
#         except Exception as e:
#             db_logger.exception(e)
#             # print("port can't be scanned due to error:{}".format(e,) , time.time() - startTime)
#             return ("port can't be scanned due to error:{}".format(e,), time.time() - startTime)


# def world_map():
#     worldmap_chart = pygal.maps.world.World(tooltip_border_radius=10)
#     worldmap_chart.title = 'Data Center In All Countries'
#     context = {}
#     # data = DataCenterCountry.objects.all()
#     # for i in data:
#     #     context[i.country_code] = int(i.capacity)

#     graphs_values = [{
#         'value': ('in', context.pop("in")),
#         'label': 'This is the fifth',
#         'xlink': {
#             'href': 'http://127.0.0.1:8000/assets/india/',
#             'target': '_parent'
#         }
#     }]

#     worldmap_chart.add('World', context)
#     worldmap_chart.add('India', graphs_values)
#     world_map = worldmap_chart.render_data_uri()
#     return world_map


#sankey_graph = sankey()
#india_map_plt = india_map()


# def indian_map():

#     this_dir = os.path.dirname(os.path.abspath('__file__'))
#     geofile_url = os.path.join(this_dir, "dashboard", "states_india.geojson")

#     indian_states_geojson = json.load(open(geofile_url))

#     df = pd.DataFrame(list(addDataCenter.objects.all().values(
#         'Add_state', 'Capacity_in_MW', 'sqr_mtr', 'DataCenterName')))
#     state_id_map = {}
#     df["Capacity"] = pd.to_numeric(df["Capacity_in_MW"])
#     df["Sqr Mtr"] = pd.to_numeric(df["sqr_mtr"])
#     for feature in indian_states_geojson["features"]:
#         feature["id"] = feature["properties"]["state_code"]
#         state_id_map[feature["properties"]["st_nm"]] = feature["id"]

#     df["id"] = df["Add_state"].apply(lambda x: state_id_map[x])
#     # df["CapacityScale"] = np.log10(df["capacity"])
#     # print(df[:3])
#     india_fig = px.choropleth(
#         df,
#         geojson=indian_states_geojson,
#         locations="id",
#         hover_name="Add_state",
#         hover_data=["DataCenterName", "Capacity", "Sqr Mtr"],
#         width=1000,
#         # projection='natural earth',
#         color="Capacity",

#     )
#     # print(str(dir(india_fig)), end="$"*100)

#     india_fig.update_layout(
#         margin={"r": 0, "t": 0, "l": 0, "b": 0}, coloraxis_showscale=False)
#     india_fig.update_geos(fitbounds="locations", visible=False)
#     # india_fig.update_annotations(text="<a href='https://google.com' target='_blank'>Testing</a>")
#     # india_fig.on_click(do_click)
#     # india_fig.add_annotation(text="<a href='http://google.com' target='_blank' style='color:black;'>Visit Delhi Data Center1</a>", hovertext="Delhi DC1",x=0.2,y=0.2)
#     # india_fig.add_annotation(text="<a href='http://google.com' target='_blank' style='color:black;'>Visit Delhi Data Center2</a>", hovertext="Delhi DC2",x=0.2,y=0.3)
#     # indian_states_geojson["features"][0]["geometry"]["coordinates"][0][0]

#     config = {'displayModeBar': False}
#     india_map_plt = plotly.offline.plot(
#         india_fig, show_link=False, config=config, output_type='div')
#     return india_map_plt


# def do_click(trace, points, state):
#     if points.point_inds:
#         ind = points.point_inds[0]
#         url = df.link.iloc[ind]
#         webbrowser.open_new_tab(url)

        # scatter


#####################################################################################################
# import webbrowser                                                                                 #
# import pandas as pd                                                                               #
# import plotly.graph_objs as go                                                                    #
# df = pd.DataFrame({'x': [1, 2, 3],                                                                #
#                    'y': [1, 3, 2],                                                                #
#                    'link': ['https://google.com', 'https://bing.com', 'https://duckduckgo.com']}) #
#                                                                                                   #
# fig = go.FigureWidget(layout={'hovermode': 'closest'})                                            #
# scatter = fig.add_scatter(x=df.x, y=df.y, mode='markers', marker={'size': 20})                    #
#                                                                                                   #
# def do_click(trace, points, state):                                                               #
#     if points.point_inds:                                                                         #
#         ind = points.point_inds[0]                                                                #
#         url = df.link.iloc[ind]                                                                   #
#         webbrowser.open_new_tab(url)                                                              #
#                                                                                                   #
# scatter.on_click(do_click)                                                                        #
# fig                                                                                               #
#####################################################################################################


# def saveServerInformation(u , data , func) :


#     #cap = (yaml.safe_load(capabilities))
#     #cap = "ASDF"

#     # if(func == "capabilities"):
#     #     yaml = ruamel.yaml.YAML(typ='safe')
#     #     d = yaml.load(data)
#     #     data = json.dump(d)
#     if(func == "config"):
#         data = json.dumps(xmltodict.parse(data))


#     # with open(f"/serverResponse/{time.time()} {func}","w") as f:
#     #     f.write(str(data))

#     obj = ServerData(user_id = u , server_data = data , function_name = func)
#     obj.save()

#     return data
