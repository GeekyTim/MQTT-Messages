# MQTTMessages Configuration Definition
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
              "thisclient": {"devicetypes": ["MotePi"],
                             "deviceid": "MotePi",
                             "username": "MotePi",
                             "password": "MotePi",
                             "version": 1.4},
              "subscribeto": [{"name": "ExampleQueue", "definition": {"topic": "Area/what", "qos": 2}}],
              "publishto": [{"name": "AnotherExample",
                             "definition": {"topic": "Area/what", "qos": 2, "devicetypes": ["devicename"]}}]
              }
