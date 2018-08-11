import time
import logging
from pathlib import Path
import pytz

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from lib.bitcoin_utils.rpc_bitcoinlib import SerialRPC
from lib.bitcoin_utils.rpc_bitcoinrpc import BatchedRPC
from lib.bitcoin_utils.block_utils import BlockProperties

BATCH_SIZE = 2

rpc_batched = BatchedRPC()
rpc = SerialRPC()

from nodestats.models import Block
logger = logging.getLogger('nodestats')


class Command(BaseCommand):
    help = 'Updates the block database with new block data.'

    def add_arguments(self, parser):
        parser.add_argument('--updated_blocks',
                            action='store',
                            dest='updated_blocks',
                            type=int,
                            default=-1,
                            help='How many next blocks should be updated?',)

    def handle(self, *args, **options):
        logger.info(">>> Updating block information.")

        height_blockchain = rpc.bitcoind_get_blockcount()
        logger.info("Blockheight blockchain {}".format(height_blockchain))

        remove_last_six_blocks()

        height_database = get_database_blockheight()
        update_blockheight_start = max(height_database, 0)

        update_blockheight_end = determine_last_updated_block(
            height_blockchain,
            height_database,
            options['updated_blocks']
        )

        update_blockheaders(update_blockheight_start, update_blockheight_end)

        print_database_blockheight()
        logger.info(self.style.SUCCESS("Blockheaders updated."))
        touch_wsgi()


def touch_wsgi():
    if settings.PRODUCTION:
        Path(settings.WSGI_PY_PATH).touch()


def print_database_blockheight():
    blockheight_database = get_database_blockheight()
    logger.info("Blockheight database {}".format(blockheight_database))


def get_database_blockheight():
    return Block.objects.count() - 1


def remove_last_six_blocks():
    print_database_blockheight()
    current_height = Block.objects.count() - 1
    Block.objects.filter(height__range=(current_height - 6, current_height)).delete()
    print_database_blockheight()


def determine_last_updated_block(last_updated_block, current_blockchain_height, number_of_updated_blocks):
    if (last_updated_block - current_blockchain_height > int(number_of_updated_blocks)) \
            and (not int(number_of_updated_blocks) == -1):
        last_updated_block = current_blockchain_height + number_of_updated_blocks

    return last_updated_block


def get_batch_intervals(start, stop, step):
    ranges = [(n, min(n + step, stop)) for n in range(start, stop, step)]
    return ranges


def update_blockheaders(update_blockheight_start, update_blockheight_end):
    """
    Updates the database with blockheaders from start to end in a batched mode using bitcoinrpc.
    """
    total_block_count = update_blockheight_end - update_blockheight_start
    logger.info("Updating database with blockheights {} to {}, in total {} blocks (batched).".format(
        update_blockheight_start, update_blockheight_end, total_block_count))

    batches = get_batch_intervals(update_blockheight_start, update_blockheight_end, BATCH_SIZE)
    logger.info('Batches: {}'.format(batches))

    # TODO: estimate time to go
    for ibatch, batch in enumerate(batches):
        report_progress(batch[0] - update_blockheight_start, total_block_count)
        blocks = rpc_batched.getblocks_batched(batch[0], batch[1])
        for block in blocks:
            make_blockheader_entry_new(block)


def report_progress(block_number, number_blocks):
    progress = (block_number * 100 / number_blocks)
    if block_number % 100 == 0:
        logger.info("Progress: {:3.3f}%. Block number {} / {}.".format(progress, block_number, number_blocks))


def make_blockheader_entry_new(block):
    # Account for genesis block
    if block['height'] == 0:
        block['previousblockhash'] = ''
    # Account for last block
    if not 'nextblockhash' in block:
        block['nextblockhash'] = ''
    block_stats = BlockProperties(block)
    bh = Block(
        hash=block['hash'],
        height=block['height'],
        version=block['version'],
        time=timezone.datetime.fromtimestamp(block['mediantime'], tz=pytz.utc),
        difficulty=block['difficulty'],
        previousblockhash=block['previousblockhash'],
        nextblockhash=block['nextblockhash'],
        chainwork=block['chainwork'],
        size=block['size'],
        transactions=len(block['tx']),
        transactions_estimated=block_stats.estimate_transactions()[1],
    )
    bh.save()
