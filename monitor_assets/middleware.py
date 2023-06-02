from tracking_analyzer.models import Tracker
from django.contrib.sites.models import Site
def simple_middleware(get_response):
    def middleware(request):
        if request.path == "/aboutUs/" or request.path == "/contactUs/" or request.path == "/dataReview/" or request.path == "/tables/" or request.path == "/edit-profile/" or request.path == "/settings/admin/" or request.path == "/notifications/" or request.path == "/appliance/" or request.path == "/" or request.path == "/asset/forms/" or request.path.startswith("/asset/datacenter/hall/") or request.path.startswith("/topview/") or request.path == "/ems/" or request.path == "/network/summary/" or request.path == "/server/summary/" or request.path == "/storage/summary/" or request.path == "/dbms/summary/" or request.path == "/apmMonitoring/" or request.path == "/web/monitoring/" or request.path == "/cctv/" or request.path == "/reports/" or request.path == "/settings/groups/" or request.path == "/settings/bulkio/" or request.path == "/show/user/" or request.path == "/ssl/" or request.path == "/backupandrestore/" or request.path == "" or request.path == "/provisioning/" or request.path == "/nfs/" or request.path == "/pdf/" or request.path == "/terminal/" or request.path == "/settings/admin/services/":
            try:
                Tracker.objects.create_from_request(request, Site.objects.get(id=1))
            except Exception as err:
                print(str(err))
        response = get_response(request)
        return response

    return middleware
