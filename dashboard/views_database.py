from itertools import count
from django.http import JsonResponse
from django.shortcuts import render
import psycopg2
from django.views.decorators.csrf import csrf_exempt
from .models import AddDevice, DeviceCapibility
from django.contrib.auth.decorators import permission_required
from datetime import datetime

ALL_TABLES = "SELECT count(*) as total_tables FROM pg_stat_all_tables"
ALL_DATABASES = "SELECT count(*) as total_database FROM pg_stat_database"


DATABASE_DETAILS = "SELECT * FROM pg_stat_database"

QUERY = """SELECT datname, pid, state, query FROM pg_stat_activity WHERE state <> 'idle' AND query NOT LIKE '% FROM pg_stat_activity %' AND query NOT LIKE '% FROM pg_stat_database %'"""
# TABLE_SIZES = """SELECT nspname || '.' || relname AS "relation",
#     pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
#   FROM pg_class C
#   LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
#   WHERE nspname NOT IN ('pg_catalog', 'information_schema')
#     AND C.relkind <> 'i'
#     AND nspname !~ '^pg_toast'
#   ORDER BY pg_total_relation_size(C.oid) DESC
#   LIMIT 20;"""

TABLE_SIZES = '''SELECT
    table_schema || '.' || table_name AS table_full_name,
    pg_size_pretty(pg_total_relation_size('"' || table_schema || '"."' || table_name || '"')) AS size
FROM information_schema.tables
ORDER BY
    pg_total_relation_size('"' || table_schema || '"."' || table_name || '"') DESC;'''


DATBASE_SIZES = "SELECT d.datname as Name,  pg_catalog.pg_get_userbyid(d.datdba) as Owner,\
                CASE WHEN pg_catalog.has_database_privilege(d.datname, 'CONNECT')\
                    THEN pg_catalog.pg_size_pretty(pg_catalog.pg_database_size(d.datname))\
                    ELSE 'No Access'\
                END as Size\
            FROM pg_catalog.pg_database d\
                order by\
                CASE WHEN pg_catalog.has_database_privilege(d.datname, 'CONNECT')\
                    THEN pg_catalog.pg_database_size(d.datname)\
                    ELSE NULL\
                END desc -- nulls first\
                LIMIT 20;"

PG_STAT = "SELECT * FROM pg_stat_activity"

PID = "SELECT pg_backend_pid()"


# LOCK_QUERY = '''select pid, 
#        usename, 
#        pg_blocking_pids(pid) as blocked_by, 
#        query as blocked_query
# from pg_stat_activity
# where cardinality(pg_blocking_pids(pid)) > 0;'''


STATS = '''select datid, datname, pid, usesysid, usename, application_name, client_addr, client_port, backend_start, xact_start, query_start, state_change, wait_event_type, wait_event, state, backend_type from pg_stat_activity'''

def connect(host , user , password , port):
    try:
        con = psycopg2.connect(host=host, user=user, password=password , port=port)
        cursor = con.cursor()

        return con , cursor

        # cursor.execute("select * from pg_stat_activity")
        
        # for row in cursor.fetchall():
        #     print(row)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return None , None
    # finally:
    #     if con is not None:
    #         con.close()
    #         print('Database connection closed.')

@csrf_exempt
def getData(request):

    host = request.POST.get("host" , "127.0.0.1")
    username = request.POST.get("username" , "postgres")
    password = request.POST.get("password" , "akus@123")
    database = request.POST.get("database" , "postgres")
    port = request.POST.get("port" , 5432)

    if host == "172.16.0.11":
        host = "127.0.01"

    # print(host , username , password , port)

    con , cur = connect(host , username , password , port)

    if con == None or cur == None:
        return JsonResponse({"error" : True})

    output = {
        "pid" : 0,
        "tableCount" : 0,
        "databaseCount" : 0,
        "active_connections" : 0,
        "session_killed" : 0,
        "session_abandoned" : 0,
        "storage" : 0,
        "tables" : {},
        "databases" : {},
        "error" : False,
    }

    # cur.execute(ALL_TABLES)
    # output["tableCount"] = cur.fetchone()[0]

    # cur.execute(ALL_DATABASES)
    



    cur.execute(PID)
    output["pid"] = cur.fetchone()[0]

    
    cur.execute(TABLE_SIZES)
    tableSizes = cur.fetchall()
    count1 = 0
    for table in tableSizes:
        output["tables"][table[0]] = {
            "name" : table[0] , 
            "size" : table[1] ,
        }
        count1 += 1
    output["tableCount"] = count1
    



    cur.execute(DATBASE_SIZES)
    databaseSizes = cur.fetchall()

    count = 0
    for database in databaseSizes:
        try:
            arr = database[2].split(" ")
            if arr[1] == "kB":
                output["storage"] += round((float(arr[0]) / 1000) , 2)
            if arr[1].lower() == "gb":
                output["storage"] += round((float(arr[0]) * 1000) , 2)
            else:
                output["storage"] += round(float(arr[0]) , 2)
            count += 1
        except Exception as ex:
            print("Meh Error" , str(ex))
                
        output["databases"][database[0]] = {"name" : database[0] , "size" : database[2]}

    output["databaseCount"] = count


        

    cur.execute(DATABASE_DETAILS)
    databaseDetails = cur.fetchall()


    for database in databaseDetails:
        if database[1] == "" or database[1] == None:
            continue
        
        # print("running for" , database) 

        # output["active_connections"] += database[2]
        # output["session_killed"] += database[25]
        # output["session_abandoned"] += database[24]

        output["databases"][database[1]] = { 
            "name" : database[1],
            "active_connections" : database[2],
            "size" : output["databases"][database[1]]["size"],
            "block_read" : database[5],
            "block_hit" : database[6],
            "records" : {
                "returned" : database[7],
                "fetched" : database[8],
                "inserted" : database[9],
                "updated" : database[10],
                "deleted" : database[11],
            },
            "sessions" : {
                # "active" : database[23],
                # "abandoned" : database[24],
                # "killed" : database[25],
            }
        }

    cur.execute(STATS)
    stats = cur.fetchall()

    tempLock = []
    for i in stats:
        locks = {}
        locks["DataID"] = i[0]
        locks["Datname"] = i[1]
        locks["pid"] = i[2]
        locks["userid"] = i[3]
        locks["username"] = i[4]
        locks["Appname"] = i[5]
        locks["clientAddress"] = i[6]
        locks["ClientPort"] = i[7]
        if i[8]:
            locks["BackendStart"] = i[8].strftime("%y-%m-%d %H:%M")
        else:
            locks["BackendStart"] = i[8]
        if i[9]:
            locks["QueryStart"] = i[9].strftime("%y-%m-%d %H:%M")
        else:
            locks["QueryStart"] = i[9]
        if i[10]:
            locks["Startchange"] = i[10].strftime("%y-%m-%d %H:%M")
        else:
            locks["Startchange"] = i[10]
        if i[11]:
            locks["WaitEType"] = i[11].strftime("%y-%m-%d %H:%M")
        else:
            locks["WaitEType"] = i[11]
        locks["WaitEvent"] = i[12]
        locks["Satrt"] = i[13]
        locks["Backendtype"] = i[14]
        tempLock.append(locks)
        
    output["locks"] = tempLock

    cur.execute(QUERY)
    query = cur.fetchall()
    queryData = []
    for i in query:
        qry = {}
        qry["datname"] = i[0]
        qry["pid"] = i[1]
        qry["state"] = i[2]
        qry["query"] = i[3]
        queryData.append(qry)
    
    output["queries"] = queryData

    # print(output)

    con.close()

    return JsonResponse(output)


@permission_required("dashboard.view_databasesummary" , "/noperm/") 
def index(request):
    # assetDevices = AddDevice.objects.filter(type_of_device = "Server")

    # devices = []

    # for device in assetDevices:
    #     fullIP = str(device.IP_Address_col1) + "." + str(device.IP_Address_col2) + "." + str(device.IP_Address_col3) + "." + str(device.IP_Address_col4)
    #     devices.append( fullIP )

    # print(assetDevices)

    devices = DeviceCapibility.objects.filter(dbuser__isnull = False).exclude(dbuser__exact='')
    return render(request, "dashboard/db-test.html" , {"devices" : devices})