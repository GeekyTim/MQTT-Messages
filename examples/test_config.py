# MQTT-MQTTMessages Configuration Definition
# 2020-09-09

"""
Include this file in all programs you use with MQTT-MQTTMessages
"""
mqttconfig = {"broker": {"host": "MQTTPi",
                         "port": 8883,
                         "keepalive": 60,
                         "transport": "tcp",
                         "tlsversion": 2,
                         "certfile": "/home/geekytim/servername.crt",
                         "selfcert": True},
              "thisclient": {"devicetypes": ["MotePi", "another"],
                             "deviceid": "testclient",
                             "username": "testclient",
                             "password": "testclient",
                             "version": 1.4},
              "subscribeto": [],
              "publishto": [{"name": "LavaLamp",
                             "definition": {"topic": "MotePi/command", "qos": 2, "devicetypes": ["MotePi", "other"]}}]
              }
