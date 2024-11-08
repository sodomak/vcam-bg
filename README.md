# Virtual Camera Background

A GUI application that adds virtual background to your webcam feed using MediaPipe for segmentation. Works with any video conferencing software through v4l2loopback virtual camera.

## Features

- Real-time background replacement
- Multiple segmentation models (landscape/portrait)
- Adjustable smoothing and scaling
- Save/Load/Import/Export settings
- Preview window
- Support for multiple camera resolutions
- Works with any v4l2loopback virtual camera

## Prerequisites

### System Requirements
- Linux system with Python 3.8+
- Webcam compatible with V4L2
- Graphics acceleration recommended

### Dependencies Installation

Choose your distribution and run the appropriate install script:

    # Arch Linux
    ./install/arch.sh

    # Ubuntu/Debian
    ./install/debian.sh

    # Fedora
    ./install/fedora.sh

Or install dependencies manually:

1. System packages:
   - v4l2loopback-dkms
   - v4l-utils
   - ffmpeg
   - python3
   - python3-pip
   - opencv dependencies

2. Python packages:

    pip install -r requirements.txt

### Virtual Camera Setup

1. Load v4l2loopback module:

    sudo modprobe v4l2loopback devices=1 video_nr=2 card_label="Virtual Camera" exclusive_caps=1

2. Make it persistent (optional):

    echo "v4l2loopback" | sudo tee /etc/modules-load.d/v4l2loopback.conf
    echo "options v4l2loopback devices=1 video_nr=2 card_label='Virtual Camera' exclusive_caps=1" | sudo tee /etc/modprobe.d/v4l2loopback.conf

## Installation

1. Clone the repository:

    git clone https://github.com/yourusername/vcam-bg.git
    cd vcam-bg

2. Install dependencies:

    ./setup.sh

3. Run the application:

    ./src/vcam-bg-gui.py

## Usage

1. Select your input camera from the dropdown
2. Select virtual camera as output (/dev/video2 by default)
3. Choose a background image
4. Adjust settings as needed:
   - Model: Landscape/Portrait based on your usage
   - FPS: Higher values for smoother video
   - Scale: Adjust output resolution
   - Smoothing: Adjust edge detection sensitivity
5. Click Start to begin
6. Select "Virtual Camera" in your video conferencing software

## Configuration

Settings are automatically saved to `~/.config/vcam-bg/config.json`

You can export/import settings through the File menu.

## Troubleshooting

### Common Issues

1. Virtual camera not showing up:

    # Check if module is loaded
    lsmod | grep v4l2loopback

    # Check available video devices
    v4l2-ctl --list-devices

2. Permission denied:

    # Add user to video group
    sudo usermod -a -G video $USER

3. Poor performance:
- Lower the resolution
- Reduce FPS
- Adjust scale factor

### Debug Information

Run with debug output:

    PYTHONPATH=src DEBUG=1 ./src/vcam-bg-gui.py

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

## License

[MIT](https://choosealicense.com/licenses/mit/)
