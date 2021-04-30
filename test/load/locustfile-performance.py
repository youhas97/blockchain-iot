import os
import time
import binascii

from locust import Locust, TaskSet, events, task, User, constant_pacing

import grpc.experimental.gevent as grpc_gevent
grpc_gevent.init_gevent()

import grpc
from iroha import Iroha, IrohaGrpc
from iroha import IrohaCrypto as ic
import iroha
import common.writer

import random
import gevent


HOSTNAME = os.environ['HOSTNAME']
#ADMIN_PRIVATE_KEY = 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70'
ADMIN_PRIVATE_KEY = "4503398c756e1bf99051836f43a6bbc45d24c2ad95f3a3bdc401993dcdabda05"

TXS = dict() # hash -> sent time
COMMITTED = set()
SENT = set()
BLOCKS = set()

def ascii_hash(tx):
    return binascii.hexlify(ic.hash(tx)).decode('ascii')

class IrohaClient(IrohaGrpc):
    """
    Simple, sample Iroha gRPC client implementation that wraps IrohaGrpc and
    fires locust events on request_success and request_failure, so that all requests
    gets tracked in locust's statistics.
    """
    def send_tx_wait(self, transaction):
        """
        Send a transaction to Iroha if there are few transactions in the queue to be committed
        :param transaction: protobuf Transaction
        :return: None
        """
        while len(SENT) - len(COMMITTED) > 100:
            time.sleep(0.01)

        hex_hash = ascii_hash(transaction)
        start_time = time.time()

        try:
            self.send_tx(transaction)
            SENT.add(hex_hash)
            TXS[hex_hash] = start_time
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            events.request_failure.fire(request_type="grpc", name='send_tx_wait', response_time=total_time, response_length=0, exception=e, tx_hash=hex_hash)


def block_listener(host):
    iroha_api = iroha.Iroha("admin@coniks")
    net = IrohaGrpc(host)
    query = iroha_api.blocks_query()
    ic.sign_query(query, ADMIN_PRIVATE_KEY)
    print("Listeting blocks")
    for block in net.send_blocks_stream_query(query):
        BLOCKS.add(block.block_response.block.block_v1.payload.height)
        hashes = block.block_response.block.block_v1.payload.rejected_transactions_hashes
        txs =  block.block_response.block.block_v1.payload.transactions
        for tx in txs:
            hashes.append(ascii_hash(tx))

        for hash in hashes:
            if hash not in TXS.keys():
                continue
            start_time = TXS[hash]
            COMMITTED.add(hash)
            del TXS[hash]
            total_time = int((time.time() - start_time) * 1000)
            try:
                events.request_success.fire(request_type="grpc", name='send_tx_wait', response_time=total_time, response_length=0, tx_hash=hash, sent=start_time, committed=time.time())
            except Exception as e:
                print(e)

class IrohaLocust(User):
    """
    This is the abstract Locust class which should be subclassed. It provides an Iroha gRPC client
    that can be used to make gRPC requests that will be tracked in Locust's statistics.
    """
    abstract=True
    def __init__(self, *args, **kwargs):
        super(IrohaLocust, self).__init__(*args, **kwargs)
        self.client = IrohaClient(self.host)
        gevent.spawn(block_listener, self.host)
        self.gps_coord = (1.5, 1.5)
        self.requests = 0


class ApiUser(IrohaLocust):

    host = "13.51.159.169:50051"
    #min_wait = 1000
    #max_wait = 1000

    @task
    class task_set(TaskSet):
        wait_time = constant_pacing(1)

        @task
        def send_tx(self):
            print("Locust instance (%r) executing my_task" % (self.user))
            print("""
            \n
                Sent: {}
                Committed: {}
                Diff: {}
                Blocks: {}\n
                """.format(len(SENT), len(COMMITTED), len(SENT) - len(COMMITTED), len(BLOCKS)))
            #iroha = Iroha('admin@test')
            iroha = Iroha("admin@coniks")

            #desc = str(random.random())
            # tx = iroha.transaction([iroha.command(
            #     'TransferAsset', src_account_id='admin@test', dest_account_id='test@test', asset_id='coin#test',
            #     amount='0.01', description=desc
            # )])

            tx = iroha.transaction([iroha.command(
              'SetAccountDetail',
              account_id="admin@coniks",
              key="gps",
              value=str(self.user.gps_coord)
            )])

            ic.sign_transaction(tx, ADMIN_PRIVATE_KEY)
            self.client.send_tx_wait(tx)
            self.user.gps_coord = (self.user.gps_coord[0] + 1, self.user.gps_coord[1] + 1)
            if self.user.requests == 100:
                self.user.environment.reached_end = True
                self.user.environment.runner.quit()
            self.user.requests += 1