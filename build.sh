#!/bin/bash

python setup.py bdist_wheel

printf "The wheel file is stored in the dist folder\n"
printf "To install it on other Pi's, copy MQTTMessages-*-py3-none-any.whl \n\
        to another Pi and install with: \n\
        python3 -m pip install MQTTMessages-*-py3-none-any.whl \n"