# This is a sample Python script.

# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from time import sleep

import MQTTMessages
import test_config as config


def main():
    # Use a breakpoint in the code line below to debug your script.
    mqtt = MQTTMessages.MQTTMessages(config, None)

    while True:
        mqtt.sendmessage("LavaLamp", "rainbow", None)
        sleep(10)
        mqtt.sendmessage("LavaLamp", "pastels", None)
        sleep(10)
        mqtt.sendmessage("LavaLamp", "police", None)
        sleep(10)
        mqtt.sendmessage("LavaLamp", "matrix", None)
        sleep(10)


if __name__ == '__main__':
    main()
