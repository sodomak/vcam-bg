#!/bin/bash

# Update package list
sudo apt update

# Install required packages
sudo apt install -y \
    python3-pip \
    python3-opencv \
    v4l2loopback-dkms \
    v4l-utils \
    ffmpeg \
    python3-tk \
    libgl1-mesa-glx
