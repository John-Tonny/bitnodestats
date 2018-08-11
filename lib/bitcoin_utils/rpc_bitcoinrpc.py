from lib.timing import function_timer

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException


class BatchedRPC:
    def __init__(self):
        #TODO put credentials in to settings
        self.rpc_name = 'user'
        self.rpc_pass = 'pass'
        auth_string = "http://{}:{}@127.0.0.1:8332".format(self.rpc_name, self.rpc_pass)
        timeout = 120
        self.rpc_connection = AuthServiceProxy(auth_string, timeout=timeout)

    @function_timer
    def getbestblockhash(self):
        return self.rpc_connection.getbestblockhash()

    def getblocks_batched(self, start, end):
        block_hashes = self.rpc_connection.batch_([["getblockhash", height] for height in range(start, end)])
        blocks = self.rpc_connection.batch_([["getblock", h, 2] for h in block_hashes])
        return blocks

