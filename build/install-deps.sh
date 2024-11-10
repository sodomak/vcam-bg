#!/bin/bash

# Install required system packages for building
sudo pacman -S --needed \
    python \
    python-opencv \
    python-mediapipe \
    python-numpy \
    python-pillow \
    imagemagick \
    wget \
    fuse2