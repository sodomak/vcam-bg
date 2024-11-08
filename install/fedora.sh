#!/bin/bash

# Install required packages
sudo dnf install -y \
    python3-pip \
    python3-opencv \
    v4l2loopback \
    v4l-utils \
    ffmpeg \
    python3-tkinter \
    mesa-libGL
