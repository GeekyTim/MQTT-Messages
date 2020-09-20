# MQTT-Messages Configuration Definition
# 2020-09-09

"""
Include this file in all programs you use with MQTT-Messages
"""
mqttconfig = {"broker": {"host": "WDDrivePi.localdomain",
                         "port": 8883,
                         "keepalive": 60,
                         "transport": "tcp",
                         "tlsversion": 2,
                         "certfile": "/home/pi/mqtt-ca.crt"},
              "thisclient": {"devicetypes": ("MotePi", "another"),
                        "deviceid": "testclient",
                        "username": "testclient",
                        "password": "testclient",
                        "version": 1.1},
              "subscribeto": [],
              "publishto": [{"name": "LavaLamp",
                             "definition": {"topic": "MotePi/command", "qos": 2, "devicetypes": ("MotePi", "other")}}]
              }
