#!/bin/bash

# Update package list
sudo apt update

# Install required packages
sudo apt install -y \
    python3-opencv \
    python3-mediapipe \
    python3-numpy \
    python3-pillow \
    v4l2loopback-dkms \
    v4l-utils \
    ffmpeg \
    python3-tk \
    libgl1-mesa-glx
