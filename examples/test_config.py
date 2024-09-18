# MQTT-MQTTMessages Configuration Definition
# 2020-09-09

"""
Include this file in all programs you use with MQTT-MQTTMessages
"""
mqttconfig = {"broker": {"host": "MQTTPi",
                         "port": 1883,
                         "keepalive": 60,
                         "transport": "tcp"},
              "thisclient": {"devicetypes": ["MotePi", "another"],
                             "deviceid": "testclient",
                             "username": "testclient",
                             "password": "testclient",
                             "version": 1.5},
              "subscribeto": [],
              "publishto": [{"name": "LavaLamp",
                             "definition": {"topic": "MotePi/command", "qos": 2, "devicetypes": ["MotePi", "other"]}}]
              }
