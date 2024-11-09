#!/bin/bash

# Install required packages
sudo dnf install -y \
    python3-opencv \
    python3-mediapipe \
    python3-numpy \
    python3-pillow \
    v4l2loopback \
    v4l-utils \
    ffmpeg \
    python3-tkinter \
    mesa-libGL
