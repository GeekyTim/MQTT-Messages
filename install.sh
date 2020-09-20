#!/bin/bash

if [ $(id -u) -ne 0 ]; then
  printf "Script must be run as root. Try 'sudo ./install.sh'\n"
  exit 1
fi

WORKING_DIR=$(pwd)

apt update
apt install -y python3-pip
# apt install  -y
pip3 install paho.mqtt jsondict

cd $WORKING_DIR/library
sudo python3 setup.py install
cd $WORKING_DIR
