from datetime import datetime
from influxdb import InfluxDBClient
from locust import events

import os
import json

class InfluxDBWriter(object):
    """
    InfluxDB writer for locust events
    """

    def __init__(self):
        self._client = InfluxDBClient(host='influxdb', database='influxdb', use_udp=True)
        self._user_count = 0
        self.file1 = "/tests/1_node_success.json"
        self.file2 = "/tests/1_node_failure.json"

        if os.path.isfile(self.file1):
            os.remove(self.file1)        
        if os.path.isfile(self.file2):
            os.remove(self.file2)

    def hatch_complete(self, user_count, **kw):
        self._user_count = user_count

    def request_success(self, request_type, name, response_time, response_length, tx_hash=None, sent=None, committed=None, **kw):
        now = datetime.now().isoformat()
        points = [{
            "measurement": "request_success_duration",
            "tags": {
                "request_type": request_type,
                "name": name
            },
            "time": now,
            "fields": {
                "value": response_time,
                "tx_hash": tx_hash,
                "sent": sent,
                "committed": committed
            }
        },
        {
            "measurement": "user_count",
            "time": now,
            "fields": {
                "value": self._user_count
            }
        }]
        self._client.write_points(points)
        points[0]["block_size"] = len(str(kw["block"].block_v1.payload).encode("utf-8"))
        points[0]["total_block_size"] = len(str(kw["block"]).encode("utf-8"))
        with open(self.file1, 'a') as f:
            f.write(json.dumps(points[0], indent=2) + '\n')

    def request_failure(self, request_type, name, response_time, exception, tx_hash=None, **kw):
        now = datetime.now().isoformat()
        points = [{
            "measurement": "request_failure_duration",
            "tags": {
                "request_type": request_type,
                "name": name
            },
            "time": now,
            "fields": {
                "value": response_time,
                "tx_hash": tx_hash
            }
        },
        {
            "measurement": "user_count",
            "time": now,
            "fields": {
                "value": self._user_count
            }
        }]
        self._client.write_points(points)
        with open(self.file2, 'a') as f:
            f.write(json.dumps(points[0], indent=2) + '\n')


writer = InfluxDBWriter()
events.request_success.add_listener(writer.request_success)
events.request_failure.add_listener(writer.request_failure)
events.spawning_complete.add_listener(writer.hatch_complete)
