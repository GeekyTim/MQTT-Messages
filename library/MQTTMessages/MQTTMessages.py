import json
import os.path

import paho.mqtt.client as mqtt


class MQTTMessages:
    """
    Creates an MQTT message handler which can send (publish) or receive (subscribe) to MQTT messages,
    and ensures they are destined for this device as well as being correctly formatted.

    :type mqttconfig: dict
    :param mqttconfig:
        A specially formatted dictionary that defines the MQTT broker, which topics are to be subscribed to
        and which topics can be published to.  Each topic has a unique name identifier, which means the
        underlying topics can be changed in the configuration without changing your code.

        The format of the configuration dict is as follows. XXX indicates a value that should be supplied:

        mqttconfig = {"broker": {"host": "XXX",
                                 "port": XXX,
                                 "keepalive": XXX,
                                 "transport": "XXX",
                                 "tlsversion": XXX,
                                 "certfile": "XXX"},
              "thisclient": {"deviceid": "XXX",
                             "username": "XXX",
                             "password": "XXX",
                             "version": XXX,
                             "devicetypes": ["XXX",...]},
              "subscribeto": [{"name": "XXX", "definition": {"topic": "XXX", "qos": XXX}}],
              "publishto": [{"name": "XXX", "definition": {"topic": "XXX", "qos": XXX, "devicetypes": ["XXX", ...]}}]
              }

        The "broker" section defines the MQTT broker which is to be connected to, consisting of:
          . The 'host' name (or IP address)
          . The broker 'port' number (e.g. 8883)
          . The 'keepalive' time (e.g. 60) - the time the connection will be kept alive between messages
          . The 'transport' being used (e.g. 'tfs', but could be 'websockets')
          . The 'tlsversion' [optional] (e.g. 2), assuming TLS is being used
          . The absolute location of the 'certfile' [optional] if you are using certificates to secure the broker.

        The 'thisclient' section describes the local Client.
          . The 'deviceid' is a unique name used by this client only.
          . The 'username' and 'password' [optional] is used when the broker is using usernames/passwords
            to secure the topics.
          . The 'version' is the MQTT-Message version that both the Publisher and Subscriber are using.
            Both must match, but has no relation to the version of MQTT being used or the MQTT broker.
          . The 'devicetypes' [optional] is a list of type of device the message is destined for. This
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
          . 'devicetypes' [optional] is a list of device types that the published message are destined for.

    :type handlerclass: object
    :param handlerclass:
        A class that contains a method called 'messagehandler' which takes two parameters.
        The first is a string for the 'what' in the MQTT message, and a dict for the parameters in the message
    """
    __libversion = 1.1

    __mqttmessageformat = {"mqttmessage": {
        "devicetypes": (),
        "version": __libversion,
        "payload": {
            "what": "whattodo",
            "params": {}
        }
    }
    }

    def __init__(self, mqttconfig, handlerclass=None):
        try:
            if mqttconfig["thisclient"]["version"] != self.__libversion:
                raise ValueError("The MQTT definition is not compatible with this library version.")

            # This device
            self.__device = mqttconfig["thisclient"]["deviceid"]
            self.__version = mqttconfig["thisclient"]["version"]
            self.__user = mqttconfig["thisclient"]["username"]
            self.__password = mqttconfig["thisclient"]["password"]
            if "devicetypes" in mqttconfig["thisclient"]:
                self.__devicetypes = mqttconfig["thisclient"]["devicetypes"]
            else:
                self.__devicetypes = ""

            # The MQTT Broker
            self.__host = mqttconfig["broker"]["host"]
            self.__port = mqttconfig["broker"]["port"]
            self.__transport = mqttconfig["broker"]["transport"]
            self.__keepalive = mqttconfig["broker"]["keepalive"]

            self.__certfile = None
            if self.__transport.lower() == "tcp":
                self.__tlsversion = mqttconfig["broker"]["tlsversion"]

                if "certfile" in mqttconfig["broker"]:
                    if os.path.isfile(mqttconfig["broker"]["certfile"]):
                        self.__certfile = mqttconfig["broker"]["certfile"]
                    else:
                        raise AttributeError("The certificate file does not exist.")

            # The queues that can be published to
            self.__publishqueues = mqttconfig["publishto"]

            # Queues to listen to
            self.__listenqueues = mqttconfig["subscribeto"]

            self.__handlerclass = handlerclass

            # For logging results
            self.__lastlog = ""

            # Start listening to the queue
            self.__client = self.__startmqtt()
            self.__client.loop_start()
        except:
            raise ValueError("There is a problem with the provided configuration.")

    # ==================================================================================================================
    # Private Methods
    # ==================================================================================================================

    # ------------------------------------------------------------------------------------------------------------------
    # MQTT Handling callback Functions
    # ------------------------------------------------------------------------------------------------------------------
    def __startmqtt(self):
        """
        Start the connection to the MQTT broker.

        This will fail with an error of the connection has been tried 10 times without success.
        """
        # Creates the MQTT object for this client
        startclient = mqtt.Client(client_id=self.__device, clean_session=True, transport=self.__transport)

        if self.__transport.lower() == "tcp":
            # Set the security
            if self.__tlsversion is not None:
                if self.__certfile is not None:
                    startclient.tls_set(self.__certfile, tls_version=self.__tlsversion)
                else:
                    startclient.tls_set(tls_version=self.__tlsversion)

        if self.__user is not None:
            startclient.username_pw_set(username=self.__user, password=self.__password)

        # Methods to call on MQTT events
        startclient.on_connect = self.__on_connect
        if self.__handlerclass is not None:
            startclient.on_message = self.__on_message
        startclient.on_publish = self.__on_publish
        startclient.on_log = self.__on_log

        # Attempt to connect the broker
        while True:
            try:
                startclient.connect(host=self.__host, port=self.__port, keepalive=self.__keepalive)
                break
            except:
                self.__log("Unable to connect to the MQTT Broker.")

        return startclient

    def __on_connect(self, client, userdata, flags, rc):
        """
        This is run once this client connects with the MQTT Broker
        Subscribing in __on_connect() means that if the client loses the connection and
        reconnect then subscriptions will be renewed.
        """

        for queue in self.__listenqueues:
            client.subscribe(topic=queue["definition"]["topic"], qos=queue["definition"]["qos"])

    def __on_message(self, client, userdata, msg):
        """
        When a message is received, ensure that it is the correct format and
        call the message handler in the controlling class.
        :type client: object
        :type userdata: object
        :type msg: string
        """

        payload = self.__getpayloadcontents(msg)

        if payload != {}:
            self.__log("Payload received")
            self.__handlerclass.messagehandler(payload['what'], payload['params'])
        else:
            self.__log("Error in the Payload received")

    def __on_publish(self, client, obj, mid):
        """ What to do when a message is published """
        self.__log("Payload sent")

    def __on_log(self, client, obj, level, string):
        """ When a log is required """
        self.__log(string)

    # ------------------------------------------------------------------------------------------------------------------
    # Message Checking and Generation
    # ------------------------------------------------------------------------------------------------------------------

    def __jsontodict(self, jsonmessage):
        """
        Converts a JSON string, received from MQTT. to a python dictionary
        """
        message = ""
        try:
            message_json = jsonmessage.payload.decode("utf-8")
            message = json.loads(message_json)
        except:
            self.__log("Unable to interpret the MQTT message:" + jsonmessage)
            message = {}
        finally:
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
            for type in message["mqttmessage"]["devicetypes"]:
                if type in self.__devicetypes:
                    response = True
                    break

        return response

    def __isrightversion(self, message):
        """
        Is the message the correct version for this program
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
        Does the message have a 'payload'
        """
        response = False
        if "payload" in message["mqttmessage"]:
            payload = message["mqttmessage"]["payload"]
            if "what" in payload and "params" in payload:
                response = True
            else:
                self.__log("The payload is incorrectly formatted.")

        return response

    def __getpayloadcontents(self, mqttmessage):
        """
        Extracts the message from MQTT queue message
        """
        payload = {}

        try:
            message_json = self.__jsontodict(mqttmessage)

            if self.__ismqttmessage(message_json):
                if self.__isrightdevicetype(message_json):
                    if self.__isrightversion(message_json):
                        if self.__haspayload(message_json):
                            payload = message_json["mqttmessage"]["payload"]
        except:
            self.__log("Unable to read the received message.")

        return payload

    def __makemessage(self, queuename, what, paramdict):
        messagejson = ""
        if len(what) == 0:
            self.__log("The instruction is blank.")
        else:
            if paramdict is None:
                paramdict = {}
            if isinstance(paramdict, dict):
                message = self.__mqttmessageformat
                message["mqttmessage"]["payload"]["what"] = what
                message["mqttmessage"]["payload"]["params"] = paramdict
                message["mqttmessage"]["devicetypes"] = self.__publishqueues["name" == queuename]["definition"][
                    "devicetypes"]
                messagejson = self.__makeJsonMessage(message)
            else:
                self.__log("The parameters supplied were not a dictonary or 'None'.")
        return messagejson

    @staticmethod
    def __makeJsonMessage(messagedict):
        try:
            message = json.dumps(messagedict)
        except:
            message = ""
        return message

    def __log(self, message):
        print(message)
        self.__lastlog = message

    # ==================================================================================================================
    # Public Methods
    # ==================================================================================================================
    def sendmessage(self, sendqueuename, what, paramdict):
        for queue in self.__publishqueues:
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
        return self.__lastlog
