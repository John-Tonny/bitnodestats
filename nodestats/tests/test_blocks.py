import logging

from django.test import TestCase
from django.core.management import call_command

import nodestats.management.commands.blocks_populate as blocks_populate

from nodestats.models import Block

logger = logging.getLogger('django_test')


class CommandsTestCase(TestCase):
    """Test my custom management commands"""

    def test_populate_and_update(self):
        """
        Tests the population and update of blocks.
        """
        args = [5003]

        """Test population management command."""
        call_command('blocks_populate', *args)
        self.assertEqual(
            Block.objects.first().hash,
            '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
        )
        self.assertEqual(
            Block.objects.all()[9].hash,
            '000000008d9dc510f23c2657fc4f67bea30078cc05a90eb89e84cc475c080805'
        )

        """Test update management command."""
        args = ['--updated_blocks', 13]

        call_command('blocks_update', *args)

        self.assertEqual(
            Block.objects.all()[11].hash,
            '0000000097be56d606cdd9c54b04d4747e957d3608abe69198c661f2add73073'
        )
        self.assertEqual(
            Block.objects.all()[15].hash,
            '00000000b3322c8c3ef7d2cf6da009a776e6a99ee65ec5a32f3f345712238473'
        )

    def batched_update(self):
        """
        Tests the population and update of blocks.
        """
        nblocks = 1001
        blocks_populate.populate_blocks_batched(nblocks)
        self.assertEqual(
            Block.objects.count(),
            nblocks
        )
        self.assertEqual(
            Block.objects.first().hash,
            '000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f'
        )
        self.assertEqual(
            Block.objects.all()[9].hash,
            '000000008d9dc510f23c2657fc4f67bea30078cc05a90eb89e84cc475c080805'
        )
