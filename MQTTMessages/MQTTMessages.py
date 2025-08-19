import json
import os.path
import socket
import ssl

import paho.mqtt.client as mqtt


class MQTTMessages:
    """
    Creates an MQTT message handler that can send (publish) or receive (subscribe) to MQTT messages,
    and ensures they are destined for this device as well as being correctly formatted.

    :type mqtt_config: dict
    :param mqtt_config:
        A specially formatted dictionary that defines the MQTT broker, which topics are to be subscribed to
        and that topics can be published to.
        Each topic has a unique name identifier, which means the underlying topics can be changed in the configuration
        without changing your code.

        The format of the configuration dict is as follows.
        XXX indicates a value that should be supplied.

        mqtt_config = {"broker”: {"host”: “XXX”,
                                 "port": XXX,
                                 "keepalive": XXX,
                                 "transport": "XXX",
                                 "tlsversion": XXX,
                                 "certfile": "XXX",
                                 "selfcert": True/False},
              "thisclient": {"deviceid": "XXX",
                             "username": "XXX",
                             "password": "XXX",
                             "version": XXX,
                             "devicetypes": ["XXX",...]},
              "subscribeto": [{"name": "XXX", "definition": {"topic": "XXX", "qos": XXX}}],
              "publishto": [{"name": "XXX", "definition": {"topic": "XXX", "qos": XXX, "devicetypes": ["XXX", ...]}}]
              }

        The "broker" section defines the MQTT broker that is to be connected to, consisting of:
          . The 'host' name (or IP address).
          . The broker 'port' number (e.g. 1883).
          . The 'keepalive' time (e.g. 60) - the time the connection will be kept alive between messages.
          . The 'transport' being used (e.g. 'tfs', but could be 'websockets').
          . The 'tlsversion' [optional] (e.g. 2), assuming TLS is being used.
          . The absolute location of the 'certfile' [optional] if you are using certificates to secure the broker.

        The 'thisclient' section describes the local Client.
          . The 'deviceid' is a unique name used by this client only.
          . The 'username' and 'password' [optional] are used when the broker is using usernames/passwords
            to secure the topics.
          . The 'version' is the MQTT-Message version that both the Publisher and Subscriber are using.
            Both must match, but have no relation to the version of MQTT being used or the MQTT broker.
          . The 'devicetypes' [optional] is a list of types of devices the message is destined for.
          This
            allows for shared topics between device types where messages can be destined for a subset of
            devices.

        The 'subscribeto' section lists all the MQTT topics which the client will subscribe to.
          . The 'name' is a name for the queue.
          . The 'topic' is the MQTT topic being subscribed to.
          . 'qos' is the QOS of the topic (to be expanded)
        You may leave the 'subscribeto' array empty if you do not want to subscribe to any topics.

        The 'publishto' section lists the MQTT topics that your client can publish to.
          . The 'topic' is the MQTT topic to publish on.
          . 'qos' is the QOS of the topic (to be expanded)
          .
          'Devicetypes' [optional] is a list of device types that the published message is destined for.

    :type handler_class: object
    :param handler_class:
        A class that contains a method called 'messagehandler' which takes two parameters.
        The first is a string for the 'what' in the MQTT message, and a dict for the parameters in the message
    """
    __libversion = 2.0

    __hostname = socket.gethostname()

    __mqtt_message_format = {
        "mqttmessage": {
            "devicetypes": [],
            "version"    : __libversion,
            "payload"    : {
                "host"  : __hostname,
                "what"  : "whattodo",
                "params": {}
            }
        }
    }

    def __init__(self, mqtt_config, handler_class=None):
        try:
            if mqtt_config["thisclient"]["version"] > self.__libversion:
                raise ValueError(
                    f"The MQTT definition is not compatible with this library version. Please upgrade MQTT-Messages.\n"
                    f"Installed version: {self.__libversion}, Expected Version: {mqtt_config['thisclient']['version']}")

            # This device
            self.__deviceid = mqtt_config["thisclient"]["deviceid"]
            self.__version = mqtt_config["thisclient"]["version"]
            self.__user = mqtt_config["thisclient"]["username"]
            self.__password = mqtt_config["thisclient"]["password"]

            if "devicetypes" in mqtt_config["thisclient"]:
                self.__device_types = mqtt_config["thisclient"]["devicetypes"]
            else:
                self.__device_types = ""

            # The MQTT Broker
            self.__host = mqtt_config["broker"]["host"]
            self.__port = mqtt_config["broker"]["port"]
            self.__transport = mqtt_config["broker"]["transport"]
            self.__keepalive = mqtt_config["broker"]["keepalive"]

            self.__certificate_file = None
            self.__tls_version = None

            if self.__transport.lower() == "tcp":
                if "tlsversion" in mqtt_config["broker"]:
                    self.__tls_version = mqtt_config["broker"]["tlsversion"]

                if "certfile" in mqtt_config["broker"]:
                    if os.path.isfile(mqtt_config["broker"]["certfile"]):
                        self.__certificate_file = mqtt_config["broker"]["certfile"]
                    else:
                        raise AttributeError(f"The certificate file does not exist.\n"
                                             f"Expected Location: {mqtt_config['broker']['certfile']}")

                if "selfcert" in mqtt_config["broker"]:
                    self.__selfcert = mqtt_config["broker"]["selfcert"]

            # The queues that can be published to
            self.__publish_topics = mqtt_config["publishto"]

            # Queues to listen to
            self.__subscribe_topics = mqtt_config["subscribeto"]

            self.__handler_class = handler_class

            # For logging results
            self.__last_log = ""

            # __On_Connect responses
            self.__oc_userdata = None
            self.__oc_flags = None
            self.__oc_result_code = None

            # __on_log responses
            self.__ol_client = None
            self.__ol_object = None
            self.__ol_level = None

            # __on_publish
            self.__op_client = None
            self.__op_object = None
            self.__op_mid = None

            # __on_message
            self.__om_client = None
            self.__om_userdata = None

            # Start listening to the queue
            self.__client = self.__start_mqtt()
            # self.__client.loop_start()
            self.__client.loop_forever()

        except Exception as err:
            print(f"There is a problem with the provided configuration.\n{err}")
            exit(1)

    # ==================================================================================================================
    # Private Methods
    # ==================================================================================================================

    # ------------------------------------------------------------------------------------------------------------------
    # MQTT Handling callback Functions
    # ------------------------------------------------------------------------------------------------------------------
    def __start_mqtt(self):
        """
        Start the connection to the MQTT broker.

        This will fail with an error of the connection has been tried 10 times without success.
        """
        # Creates the MQTT object for this client
        try:
            client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                                 client_id=self.__deviceid,
                                 clean_session=True,
                                 transport=self.__transport,
                                 reconnect_on_failure=True)

            if self.__transport.lower() == "tcp":
                # Set the security
                if self.__tls_version is not None:
                    if self.__certificate_file is not None:
                        if self.__selfcert:
                            client.tls_set(self.__certificate_file, tls_version=self.__tls_version, cert_reqs=ssl.CERT_NONE)
                        else:
                            client.tls_set(self.__certificate_file, tls_version=self.__tls_version)
                    else:
                        client.tls_set(tls_version=self.__tls_version)

            if self.__user is not None:
                client.username_pw_set(username=self.__user, password=self.__password)

            # Methods to call on MQTT events
            client.on_connect = self.__on_connect

            if self.__handler_class is not None:
                client.on_message = self.__on_message

            client.on_publish = self.__on_publish
            client.on_subscribe = self.__on_subscribe
            # client.on_log = self.__on_log

            # Attempt to connect the broker
            try:
                client.connect(host=self.__host, port=self.__port, keepalive=self.__keepalive)
            except Exception as err:
                self.__log(f"Unable to connect to the MQTT Broker: {err}.")

        except Exception as err:
            self.__log(f"Unable to start MQTT-Messages.\nError: {err}")
            client = None

        return client

    def __on_connect(self, client, userdata, flags, reason_code, properties):
        """
        This is run once this client connects with the MQTT Broker
        Subscribing in __on_connect() means that if the client loses the connection and
        reconnect then subscriptions will be renewed.
        """
        if reason_code == 0:
            for queue in self.__subscribe_topics:
                client.subscribe(topic=queue["definition"]["topic"], qos=queue["definition"]["qos"])
        else:
            print(f"Connection Error (Client: {client}, User data: {userdata}, Flags: {flags}. rc: {reason_code})")
            exit(reason_code)

    def __on_subscribe(self, client, userdata, mid, reason_codes, properties):
        for sub_result in reason_codes:
            if sub_result == 1:
                pass
            # process QoS == 1

            # Any reason code >= 128 is a failure.
            if sub_result >= 128:
                print(f"Unable to subscribe to topic: {reason_codes}")

    def __on_message(self, client, userdata, msg):
        """
        When a message is received, ensure that it is the correct format and
        call the message handler in the controlling class.
        :type client: mqtt.client
        :type userdata: mqtt.userdata
        :type msg: mqtt.MQTTMessage
        """
        self.__om_client = client
        self.__om_userdata = userdata

        payload = self.__getpayload(msg.payload)

        if payload != {}:
            self.__log("Payload received")
            self.__handler_class.messagehandler(payload['what'], payload['params'])
        else:
            self.__log("Error in the Payload received")

    def __on_publish(self, client, obj, mid, reason_codes, properties):
        """ What to do when a message is published """
        self.__log(f"Payload sent (Client: {client}, Object: {obj}, Mid: {mid})")

    def __on_log(self, client, obj, level, string):
        """ When a log is required """
        self.__log(f"{string} (Client: {client}, Object: {obj}, Level: {level})")

    # ------------------------------------------------------------------------------------------------------------------
    # Message Checking and Generation
    # ------------------------------------------------------------------------------------------------------------------

    def __jsontodict(self, jsonmessage):
        """
        Converts a JSON string, received from MQTT, to a python dictionary
        """

        try:
            message = json.loads(jsonmessage)
        except Exception as err:
            self.__log(f"Unable to interpret the MQTT message: {jsonmessage}\n({err})")
            message = None

        return message

    @staticmethod
    def __ismqttmessage(message):
        """
        Returns true if 'mqttmessage' is in the message i.e. if it is likely to be using the predefined message
        format
        """
        return "mqttmessage" in message

    def __isrightdevicetype(self, message):
        """
        Is this message destined for this device?
        """
        response = False
        if "devicetypes" in message["mqttmessage"]:
            for devicetype in message["mqttmessage"]["devicetypes"]:
                if devicetype in self.__device_types:
                    response = True
                    break

        return response

    def __isrightversion(self, message):
        """
        Is the message the correct version for this program?
        """
        response = False
        if "version" in message["mqttmessage"]:
            if message["mqttmessage"]["version"] == self.__version:
                response = True
            else:
                self.__log("Incorrect message version received.")
        return response

    def __haspayload(self, message):
        """
        Does the message have a 'payload'?
        """
        response = False
        if "payload" in message["mqttmessage"]:
            payload = message["mqttmessage"]["payload"]
            if "what" in payload and "params" in payload:
                response = True
            else:
                self.__log("The payload is incorrectly formatted.")

        return response

    def __getpayload(self, mqttmessage):
        """
        Extracts the message from MQTT queue message
        """
        payload = None

        try:
            message_json = self.__jsontodict(mqttmessage)

            if self.__ismqttmessage(message_json):
                if self.__isrightdevicetype(message_json):
                    if self.__isrightversion(message_json):
                        if self.__haspayload(message_json):
                            payload = message_json["mqttmessage"]["payload"]
        except Exception as err:
            self.__log(f"Unable to read the received message. ({err})")
            payload = None

        return payload

    def __makemessage(self, queuename, what, paramdict):
        messagejson = ""
        if len(what) == 0:
            self.__log("The instruction is blank.")
        else:
            if paramdict is None:
                paramdict = {}
            if isinstance(paramdict, dict):
                message = self.__mqtt_message_format
                message["mqttmessage"]["payload"]["what"] = what
                message["mqttmessage"]["payload"]["params"] = paramdict
                message["mqttmessage"]["devicetypes"] = self.__publish_topics["name" == queuename]["definition"][
                    "devicetypes"]
                messagejson = self.__make_json_message(message)
            else:
                self.__log("The parameters supplied were not a dictionary or 'None'.")
        return messagejson

    def __make_json_message(self, messagedict):
        try:
            message = json.dumps(messagedict)
        except Exception as err:
            self.__log(f"Unable to convert a message dictionary into JSON.\n{err}")
            message = None
        return message

    def __log(self, message):
        print(message)
        self.__last_log = message

    # ==================================================================================================================
    # Public Methods
    # ==================================================================================================================
    def sendmessage(self, sendqueuename, what, paramdict):
        for queue in self.__publish_topics:
            if queue["name"] == sendqueuename:
                message = self.__makemessage(sendqueuename, what, paramdict)
                if len(message) > 0:
                    self.__client.publish(queue["definition"]["topic"], message, queue["definition"]["qos"],
                                          retain=False)
                else:
                    self.__log("The message could not be sent")

    def getlastlog(self):
        """
        Returns the last message logged. Useful for debugging.
        :return: string
        """
        return self.__last_log
