import logging

from django.core.management.base import BaseCommand

from nodestats.models import Block

from nodestats.management.commands import blocks_update

logger = logging.getLogger('nodestats')


class Command(BaseCommand):
    help = 'Populates the database with blockchain headers.'

    def add_arguments(self, parser):
        parser.add_argument(
            'blocks',
            type=int,
            help='Blockheight up to which should it be populated?',
        )

    def handle(self, *args, **options):
        logger.info("Attempting to populate Blockheaders database.")
        logger.info("Deleting all entries.")

        delete_entries_blockheaders()

        logger.info("Filling database with {} blockheaders.".format(options['blocks']))

        populate_blocks(options['blocks'])
        logger.info(self.style.SUCCESS("Blockheaders populated."))


def delete_entries_blockheaders():
    Block.objects.all().delete()

def populate_blocks(blocks):
    blocks_update.update_blockheaders(0, blocks)
