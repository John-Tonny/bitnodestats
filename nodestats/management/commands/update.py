import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand

logger = logging.getLogger('nodestats')

class Command(BaseCommand):
    help = 'Carries out the update procedure.'

    def handle(self, *args, **options):
        call_command('blocks_update')
        call_command('statistics_update')
