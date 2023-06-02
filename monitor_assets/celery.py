from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitor_assets.settings')
app = Celery('monitor_assets')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

app.conf.beat_schedule = {
    # Execute the Speed Test every 10 minutes
    'Dashboard_Data': {
        'task': 'collectDashboardData',
        'schedule': 15.0,
        'options': {'expires': 2,},
    },
    'SNMP_Data': {
        'task': 'collectSNMPData',
        'schedule': 15.0,
        'options': {'expires': 2,},
    },
    'Website_Data': {
        'task': 'collectWebsiteData',
        'schedule': 20.0,
        'options': {'expires': 2,},
    },
    'Raise_Ticket': {
        'task': 'raiseTicketToAdmin',
        'schedule': 15.0,
        'options': {'expires': 2,},
    },
}