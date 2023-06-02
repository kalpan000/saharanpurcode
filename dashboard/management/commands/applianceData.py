from django.core.management.base import BaseCommand, CommandError
from dashboard.tasks import collectData
class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        collectData()