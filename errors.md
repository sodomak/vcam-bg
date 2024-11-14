- command for `magick` is `convert`

```bash
  $ ./build/create-appimage.sh
Using Python version: 3.10
Requirement already satisfied: opencv-python-headless in ./build/venv/lib/python3.10/site-packages (4.10.0.84)
Requirement already satisfied: mediapipe in ./build/venv/lib/python3.10/site-packages (0.10.18)
Requirement already satisfied: numpy in ./build/venv/lib/python3.10/site-packages (1.26.4)
Requirement already satisfied: pillow in ./build/venv/lib/python3.10/site-packages (11.0.0)
Requirement already satisfied: protobuf<5,>=4.25.3 in ./build/venv/lib/python3.10/site-packages (from mediapipe) (4.25.5)
Requirement already satisfied: opencv-contrib-python in ./build/venv/lib/python3.10/site-packages (from mediapipe) (4.10.0.84)
Requirement already satisfied: sounddevice>=0.4.4 in ./build/venv/lib/python3.10/site-packages (from mediapipe) (0.5.1)
Requirement already satisfied: matplotlib in ./build/venv/lib/python3.10/site-packages (from mediapipe) (3.9.2)
Requirement already satisfied: jax in ./build/venv/lib/python3.10/site-packages (from mediapipe) (0.4.35)
Requirement already satisfied: absl-py in ./build/venv/lib/python3.10/site-packages (from mediapipe) (2.1.0)
Requirement already satisfied: attrs>=19.1.0 in ./build/venv/lib/python3.10/site-packages (from mediapipe) (24.2.0)
Requirement already satisfied: jaxlib in ./build/venv/lib/python3.10/site-packages (from mediapipe) (0.4.35)
Requirement already satisfied: flatbuffers>=2.0 in ./build/venv/lib/python3.10/site-packages (from mediapipe) (24.3.25)
Requirement already satisfied: sentencepiece in ./build/venv/lib/python3.10/site-packages (from mediapipe) (0.2.0)
Requirement already satisfied: CFFI>=1.0 in ./build/venv/lib/python3.10/site-packages (from sounddevice>=0.4.4->mediapipe) (1.17.1)
Requirement already satisfied: scipy>=1.10 in ./build/venv/lib/python3.10/site-packages (from jax->mediapipe) (1.14.1)
Requirement already satisfied: opt-einsum in ./build/venv/lib/python3.10/site-packages (from jax->mediapipe) (3.4.0)
Requirement already satisfied: ml-dtypes>=0.4.0 in ./build/venv/lib/python3.10/site-packages (from jax->mediapipe) (0.5.0)
Requirement already satisfied: python-dateutil>=2.7 in ./build/venv/lib/python3.10/site-packages (from matplotlib->mediapipe) (2.9.0.post0)
Requirement already satisfied: kiwisolver>=1.3.1 in ./build/venv/lib/python3.10/site-packages (from matplotlib->mediapipe) (1.4.7)
Requirement already satisfied: fonttools>=4.22.0 in ./build/venv/lib/python3.10/site-packages (from matplotlib->mediapipe) (4.54.1)
Requirement already satisfied: pyparsing>=2.3.1 in ./build/venv/lib/python3.10/site-packages (from matplotlib->mediapipe) (3.2.0)
Requirement already satisfied: contourpy>=1.0.1 in ./build/venv/lib/python3.10/site-packages (from matplotlib->mediapipe) (1.3.1)
Requirement already satisfied: packaging>=20.0 in ./build/venv/lib/python3.10/site-packages (from matplotlib->mediapipe) (24.2)
Requirement already satisfied: cycler>=0.10 in ./build/venv/lib/python3.10/site-packages (from matplotlib->mediapipe) (0.12.1)
Requirement already satisfied: pycparser in ./build/venv/lib/python3.10/site-packages (from CFFI>=1.0->sounddevice>=0.4.4->mediapipe) (2.22)
Requirement already satisfied: six>=1.5 in ./build/venv/lib/python3.10/site-packages (from python-dateutil>=2.7->matplotlib->mediapipe) (1.16.0)
./build/create-appimage.sh: line 148: magick: command not found
```
- `numpy` missing

```bash
/vcam-bg-x86_64.AppImage
Starting application...
OpenCV bindings requires "numpy" package.
Install it via command:
    pip install numpy
Traceback (most recent call last):
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/numpy/core/__init__.py", line 24, in <module>
    from . import multiarray
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/numpy/core/multiarray.py", line 10, in <module>
    from . import overrides
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/numpy/core/overrides.py", line 8, in <module>
    from numpy.core._multiarray_umath import (
ModuleNotFoundError: No module named 'numpy.core._multiarray_umath'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/numpy/__init__.py", line 130, in <module>
    from numpy.__config__ import show as show_config
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/numpy/__config__.py", line 4, in <module>
    from numpy.core._multiarray_umath import (
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/numpy/core/__init__.py", line 50, in <module>
    raise ImportError(msg)
ImportError: 

IMPORTANT: PLEASE READ THIS FOR ADVICE ON HOW TO SOLVE THIS ISSUE!

Importing the numpy C-extensions failed. This error can happen for
many reasons, often due to issues with your setup or how NumPy was
installed.

We have compiled some common reasons and troubleshooting tips at:

    https://numpy.org/devdocs/user/troubleshooting-importerror.html

Please note and check the following:

  * The Python version is: Python3.10 from "/usr/bin/python3"
  * The NumPy version is: "1.26.4"

and make sure that they are the versions you expect.
Please carefully study the documentation linked above for further help.

Original error was: No module named 'numpy.core._multiarray_umath'


The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/src/main.py", line 29, in <module>
    main() 
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/src/main.py", line 18, in main
    from src.gui.main_window import MainWindow
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/src/gui/main_window.py", line 3, in <module>
    from .settings_frame import SettingsFrame
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/src/gui/settings_frame.py", line 6, in <module>
    import cv2
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/cv2/__init__.py", line 11, in <module>
    import numpy
  File "/tmp/.mount_vcam-bp0a3mO/usr/lib/python3.12/site-packages/numpy/__init__.py", line 135, in <module>
    raise ImportError(msg) from e
ImportError: Error importing numpy: you should not try to import numpy from
        its source directory; please exit the numpy source tree, and relaunch
        your python interpreter from there.
```
