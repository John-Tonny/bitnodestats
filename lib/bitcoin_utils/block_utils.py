
class BlockProperties:
    """Implements a class to calculate statistics on a block."""
    def __init__(self, block):
        self.block = block

    def number_inputs_outputs(self):
        ins = 0
        outs = 0
        for it, t in enumerate(self.block['tx']):
            ins += len(t['vin'])
            outs += len(t['vout'])
        return ins, outs

    def estimate_transactions(self):
        """
        Estimates number of transactions by summing over outputs minus change outputs.
        """
        number_transactions = 0
        number_estimated_transactions = 0

        for it, t in enumerate(self.block['tx']):
            number_transactions += 1
            number_outputs = len(t['vout'])
            assert number_outputs >= 0
            number_estimated_transactions += number_outputs - 1
        return number_transactions, number_estimated_transactions

    def get_coinbase(self):
        tx = self.block['tx'][0]
        coinbase = tx['vin'][0]
        print(coinbase)
