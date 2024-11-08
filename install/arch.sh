#!/bin/bash

# Install required packages
sudo pacman -S --needed \
    python-pip \
    python-opencv \
    v4l2loopback-dkms \
    v4l-utils \
    ffmpeg \
    tk
