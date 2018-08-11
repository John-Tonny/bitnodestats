import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bitnodestats.settings.local")
import django
django.setup()

from lib.bitcoin_utils.rpc_bitcoinlib import SerialRPC
import pprint

bitcoind_rpc = SerialRPC()

hash = bitcoind_rpc.getbestblockhash()
print(hash)
print(bitcoind_rpc.get_block(hash, 2))
#pp = pprint.PrettyPrinter(indent=4)
#
#l = (
#        {"jsonrpc": "2.0", "method": "getinfo", "params": [], "id": "1"},
#        {"jsonrpc": "2.0", "method": "getinfo", "params": [], "id": "2"}
#    )
#d = bitcoind_rpc.proxy._batch(l)

#pp.pprint(d)
