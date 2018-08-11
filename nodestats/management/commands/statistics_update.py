from collections import deque
import logging

from django.core.management.base import BaseCommand

from nodestats.models import Block, BlockStatistics
from lib.bitcoin_utils import consensus

logger = logging.getLogger("nodestats")

BLOCKS_PER_STATS_BIN = 72
MAX_STATISTICS_BLOCK_RANGE = 2016
DISCARD_LAST_AVERAGES = 10


class Command(BaseCommand):
    help = 'Populates block statistics.'

    def handle(self, *args, **options):
        logger.info(">>> Attempting to update the statistics.")

        discard_statistics(DISCARD_LAST_AVERAGES)
        height_stats = get_height_stats()
        height_database = get_database_blockheight()
        logger.info("Actual database blockheight {}".format(height_database))

        latest_block_for_filled_bins = BLOCKS_PER_STATS_BIN * (height_database // BLOCKS_PER_STATS_BIN)

        # check
        update_statistics(height_stats, latest_block_for_filled_bins)

        print_height_stats()
        logger.info(self.style.SUCCESS("Statistics updated."))


def print_height_stats(comment=''):
    logger.info("Stats height {}: {}.".format(get_height_stats(), comment))


def get_height_stats():
    """
    Returns blockheight of the database (number of total blocks - 1)
    :return:
    int blockheight
    """
    return (BlockStatistics.objects.count()) * BLOCKS_PER_STATS_BIN


def get_database_blockheight():
    return Block.objects.count() - 1


def discard_statistics(number_discarded_blocks):
    logger.info("Discarding {} bins ({} blocks).".format(
        number_discarded_blocks, number_discarded_blocks * BLOCKS_PER_STATS_BIN))
    height_stats = get_height_stats()
    print_height_stats("Before")

    begin_delete = height_stats - (number_discarded_blocks - 1) * BLOCKS_PER_STATS_BIN
    end_delete = height_stats

    logger.info("Discarding stats from block {} to block {}".format(begin_delete, end_delete))
    BlockStatistics.objects.filter(bin_start__range=(begin_delete, end_delete)).delete()
    print_height_stats("After")


def update_statistics(current_stats_height, best_height):
    """
    Update the statistics.
    :param current_stats_height
    :param best_height
    """
    current_stats_height = max(0, (current_stats_height // BLOCKS_PER_STATS_BIN) * BLOCKS_PER_STATS_BIN)
    best_height = (best_height // BLOCKS_PER_STATS_BIN) * BLOCKS_PER_STATS_BIN

    logger.info("Updating database with blocks {} to {}.".format(current_stats_height, best_height))
    # Get blocks over which will be averaged. Take a bit more because of previous averages.
    logger.debug("Getting blockheaders for new statistics.")
    blockheaders = get_blockheaders_for_stats(current_stats_height, best_height)

    time_bins = create_time_bins(blockheaders, current_stats_height)

    logger.debug("Calculate segwit.")
    segwit_2016 = calculate_block_average(blockheaders, current_stats_height, 2016, blockheader_to_segwit)
    segwit_144 = calculate_block_average(blockheaders, current_stats_height, 144, blockheader_to_segwit)

    logger.debug("Calculate bip91.")
    bip91_144 = calculate_block_average(blockheaders, current_stats_height, 144, blockheader_to_bip91)

    logger.debug("Calculate difficulty.")
    difficulty = calculate_block_average(blockheaders, current_stats_height, 100,
                                         lambda b: blockheader_to_attribute(b, 'difficulty'))

    logger.debug("Calculate blocksize.")
    size = calculate_block_average(blockheaders, current_stats_height, 200, lambda b: blockheader_to_attribute(b, 'size'))

    logger.debug("Calculate hashrate.")
    hashrate = calculate_hashrate_bins(blockheaders, current_stats_height, 144)

    # TODO: transactions_day
    # TODO: transactions_estimated_day

    data = {'segwit_2016': segwit_2016,
            'segwit_144': segwit_144,
            'bip91_144': bip91_144,
            'difficulty': difficulty,
            'size': size,
            'hashrate': hashrate}

    logger.debug("Writing to database.")
    write_blockheader_statistics(time_bins, data)


def get_blockheaders_for_stats(current_height, best_height):
    """
    Gives back blocks for statistics calculations. Takes into account, that averages could be done from previous blocks.
    :param current_height:
    :param best_height:
    """
    low_block = current_height - MAX_STATISTICS_BLOCK_RANGE
    high_block = best_height
    logger.info("Fetching blocks from height {} to {}".format(low_block, high_block))
    blocks = Block.objects.filter(pk__range=[current_height - MAX_STATISTICS_BLOCK_RANGE, best_height])
    logger.info("Retrieved {} blocks.".format(len(blocks)))

    return blocks


def create_time_bins(blockheaders, begin_block_number):
    logger.debug("Creating time bins.")
    time_bins = []
    for blockheader in blockheaders:
        if is_valid_point(blockheader.height, begin_block_number):
            time_bins.append({'height': blockheader.height, 'time': blockheader.time})
    return time_bins


def is_valid_point(height, begin_height):
    """
    Checks, if the blockheight of the actual block should trigger a new statistics bin entry.
    It needs to check, whether the blockheight divides by BLOCKS_PER_STATS_BIN and that the blockheight is higher
    than the height requested from the statistics calculation. Lower blocks can be there, because the averaging
    needs to take into account blocks from previous intervals.
    :param height:
    :param begin_height:
    """
    if height >= begin_height and height > 0:
        if height % BLOCKS_PER_STATS_BIN == 0:
            return True
    else:
        return False


def calculate_hashrate_bins(blockheaders, begin_height_for_hashrate, average_interval_in_blocks):
    """Algorithm to calculate hashrate:
    depends on difficulty and time
    original: https://bitcoin.stackexchange.com/questions/11139/how-is-the-network-hash-rate-calculated
    H = (blocks found / blocks expected) * diff * 2^32 / 600

    formula used here
    H = (expected timespan to find blocks / actual timespan to find blocks) * diff * 2^32 / 600
    """
    logger.info("Calculating hashrate from block {}".format(begin_height_for_hashrate))
    if average_interval_in_blocks % BLOCKS_PER_STATS_BIN:
        raise ValueError("Average interval is not divisible by number of blocks in a bin.")

    number_of_past_blocks = 3 * BLOCKS_PER_STATS_BIN

    # historic blocks need to be taken into account
    difficulties = calculate_block_average(blockheaders, begin_height_for_hashrate - number_of_past_blocks, 100, lambda b: blockheader_to_attribute(b, 'difficulty'))
    time_bins = create_time_bins(blockheaders, begin_height_for_hashrate - number_of_past_blocks)

    # reserve temporary
    number_of_averaging_containers = average_interval_in_blocks // BLOCKS_PER_STATS_BIN
    last_blocks = deque([0] * number_of_averaging_containers)

    hashrate_bins = []
    two_to_thirty_two = 4294967296

    for n_time_bin, time_bin in enumerate(time_bins):

        bin_time_past = time_bins[n_time_bin - 1]['time']
        bin_time_now = time_bin['time']

        dt = (bin_time_now - bin_time_past).total_seconds()
        hashrate = (BLOCKS_PER_STATS_BIN * 600 / dt) * difficulties[n_time_bin] * two_to_thirty_two / 600

        # average
        last_blocks.popleft()
        last_blocks.append(hashrate)

        # append if height is requested
        if is_valid_point(time_bin['height'], begin_height_for_hashrate):
            hashrate_bins.append(sum(last_blocks) / len(last_blocks))

    return hashrate_bins

def calculate_block_average(blockheaders, begin_blockheight, average_interval, value_assignment_function):
    """
    Calculates the average of a quantity over the blockheaders.

    :param blockheaders
    :param begin_blockheight
    :param average_interval
    :param value_assignment_function:
    To get the quantity which is averaged the value_assignment_function is called with a blockheader.
    :return:
    Array with averaged quantities
    """
    data_bins = []
    last_blocks = deque([0] * average_interval)

    for blockheader in blockheaders:
        last_blocks.popleft()
        last_blocks.append(value_assignment_function(blockheader))

        if is_valid_point(blockheader.height, begin_blockheight):
            data_bins.append(sum(last_blocks) / average_interval)
    return data_bins


def blockheader_to_segwit(blockheader):
    if consensus.check_is_segwit_block(blockheader):
        return 1
    else:
        return 0


def blockheader_to_bip91(blockheader):
    if consensus.check_is_bip91_block(blockheader):
        return 1
    else:
        return 0


def blockheader_to_attribute(blockheader, attribute):
    return getattr(blockheader, attribute)


def write_blockheader_statistics(time_bins, data):
    for t, sw2016, sw144, bip91_144, diff, size, hashrate in zip(
            time_bins,
            data['segwit_2016'],
            data['segwit_144'],
            data['bip91_144'],
            data['difficulty'],
            data['size'],
            data['hashrate']):
        BlockStatistics(
            time=t['time'],
            bin_start=t['height'],
            segwit_average_2016=sw2016,
            segwit_average_144=sw144,
            bip91_average_144=bip91_144,
            difficulty=diff,
            size=size,
            hashrate=hashrate
        ).save()
