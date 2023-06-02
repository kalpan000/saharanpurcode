# Django imports
from os import name
from django.contrib.auth import login
from django.urls import path, include
from dashboard import views_ftp
from dashboard.views import aboutUs, GP,topology, IPScan, favTopology, topology1, topology2, topology3, wsl, topology5
# Custom imports
from . import views, views_cctv, views_apm , views_snmp , views_backup , views_databases , views_reports, views_license , viewsSNMP , views_webmonitoring, views_management, views_assets, views_lms, views_device_info , views_protocols , views_appliance , views_network, views_summary, views_sslcertificate, views_server, views_nms, admin_cmd, views_database, views_provisioning, snmpDashboard, views_tracker, views_ssh
from dashboard.views import DelDeviceCapability,ScheduleDeviceCapability, change_footer
from dashboard.views_management import EditDeviceCapability
from dashboard.views_auth import Registration, Login, ResetPassword, ProfileUpdate, TempUsers
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
# from view_home import akus_dashboard
from django.contrib import admin
# from dashboard.models import *
# from django_q.models import Failure, Success
# app_name = "dashboard"
from .views_audit import GeneratePdf
from .views_server_dashboard import Serverindex, Serverdata, server_summary
from .views_network_dashboard import Networkindex, Networkdata, network_summary, storage_summary
urlpatterns = [
    # Footer Seting
    path('change/footer/',change_footer, name="change_footer"),
    #SSL CERTIFICATE
    path('ssl/',views_sslcertificate.generate_ssl_certificate, name="generate_ssl_certificate"),
    #APM MONITORING
    path('apmMonitoring/getEverything/' , views_apm.mainFunction , name="APM_AJAX" ),
    path('apmMonitoring/getEverything/ssh/' , views_apm.sshLogin , name="SSH_AJAX" ),
    path('apmMonitoring/getEverything/ssh/app/' , views_apm.getSSHData , name="SSH_APP_AJAX" ),
    path('apmMonitoring/getEverything/cpu/' , views_apm.getCPUOnly , name="APM_AJAX_CPU" ),
    path('apmMonitoring/', views_apm.apm_monitoring, name='apm_monitoring'),
    # path('', views_home.akus_dashboard, name = 'home_page'),
    path('register/', Registration.as_view(), name = 'register_page'),
    path('login/', Login.as_view(), name = 'login_page'),
    path('demousers/', TempUsers.as_view(), name = 'tempusers'),
    path('reset-password/', ResetPassword.as_view(), name = 'reset_password_page'),
    path('edit-profile/', login_required(ProfileUpdate.as_view(), redirect_field_name=None), name = 'edit-profile'),
    #path('assets/world/', login_required(assetsWorld.as_view(), redirect_field_name=None), name='assets-world'),
    #path('assets/india/', login_required(Assets.as_view(), redirect_field_name=None), name='assets-india'),
    path('asset/datacenter/information/hall/<int:id>/', views.rack_page, name='rack_page'),
    path('asset/datacenter/information/hall/device/delete/<int:id>/', views.deleteDevice, name='deleteDevice'),
    path('asset/forms/device/delete/<int:id>/', views.deleteAssetDevice, name='deleteAssetDevice'),
    path('asset/forms/device/decocom/<int:id>/', views.decomAssetDevice, name='decomAssetDevice'),
    path('asset/datacenter/information/hall/delete/<int:id>/', views.delete_rack, name='delete_rack'),
    path('asset/forms/rack/edit/<int:id>/', views.edit_rack, name='edit_rack'),
    path('asset/datacenter/information/hall/patchpanel/', views.patch_panel, name='patch_panel'),

    path('asset/datacenter/information/hall/device/<int:id>/', views.device_page, name='device_page'),
    # path('asset/datacenter/information/hall/device/status/left/', views.change_device_status_left, name='change_device_status_left'),
    # path('asset/datacenter/information/hall/device/status/right/', views.change_device_status_right, name='change_device_status_right'),
    path('asset/datacenter/information/hall/device/pdu/type/', views.getpdutype, name='getpdutype'),
    path('asset/datacenter/information/hall/device/patch/port/', views.getpatchport, name='getpatchport'),
    path('asset/datacenter/information/hall/device/device/port/', views.getdeviceport, name='getdeviceport'),
    path('asset/forms/', login_required(views_assets.assetsForms.as_view(), redirect_field_name=None), name='assets-forms'),
    #CALBELS
    path('asset/forms/cables/', views.cablesGET, name='cables'),
    # path('asset/forms/post/', views.cablesPOST, name='cables_post'),
    path('asset/forms/connections/', views.cablesDevices, name='cables_post'),

    path('asset/forms/template/data/', views_management.getTemplateData, name='getTemplateData'),

    # path('device/capability/edit', login_required(EditDeviceCapabilityPage.as_view(), redirect_field_name=None), name = 'edit-device-capability-page'),
    path('device/capability/edit/', login_required(csrf_exempt(EditDeviceCapability.as_view()), redirect_field_name=None), name = 'edit-device-capability'),
    # path('device/capability/delete', login_required(DelDeviceCapabilityPage.as_view(), redirect_field_name=None), name = 'del-device-capability-page'),
    path('device/capability/delete/', login_required(csrf_exempt(DelDeviceCapability.as_view()), redirect_field_name=None), name = 'del-device-capability'),
    path('device/capability/schedule/<int:id>/', login_required(ScheduleDeviceCapability.as_view(), redirect_field_name=None), name = 'schedule-device-capability'),
    path('device/capability/retrieve/', views_device_info.retrieveDevice, name="retrieveDevice"),

    path('import/',views.importEx , name="import-export"),
    path('export/',views.exportData, name="exports"),
    path('groups/',login_required(GP.as_view(), redirect_field_name=None), name="group_data"),
    path('test/group/',views.getUserPermission,name="test_groups"),
    path('assign/group/',views.assignGroup,name="assign_groups"),
    # path('ap/',views.fun1,name="ap"),  
    path('topview/<int:id>/',views_assets.top,name="top-view"),  
    path('ems/',views.temp,name="temp-view"),
    path('settings',views.setting,name="setting-view"),
    path('settings/admin/',views.AdminSetting,name="admin-setting-view"),
    path('settings/groups/',views.AdminGroup,name="AdminGroup"),
    path('settings/bulkio/',views.AdminIO,name="AdminIO"),
    path('settings/admin/services/',views.AdminServices,name="admin-services"),
    #AJAX ADMIN
    path('service/restart/',admin_cmd.restartDevice,name="restartDevice"),
    
    path('logout',views.logoutView,name="logout-view"),
    path('changestatus/<int:id>',views.changeStatus,name="change_status"),    
    path('changeusertype/',views.changeUserType,name="changeUserType"),    
    path('show/user/',views.showUser,name="show_user"),
    path("reports2/", include("data_browser.urls")),
    path("reports/", views_reports.loadTemplate , name="reports2"),
    path("reports2DATA/", views_reports.loadData , name="reportsDATA2"),
    path("reports3DATA/", views_reports.loadFieldName , name="reports3DATA"),
    path('asset/datacenter/hall/<int:id>/',views_assets.datacenter_page, name='datacenter'), 
    path('asset/datacenter/hall/delete/<int:id>/',views_assets.deleteDC, name='deleteDC'), 
    #NOTIFICATION AJAX HANDLING
    path('notificationMarkRead/',views.notification_update, name='notification_update'),
    path('notificationRead/<int:id>/',views.notification_read, name='notification_read'),
    path('notifications/',views.all_notifications, name='all_notifications'),
    path('notifications/ajax/',views.fetch_notifications, name='fetch_notifications'),
    path('notifications/count/',views.get_notifications_count, name='get_notifications'),
    path('notificationDelet/<int:id>/',views.notification_delete, name='notification_delete'),
    path('notification/settings/',views.changeBlinkStatus, name='changeBlinkStatus'),

    #Send Deive Mail
    path('senddevicemail/',views.send_device_via_mail, name='send_device_via_mail'),
    #menubar functionality
    #path('genearteRawDataReport/',views.genearte_raw_data_report,name='genearte_raw_data_report'),
    # path('rackReport/',views.rack_report,name='rack_report'),
    path('web/monitoring/',views_webmonitoring.hexbin_graph, name='hexbin_graph'),
    path('web/monitoring/response',views_webmonitoring.WemMonitoring, name='WemMonitoring'),
    path('web/monitoring/delete/<int:id>/',views_webmonitoring.delete_web_monitor, name='delete_web_monitor'),
    path('web/data/', views_webmonitoring.AjaxWeb, name='AjaxWeb'),
    path('web/ajax/favorite/',views_webmonitoring.changeWebFav,name='changeWebFav'),
    path('web/response/',views_webmonitoring.responseTime,name='responseTime'),

    #CCTV
    path('cctv/delete/cctv/<int:id>/',views_cctv.delete_cctv, name='delete_cctv'),
    path('cctv/delete/camera/<int:id>/',views_cctv.delete_camera, name='delete_camera'),
    path('cctv/', views_cctv.cctv, name='cctv'),
    # path('topology/',login_required(topology.as_view(), redirect_field_name=None),name="topology-graph"),
    path('cctv/ajax/ipcamera/',views_cctv.ip_camera_ajax_page,name='cctv_camera_ajax'),
    path('cctv/ajax/cctvcamera/',views_cctv.cctv_ajax_page,name='camera_ajax'),
    path('cctv/ajax/favorite/',views_cctv.changeCCTVFav,name='changeCCTVFav'),
    path('mail/',views.mail,name='mail'),
    path('aboutUs/',views.aboutUs,name="about-us"),
    path('dataReview/',views.dataReview,name="data-review"),
    path('dataReview/ajax/',views.dataReviewAjax,name="dataReviewAjax"),
    path('threshold/',views.dataCheck,name="data-check"),
    path('device/settings/',views.devicesetting,name="devicesetting"),
    path('contactUs/',views.contactUs,name="contact-us"),
    path('raiseticket/',views.raiseTicket,name="raiseTicket"),
    path('assignticket/',views.AssignedTicket,name="assignTicket"),
    path('viewraiseticket/<int:id>/',views.viewRaiseTicket,name="viewRaiseTicket"),
    
    path('topology/',topology,name="topology-graph"),
    path('topology/fav/',favTopology,name="fav-topology-graph"),
    path("topology/1/" , topology1 , name="mytopo1"),
    path("topology/2/" , topology2 , name="mytopo2"),
    path("topology/3/" , topology3 , name="mytopo3"),
    path("topology/wlc/" , wsl , name="wsltopo"),
    path("topology/sankey/" , topology5 , name="sankeytopo"),

    path('device/capibility/', login_required(ScheduleDeviceCapability.as_view(), redirect_field_name=None), name="show-device-capability"),
    # path('ansible/', login_required.as_view(), redirect_field_name=None), name="),
    # path("data-browser/", include("data_browser.urls")),
    


    #add_data_center_cainet
    path('showrows',views_management.showRows, name='showrows'),
    path('showracks',views_management.showRacks, name='showracks'),
    path('showunitloc',views_management.showUnitLoc, name='showunitloc'),
    path('checkunitloc',views_management.checkUnitLoc, name='checkunitloc'),
    path('leftHeight',views_management.leftHeight, name='leftheight'),
    path('showdc',views_management.showdc, name='showdc'),
    #add_data_center_cainet

    path('tables/',views.table, name='table'),
    path('dashboard/host/<str:ip>/<str:str>',views.individualDashboard, name='individualDashboard'),

    # APM 
    path('apmMonitoring/getEverything/' , views_apm.mainFunction , name="APM_AJAX" ),
    path('apmMonitoring/getEverything/ssh/' , views_apm.sshLogin , name="SSH_AJAX" ),
    path('apmMonitoring/getEverything/ssh/app/' , views_apm.sshLogin , name="SSH_APP_AJAX" ),
    path('apmMonitoring/getEverything/cpu/' , views_apm.getCPUOnly , name="APM_AJAX_CPU" ),

    # Cable
    path('asset/forms/cables/', views.cablesGET, name='cables'),
    path('asset/forms/post/', views.cablesPOST, name='cables_post'), # used for updating cable quantity 
    path('asset/forms/connections/', views.cablesDevices, name='cables_post'), # returns cable quantity 

    # SUMMARY PAGES 
    # path('dbms/summary/', views_snmp.database, name='dbms'),
    path('server/summary/', views_snmp.server, name='server'),
    path('storage/summary/', views_snmp.storage, name='storage'),
    path('network/summary/', views_snmp.network, name='network'),

    path('network/summary/getDeviceData/' , views_snmp.getNetworkDeviceData , name="networkDeviceData"),
    path('network/summary/summary/' , views_snmp.getNetworkSummary , name="networkDeviceData"),



    path('',views.echart, name="home_page"),
    path('start',views.startPage, name="startPage"),
    path('start/save/',views.saveStarterSetting, name="saveStarterSetting"),
    #JSON RESPONSE FOR LIVE DATA
    path('charts/usedram/<int:firstRun>', views_appliance.fronendfunc, name='UsedRam'),
    path('charts/usedram/<str:duration>/<str:type>', views_appliance.fronendfunc, name='UsedRam'),
    path('charts/networkspeed/', views.networkspeed, name='networkspeed'),
    path('discover/ipscan/', login_required(IPScan.as_view(), redirect_field_name=None), name='IPScan'),
    path('asset/forms/host/', views.AddDeviceIP, name='AddDeviceIP'),
    path('logs/', views.LogsNotif, name='logs'),

    path('appliance/', views.applianceDashboard, name='appliance'),
    path('appliance/<int:firstRun>', views.applianceAjax, name='applianceajax'),
    path('device/capability/test/<int:id>/<value>/', views.myPath, name = 'myPath'),

    # Corrections / Paginations / AJAX
    path('device/ipdevices/', views_management.ipdevices, name='ipdevices'),
    path('device/cap/device/', views_management.cap_device, name='cap_device'),
    path('device/lms/', views_lms.lmsDevice, name='lmsDevice'),
    path('website/lms/', views_lms.websiteLMS, name='lmsWebsite'),
    path('device/decommision/', views_device_info.decommisionDevice, name='decommisionDevice'),
    path('device/lmsarchieve/', views_lms.lmsarchieveDevice, name='lmsarchieveDevice'),
    
    path('backupandrestore/',views_backup.loadTemplate,name='backupandrestore'),
    path('backupandrestore/backup/<str:name>',views_backup.backupDB,name='backupdb'),
    path('backupandrestore/backup/network/<str:file>',views_ftp.uploadDBFIles,name='backupdbtonetwork'),
    path('backupandrestore/restore/<str:name>',views_backup.restoreDB,name='restoredb'),
    path('backupandrestore/reset/',views_backup.factoryReset,name='resetdb'),

    
    path('datacenterall/', views_databases.loadTemplate ,name='datacenterAll'),
    path('datacenterallload/<str:datacenter>', views_databases.loadAll ,name='datacenterAllLoad'),


    #webmmonitoe fav true false
        # json("data":"done")
    #cctc

    #ipcamers

    #edit datacente
    path('asset/forms/edit/datacenter/<int:id>/', views_assets.editDC, name='editDC'),

    #ajax assets form --Management Tab--
    
    path('asset/forms/add/schedule/', views_management.addSchedule, name='addSchedule'),
    path('asset/forms/add/addcap/', views_management.addDCap, name='addDCap'),
    path('asset/forms/add/datacenter/', views_management.addDC, name='addataCenter'),
    path('asset/forms/add/row/', views_management.addRow, name='addRow'),
    path('asset/forms/add/rack/', views_management.addRack, name='addRack'),
    path('asset/forms/add/device/', views_management.deviceAdd, name='deviceAdd'), 
    path('asset/forms/add/devicetemplate/', views_management.deviceTemplateAdd, name='deviceTemplateAdd'), 

    # License Management
    path('license/', views_license.ActivationPage, name='ActivationPage'), 
    path('license/decrypt/', views_license.DecryptKey, name='DecryptKey'), 
    path('license/check/' , views_license.compareDate , name='statusCheck'),

    
    path('playstream/' , views_cctv.startStream , name='playStream'),
    path('recordstream/' , views_cctv.startRecording , name='recordStream'),
    path('stoprecording/' , views_cctv.stopRecording , name='stoprecording'),
    path('stopstream/<str:id>' , views_cctv.stopStream , name='stopStream'),
    path('resetTimer/' , views_cctv.startLastSignalCheck , name='resetTimer'),
    path('streamrecordings/' , views_cctv.allRecording , name='allRecording'),
    path('streamrecordings/ajax/' , views_cctv.allRecordingAJAX , name='allRecordingAJAX'),
    path('deleterecordings/' , views_cctv.deleteRecording , name='deleterecordings'),


    path('getsnmp/' , viewsSNMP.getDetails , name='getsnmp'),
    path('getnetconf/' , views_protocols.netconfajax , name='getnetconf'),
    path('getrestconf/' , views_protocols.restconfajax , name='getrestconf'),

    #network Dashboard
    path('networksummarychart/<int:firstRun>/<str:ip>', views_network.frontendFunc, name='ngetindividualdata'),
    path('networksummarychart/<str:duration>/<str:ip>/<str:type>', views_network.frontendFunc, name='nadsfsadf'),
    #NetworkSumaryAjax
    path('networksummary/', views_summary.NetworkSummary, name='networkSummary'),
    path('storagesummary/', views_summary.StorageSummary, name='storageSummary'),

    #server Dashboard
    path('serversummarychart/<int:firstRun>/<str:ip>', views_server.frontendFunc, name='sgetindividualdata'),
    path('serversummarychart/<str:duration>/<str:ip>/<str:type>', views_server.frontendFunc, name='sadsfsadf'),
    #ServerSumaryAjax
    path('serversummary/', views_summary.ServerSummary, name='ServerSummary'),
    path('serversummary/day', views_summary.ServerSummaryIn24Hours, name='ServerSummaryIn24Hours'),

    #makefavbtn for dashboard
    path('makedevicefav/', views_network.makedevicefav, name='makedevicefav'),

    #TERMINAL
    path('terminal/', views_nms.terminal, name='terminal'),
    path('terminal/data/', views_nms.getUserCmd, name='terminaldata'),
    path('terminal/data/ssh/', views_nms.sshCommand, name='sshCommand'),
    path('terminal/logs/', views_nms.terminalogs, name='terminalogs'),
    path('terminal/logs/data/', views_nms.terminalLogsdata, name='terminalLogsdata'),

    path('dbms/summary/', views_database.index, name='dbms'),
    path('database/testing/ajax', views_database.getData, name='db-test-aajx'),

    #Audit Report
    path('pdf/', GeneratePdf), 


    path('summary/server/', Serverindex, name='Serverindex'),
    path('summary/server/individual/', Serverdata, name='Serverdata'),
    path('summary/server/data/', server_summary, name='server_summary'),
    path('summary/network/individual/', Networkdata, name='Networkdata'),
    path('summary/network/data/', network_summary, name='network_summary'),
    path('summary/storage/data/', storage_summary, name='storage_summary'),


    path('nfs/', views.nfs, name='nfs'),
    path('nfs/upload/', views_ftp.uploadFile , name='nfsUpload'),

    path('syslogs/', views_nms.syslogs , name='syslogs'),
    path('fetchsyslog/', views_nms.fetchsyslog , name='fetchsyslog'),
    path('sendlog/', views_nms.send_log , name='send_log'),

    # PROVISIONING
    path('provisioning/', views_provisioning.index , name='provisioning'),
    path('stacking/', views_provisioning.staking , name='stacking'),
    path('replication/', views_provisioning.replication , name='replication'),


    path("noperm/" , views.noperm , name="noperm"),
    path("patches/" , views.patchesGet , name="patches"),
    path("patches/run/" , views.runPatch , name="runPatch"),


    path("snmp/dashboard/" , snmpDashboard.index , name="snmpDashboard"),
    path("snmp/dashboard/details/" , snmpDashboard.getDetail , name="snmpDashboardDetails"),
    path('stats', views_tracker.stats, name='stats'),
    path('cdn', views_tracker.cdn, name='cdn'),
    path('cdnfind', views_tracker.cdnfind, name='cdnfind'),
    path('crawl', views_tracker.crawl, name='crawl'),

    # SSH DATA
    path('ssh/host/<str:ip>/', views_ssh.individualDashboard, name='individualDashboard'),
    path('sshData', views_ssh.index, name='sshData')

]

# admin.site.unregister(Failure)
# admin.site.unregister(Success)
