# MQTTMessages Configuration Definition
# 2020-09-09

"""
Include this file in all programs you use with MQTT-MQTTMessages
"""
mqttconfig = {"broker": {"host": "WDDrivePi.localdomain",
                         "port": 8883,
                         "keepalive": 60,
                         "transport": "tcp",
                         "tlsversion": 2,
                         "certfile": "/home/pi/mqtt-ca.crt"},
              "thisclient": {"devicetypes": ("MotePi"),
                             "deviceid": "MotePi",
                             "username": "MotePi",
                             "password": "MotePi",
                             "version": 1.1},
              "subscribeto": [{"name": "ExampleQueue",
                               "definition": {"topic": "Area/what", "qos": 2}}],
              "publishto": [{"name": "AnotherExample",
                             "definition": {"topic": "Area/what", "qos": 2, "devicetypes": ("devicename")}}]
              }
