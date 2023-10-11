#!/bin/bash

scriptpath=$(dirname "$0")

cd "$scriptpath"/library || exit
sudo python3 setup.py install
cd "$scriptpath" || exit
