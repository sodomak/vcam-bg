#!/bin/bash

# Install required packages
sudo pacman -S --needed \
    python-opencv \
    python-mediapipe \
    python-numpy \
    python-pillow \
    v4l2loopback-dkms \
    v4l-utils \
    ffmpeg \
    tk
