import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
import sys

import json

if sys.version_info[0] < 3:
  raise Exception('Python 3 or a more recent version is required.')

if len(sys.argv) != 2:
  sys.exit("Usage: python -i iroha_cmd.py username@domain")

IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '127.0.0.1')
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

@trace
def set_account_details(account_id, key, val):
  tx = iroha.transaction([
    iroha.command(
      "SetAccountDetail",
      account_id=account_id,
      key=key,
      value=val
    )
  ])

@trace 
def get_account(account_id):
  query = iroha.query("GetAccount", account_id=account_id)
  IrohaCrypto.sign_query(query, ACCOUNT_PRIVATE_KEY)

  response = net.send_query(query)
  return json.loads(response.account_response.account.json_data)

@trace
def get_blocks():
  gps = int(get_account("admin@coniks")["admin@coniks"]["gps"]) + 1

  query = iroha.blocks_query()
  IrohaCrypto.sign_query(query, ACCOUNT_PRIVATE_KEY)
  blocks = net.send_blocks_stream_query(query, timeout=120)
  set_account_details("admin@coniks", "gps", str(gps))

  print(next(blocks))

@trace
def get_block(height):
  query = iroha.query("GetBlock", height=height)
  IrohaCrypto.sign_query(query, ACCOUNT_PRIVATE_KEY)

  response = net.send_query(query)
  if len(str(response.error_response)) != 0:
    print("No block found.")
  else:
    print(len(str(response).encode("utf-8")))
  