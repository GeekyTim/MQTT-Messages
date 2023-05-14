#!/bin/bash

scriptpath=$(dirname "$0")

# sudo apt-get update
# sudo apt-get install python3-pip -y
# pip3 install paho.mqtt jsondict

cd "$scriptpath"/library || exit
sudo python3 setup.py install
cd "$scriptpath" || exit
