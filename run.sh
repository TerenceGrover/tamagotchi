#!/bin/bash
cd "$(dirname "$0")"
export GPIOZERO_PIN_FACTORY=rpigpio
export RPI_GPIO_USE_GPIOMEM=1
# source venv/bin/activate
sudo /usr/bin/python3.11 script.py
