from django.conf import settings

from lib.timing import function_timer
import bitcoin.rpc
import bitcoin.core


class SerialRPC:
    def __init__(self):
        self.proxy = self.bitcoind_connect_proxy()

    def bitcoind_connect_proxy(self):
        bitcoin.SelectParams('mainnet')
        return bitcoin.rpc.Proxy(btc_conf_file=settings.BITCOIN_CONF)

    def get_block(self, blockhash, verbosity=1):
        return self.proxy.call("getblock", blockhash, verbosity)

    def bitcoind_get_blockhash(self, nblock):
        return self.proxy.call("getblockhash", nblock)

    def bitcoind_get_blockcount(self):
        return self.proxy.getblockcount()

    def bitcoind_get_blockheader(self, blockhash):
        return self.proxy.call("getblockheader", blockhash)

    @function_timer
    def getbestblockhash(self):
        return self.proxy.call("getbestblockhash")


