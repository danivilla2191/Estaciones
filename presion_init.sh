#!/bin/bash

sleep 1
echo bmp085 0x77 >/sys/class/i2c-adapter/i2c-1/new_device
