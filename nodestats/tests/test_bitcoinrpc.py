from django.test import TestCase

import time

from lib.bitcoin_utils.rpc_bitcoinrpc import BatchedRPC
from lib.bitcoin_utils import block_utils


class TestBitcoinRpc(TestCase):
    def setUp(self):
        self.rpc = BatchedRPC()

    def test_bestblockhash(self):
        best_block_hash = self.rpc.getbestblockhash()
        print(best_block_hash)

    def test_getblock(self):
        best_block_hash = self.rpc.getbestblockhash()
        print(self.rpc.rpc_connection.getblock(best_block_hash))

    def test_batched_block_retreival(self):
        block_hashes = self.rpc.rpc_connection.batch_([[ "getblockhash", height] for height in range(0, 10)])
        blocks = self.rpc.rpc_connection.batch_([["getblock", h] for h in block_hashes])
        print(blocks[0]['hash'])
        print(blocks[0]['height'])
        print(blocks[0]['version'])
        print(blocks[0]['mediantime'])
        print(blocks[0]['difficulty'])
        print(blocks[0].get('previousblockhash'))
        print(blocks[0].get('nextblockhash'))
        print(blocks[0]['chainwork'])
        print(blocks[0]['size'])
        print(len(blocks[0]['tx']))

    def test_vin_vout(self):
        hash_ = '0000000000000000000c78693abeb1498dca02c23a8538e940add85de55af7ec'
        blocks = self.rpc.rpc_connection.batch_([['getblock', hash_, 2]])
        block = block_utils.BlockProperties(blocks[0])
        number_inputs_outputs = block.number_inputs_outputs()
        self.assertEqual(number_inputs_outputs, (396, 2570))
        print("Number of inputs / outputs: {} {}".format(*number_inputs_outputs))

    def test_number_transactions(self):
        hash_ = '0000000000000000000c78693abeb1498dca02c23a8538e940add85de55af7ec'
        blocks = self.rpc.rpc_connection.batch_([['getblock', hash_, 2]])
        block = block_utils.BlockProperties(blocks[0])
        transactions_estimate = block.estimate_transactions()
        self.assertEqual(transactions_estimate, (215, 2355))
        print("Number of transactions / est transactions: {} {}".format(*transactions_estimate))

if __name__ == '__main__':
    test = TestBitcoinRpc()
    test.setUp()
    test.test_vin_vout()
    test.test_number_transactions()