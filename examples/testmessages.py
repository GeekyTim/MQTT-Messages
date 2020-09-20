# This is a sample Python script.

# Press Ctrl+F5 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import test_config as config
import mqtt_messages
import signal
from time import sleep


def main():
    # Use a breakpoint in the code line below to debug your script.
    mqtt = mqtt_messages.Messages(config, None)

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

