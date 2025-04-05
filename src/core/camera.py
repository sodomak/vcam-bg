from typing import List, Optional, Tuple
import subprocess
import re
import cv2
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class Camera:
    def __init__(self):
        self.input_device = None
        self.output_device = None
        self.cap = None
        self.processor = None
        self.running = False
        self.resolution = (1280, 720)
        self.fps = 20.0

    def get_available_cameras(self) -> List[str]:
        """Get list of available camera devices"""
        try:
            output = subprocess.check_output("v4l2-ctl --list-devices", shell=True).decode("utf-8")
            devices = re.findall(r"(.*):\n\t(/dev/video\d+)", output)
            
            input_devices = []
            for name, path in devices:
                name = name.strip()
                if "v4l2loopback" not in name.lower():
                    input_devices.append(f"{name} ({path})")
            
            # Add GStreamer as an option
            input_devices.append("GSTREAMER")
            return input_devices
                
        except Exception as e:
            print(f"Error detecting cameras: {e}")
            return ["GSTREAMER"]

    def get_available_outputs(self) -> List[str]:
        """Get list of available v4l2loopback devices"""
        try:
            output = subprocess.check_output("v4l2-ctl --list-devices", shell=True).decode("utf-8")
            devices = re.findall(r"(.*):\n\t(/dev/video\d+)", output)
            
            output_devices = []
            for name, path in devices:
                name = name.strip()
                if "v4l2loopback" in name.lower():
                    output_devices.append(f"{name} ({path})")
            return output_devices
                
        except Exception as e:
            print(f"Error detecting output devices: {e}")
            return []

    def set_input_device(self, device: str) -> bool:
        """Set input camera device"""
        if not isinstance(device, str):
            raise ValueError("Device must be a string")
        
        if device == "GSTREAMER":
            self.input_device = 0
        else:
            match = re.search(r"\((/dev/video\d+)\)", device)
            if match:
                device_path = match.group(1)
                # Validate device path exists
                if not os.path.exists(device_path):
                    raise ValueError(f"Camera device not found: {device_path}")
                self.input_device = device_path
            else:
                try:
                    device_num = int(device)
                    if device_num < 0:
                        raise ValueError("Camera device number must be non-negative")
                    self.input_device = device_num
                except ValueError:
                    raise ValueError(f"Invalid camera device format: {device}")
        return True

    def set_output_device(self, device: str) -> bool:
        """Set output device"""
        self.output_device = device
        return True

    def set_resolution(self, resolution: str):
        """Set camera resolution"""
        if not isinstance(resolution, str):
            raise ValueError("Resolution must be a string")
        
        try:
            width, height = map(int, resolution.split('x'))
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive")
            if width > 7680 or height > 4320:  # 8K resolution limit
                raise ValueError("Resolution too high")
            self.resolution = (width, height)
        except ValueError as e:
            raise ValueError(f"Invalid resolution format: {resolution}. Expected format: WIDTHxHEIGHT") from e

    def set_fps(self, fps: float):
        """Set camera FPS"""
        try:
            fps = float(fps)
            if fps <= 0:
                raise ValueError("FPS must be positive")
            if fps > 240:  # Reasonable upper limit
                raise ValueError("FPS too high")
            self.fps = fps
        except ValueError as e:
            raise ValueError(f"Invalid FPS value: {fps}") from e

    def start(self):
        """Start camera capture"""
        if not self.running:
            try:
                # Try to open the camera with different methods
                if isinstance(self.input_device, str):
                    if "video" in self.input_device:
                        logger.info(f"Opening camera device: {self.input_device}")
                        self.cap = cv2.VideoCapture(self.input_device)
                    else:
                        # Try v4l2 first
                        logger.info(f"Opening camera device with V4L2: {self.input_device}")
                        self.cap = cv2.VideoCapture(self.input_device, cv2.CAP_V4L2)
                else:
                    # Try default camera with v4l2
                    logger.info("Opening default camera with V4L2")
                    self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

                if not self.cap.isOpened():
                    logger.error(f"Failed to open camera: {self.input_device}")
                    raise RuntimeError(f"Failed to open camera: {self.input_device}")

                # Set camera properties
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)

                # Verify settings
                actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                actual_fps = self.cap.get(cv2.CAP_PROP_FPS)

                logger.info(f"Camera initialized with resolution: {actual_width}x{actual_height} @ {actual_fps}fps")
                
                self.running = True
                
            except Exception as e:
                logger.error(f"Camera error: {str(e)}")
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                raise RuntimeError(f"Failed to initialize camera: {str(e)}")

    def stop(self):
        """Stop camera capture"""
        self.running = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the camera"""
        if self.running and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None

    def get_current_resolution(self) -> Tuple[int, int]:
        """Get current camera resolution"""
        if self.cap is not None:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return (width, height)
        return self.resolution
