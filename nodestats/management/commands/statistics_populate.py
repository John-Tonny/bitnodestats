import pytz
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from nodestats.models import Block, BlockStatistics
from nodestats.management.commands import statistics_update

logger = logging.getLogger('nodestats')


class Command(BaseCommand):
    help = 'Calculates averages over blockheaders.'

    def add_arguments(self, parser):
        parser.add_argument(
            'blocks',
            type=int,
            help='Up to which block should it be populated?',
        )

    def handle(self, *args, **options):
        logger.info("Attempting to update the statistics.")
        empty_blockheader_statistics()
        populate_statistics(options['blocks'])
        logger.info(self.style.SUCCESS("Statistics populated."))


def empty_blockheader_statistics():
    BlockStatistics.objects.all().delete()


def populate_statistics(blocks):
    statistics_update.update_statistics(0, blocks)
