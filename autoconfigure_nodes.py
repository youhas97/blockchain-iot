from iroha import IrohaCrypto
import sys
import json
import os
from copy import deepcopy

config_docker = {
  "block_store_path" : "/tmp/block_store/",
  "torii_port" : 50051,
  "internal_port" : 10001,
  "max_proposal_size" : 10,
  "proposal_delay" : 5000,
  "vote_delay" : 100,
  "mst_enable" : False,
  "mst_expiration_time" : 1440,
  "max_rounds_delay": 3000,
  "stale_stream_max_rounds": 2,
  "database": {
    "host" : "",
    "port" : 5432,
    "user" : "postgres",
    "password" : "QPtc2AssTNv2ugnD",
    "working database" : "iroha_data",
    "maintenance database" : "postgres"
  }
}

genesis_block = {
  "block_v1":{
    "payload":{
      "transactions":[
        {
          "payload":{
            "reducedPayload":{
              "commands":[
                {
                  "createRole":{
                    "roleName":"admin",
                    "permissions":[
                      "can_create_account",
                      "can_set_detail",
                      "can_create_asset",
                      "can_receive",
                      "can_transfer",
                      "can_add_asset_qty",
                      "can_subtract_asset_qty",
                      "can_add_domain_asset_qty",
                      "can_subtract_domain_asset_qty",
                      "can_create_domain",
                      "can_add_peer",
                      "can_remove_peer",
                      "can_append_role",
                      "can_create_role",
                      "can_detach_role",
                      "can_add_signatory",
                      "can_remove_signatory",
                      "can_set_quorum",
                      "can_get_all_acc_detail",
                      "can_get_all_accounts",
                      "can_get_all_acc_ast",
                      "can_get_all_acc_ast_txs",
                      "can_get_all_acc_txs",
                      "can_read_assets",
                      "can_get_blocks",
                      "can_get_roles",
                      "can_get_all_signatories",
                      "can_get_all_txs",
                      "can_get_peers"
                    ]
                  }
                },
                {
                  "createRole":{
                    "roleName":"user",
                    "permissions":[
                      "can_add_signatory",
                      "can_get_my_acc_ast",
                      "can_get_my_acc_ast_txs",
                      "can_get_my_acc_detail",
                      "can_get_my_acc_txs",
                      "can_get_my_account",
                      "can_get_my_signatories",
                      "can_receive",
                      "can_remove_signatory",
                      "can_set_quorum",
                      "can_transfer"
                    ]
                  }
                },
                {
                  "createDomain":{
                    "domainId":"coniks",
                    "defaultRole":"user"
                  }
                },
                {
                  "createAsset":{
                    "assetName":"coin",
                    "domainId":"coniks",
                    "precision":2
                  }
                },
                {
                  "createAccount":{
                    "accountName":"admin",
                    "domainId":"coniks",
                    "publicKey":"65628c6eaddc37c042c5a97ec69c6d16857bd5aa0465125dbb315b84019d9d6a"
                  }
                },
                {
                  "appendRole":{
                    "accountId":"admin@coniks",
                    "roleName":"admin"
                  }
                },
                {
                  "createAccount":{
                    "accountName":"drone1",
                    "domainId":"coniks",
                    "publicKey":"94e15264063c5b2a3db480bc686cb8822a752be59e6f2f006bb057be91fdcd1f"
                  }
                },
                {
                  "createAccount":{
                    "accountName":"drone2",
                    "domainId":"coniks",
                    "publicKey":"56b522f1d91bd7284ee05cd41d25ad26ac574d9ab091649380371be47632bfb6"
                  }
                }
              ],
              "quorum":1
            }
          }
        }
      ],
      "txNumber":1,
      "height":"1",
      "prevBlockHash":"0000000000000000000000000000000000000000000000000000000000000000"
    }
  }
}

NODES_PER_DB=10

if __name__ == '__main__':
    if len(sys.argv) != 2 or not (sys.argv[1].isdigit() and int(sys.argv[1]) >= 0):
        sys.exit("ERROR: YOU NEED TO ENTER THE NUMBER OF KEYS TO GENERATE (POSITIVE INTEGER).")

    nodes = int(sys.argv[1])

    db_counter = 0
    for i in range(nodes):
      private_key = IrohaCrypto.private_key()
      public_key = IrohaCrypto.derive_public_key(private_key)

      if not os.path.isdir("nodes"):
        os.mkdir("nodes", 0o755)
      if not os.path.isdir("nodes/node_{}".format(i)):
        os.mkdir("nodes/node_{}".format(i), 0o755)

      with open('nodes/node_{}/node_{}.priv'.format(i, i), 'wb') as f:
        f.write(private_key)

      with open('nodes/node_{}/node_{}.pub'.format(i, i), 'wb') as f:
        f.write(public_key)

      genesis_block["block_v1"]["payload"]["transactions"][0]["payload"]["reducedPayload"]["commands"].append({
        "addPeer": {
          "peer": {
            "address": "10.1.2.{}:10001".format(i),
            "peerKey": public_key.decode("utf-8")
          }
        }
      })
      

      if i > 0 and i % NODES_PER_DB == 0:
        db_counter+=1
      config_docker["database"]["host"] = "nodedb_{}".format(db_counter)
      config_docker["database"]["working database"] = "node_data_{}".format(i % NODES_PER_DB)

      with open("nodes/node_{}/config.docker".format(i), 'w') as f:
        json.dump(config_docker, f, indent=2)

    for i in range(nodes):
      # node_genesis_block = deepcopy(genesis_block)
      # commands = node_genesis_block["block_v1"]["payload"]["transactions"][0]["payload"]["reducedPayload"]["commands"]
      # commands = list(filter(lambda command: "addPeer" in command, commands))
      # commands[i]["addPeer"]["peer"]["address"] = "127.0.0.1:10001"  

      with open("nodes/node_{}/genesis.block".format(i), 'w') as f:
        json.dump(genesis_block, f, indent=2)