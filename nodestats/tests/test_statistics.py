import logging

from django.test import TestCase
# from django.core.management import call_command

from nodestats.models import BlockStatistics

from nodestats.management.commands.statistics_populate import populate_statistics
from nodestats.management.commands.statistics_update import update_statistics, create_time_bins,\
    get_blockheaders_for_stats, is_valid_point, BLOCKS_PER_STATS_BIN, calculate_block_average,\
    blockheader_to_attribute, discard_statistics, get_height_stats

logger = logging.getLogger('django_test')


class StatisticsTest(TestCase):
    """
    Testing environment for blockheader statistics generation.

    Fixture generation:
    args = ["nodestats.Block", "--indent", 4, "--output", "nodestats/tests/fixtures/blocks_statistics_test.json"]
    call_command("dumpdata", *args)
    """
    fixtures = ['blocks_statistics_test.json']

    def test_statistics_population(self):
        """Test for population of statistics database."""
        logger.info("TEST for population of statistics.")
        populate_statistics(500)
        for s in BlockStatistics.objects.all():
            logger.info(s.bin_start)
        logger.info("Number of block statistics generated: {}".format(BlockStatistics.objects.count()))

    def test_time_bins(self):
        """Test for time bins, which gives back height for last block and its median time"""
        logger.info("TEST Time bins.")
        current_height = 0
        best_height = 500
        blockheaders = get_blockheaders_for_stats(current_height, best_height)
        time_bins = create_time_bins(blockheaders, current_height)
        self.assertEqual(6, len(time_bins))
        self.assertEqual(72, time_bins[0]['height'])
        self.assertEqual(432, time_bins[-1]['height'])
        logger.info("Time bins:")
        for t in time_bins:
            logger.info(t)

    def test_is_valid_point(self):
        """Test for binning the datasets"""
        logger.info("TEST Valid point.")
        self.assertFalse(is_valid_point(0, 0))
        self.assertTrue(is_valid_point(BLOCKS_PER_STATS_BIN, 0))

    def test_blocksize(self):
        """Test for blocksize statistics"""
        logger.info("TEST Blocksize statistics.")
        current_height = 0
        best_height = 500
        average_interval = 200
        blockheaders = get_blockheaders_for_stats(current_height, best_height)
        size = calculate_block_average(
            blockheaders, current_height, average_interval,
            lambda b: blockheader_to_attribute(b, 'size'))
        self.assertEqual(78.895, size[0])
        self.assertEqual(217.135, size[-1])

    def test_difficulty(self):
        """Test for difficulty statistics"""
        logger.info("TEST Difficulty statistics.")
        current_height = 0
        best_height = 500
        average_interval = 100
        blockheaders = get_blockheaders_for_stats(current_height, best_height)
        difficulty = calculate_block_average(
            blockheaders, current_height, average_interval,
            lambda b: blockheader_to_attribute(b, 'difficulty'))
        self.assertEqual(0.73, difficulty[0])
        self.assertEqual(1.0, difficulty[-1])

    def test_update_difficulty(self):
        """Test if updating of difficulty works"""
        logger.info("TEST Update difficulty.")

        populate_statistics(500)
        stats_before = BlockStatistics.objects.all()
        difficulties_before = []
        for s in stats_before:
            difficulties_before.append(s.difficulty)

        update_statistics(500, 720)
        stats_after = BlockStatistics.objects.all()
        difficulties_after = []

        for s in stats_after:
            difficulties_after.append(s.difficulty)

        for s1, s2 in zip(difficulties_before, difficulties_after):
            self.assertEqual(s1, s2)

    def test_get_height_stats(self):
        populate_statistics(500)
        self.assertEqual(get_height_stats(), (500 // BLOCKS_PER_STATS_BIN ) * BLOCKS_PER_STATS_BIN)

    def test_discard_height_stats(self):
        bins = (500 // BLOCKS_PER_STATS_BIN )
        populate_statistics(500)
        self.assertEqual(get_height_stats(), bins * BLOCKS_PER_STATS_BIN)
        discard_statistics(1)
        self.assertEqual(get_height_stats(), (bins - 1) * BLOCKS_PER_STATS_BIN)

    def test_update_hashrate(self):
        """Test if updating of hashrate works"""
        logger.info("TEST Update hashrate.")

        populate_statistics(720)
        stats_before = BlockStatistics.objects.all()
        stats_before = save_stats(stats_before)

        update_statistics(360, 720)
        stats_after = BlockStatistics.objects.all()
        stats_after = save_stats(stats_after)

        for ss1, ss2 in zip(stats_before, stats_after):
            self.assertEqual(ss1, ss2)


def save_stats(stats):
    copied_stats = []
    for s in stats:
        copied_stats.append({'bin_start': s.bin_start, 'hashrate': s.hashrate, 'difficulty': s.difficulty})
    return copied_stats

