import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

if len(sys.argv) != 2:
    sys.exit("Usage: python iroha_cmd.py username@domain")

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '13.51.156.212')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')

ACCOUNT_ID = sys.argv[1]
ACCOUNT_PRIVATE_KEY = ''
ACCOUNT_PUBLIC_KEY = ''

with open("{}.priv".format(ACCOUNT_ID), 'r') as f:
    ACCOUNT_PRIVATE_KEY = f.read()

with open("{}.pub".format(ACCOUNT_ID), 'r') as f:
    ACCOUNT_PUBLIC_KEY = f.read()

iroha = Iroha(ACCOUNT_ID)
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))

def trace(func):
    """
    A decorator for tracing methods' begin/end execution points
    """

    def tracer(*args, **kwargs):
        name = func.__name__
        print('\tEntering "{}"'.format(name))
        result = func(*args, **kwargs)
        print('\tLeaving "{}"'.format(name))
        return result

    return tracer

@trace
def send_transaction_and_print_status(transaction):
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)
    for status in net.tx_status_stream(transaction):
        print(status)

@trace
def get_account_assets(account_id):
    """
    List all the assets of userone@domain
    """
    query = iroha.query('GetAccountAssets', account_id=account_id)
    IrohaCrypto.sign_query(query, ACCOUNT_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.account_assets_response.account_assets
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


@trace
def create_account(name, domain):
    with open("{}.pub".format(name + '@' + domain), 'r') as f:
        key = f.read()
    transaction = iroha.transaction([
        iroha.command(
            'CreateAccount',
            account_name = name,
            domain_id = domain,
            public_key = key
        )
    ])
    IrohaCrypto.sign_transaction(transaction, ACCOUNT_PRIVATE_KEY)
    net.send_tx(transaction)

    for status in net.tx_status_stream(transaction):
        print(status)