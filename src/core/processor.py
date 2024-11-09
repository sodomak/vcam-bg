import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, Tuple
import queue

class Processor:
    def __init__(self):
        # MediaPipe components
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation
        self.selfie_segmentation = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
        
        # Processing settings
        self.fps = 20.0
        self.scale = 1.0
        self.smooth_kernel = 21
        self.smooth_sigma = 10.0
        self.resolution = (1280, 720)
        
        # Background
        self.background_image = None
        self.background_path = ""
        
        # Preview queue
        self.preview_queue = queue.Queue(maxsize=2)
        self.show_preview = True

    def initialize(self):
        """Initialize MediaPipe segmentation"""
        if self.selfie_segmentation is None:
            self.selfie_segmentation = self.mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

    def cleanup(self):
        """Clean up resources"""
        if self.selfie_segmentation:
            self.selfie_segmentation.close()
            self.selfie_segmentation = None
            self.mp_selfie_segmentation = None

    def set_background(self, path: str) -> bool:
        """Load and set background image"""
        try:
            if path:
                image = cv2.imread(path)
                if image is not None:
                    self.background_path = path
                    self.background_image = cv2.resize(
                        image,
                        (int(self.resolution[0] * self.scale),
                         int(self.resolution[1] * self.scale))
                    )
                    return True
            return False
        except Exception as e:
            print(f"Error loading background: {e}")
            return False

    def set_resolution(self, width: int, height: int):
        """Set processing resolution"""
        self.resolution = (width, height)
        if self.background_image is not None and self.background_path:
            self.set_background(self.background_path)

    def set_scale(self, scale: float):
        """Set output scale"""
        self.scale = scale
        if self.background_image is not None and self.background_path:
            self.set_background(self.background_path)

    def set_smoothing(self, kernel: int, sigma: float):
        """Set smoothing parameters"""
        self.smooth_kernel = kernel if kernel % 2 == 1 else kernel + 1
        self.smooth_sigma = sigma

    def process_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """Process a single frame"""
        if self.selfie_segmentation is None or self.background_image is None:
            return frame

        try:
            # Resize frame
            width = int(self.resolution[0] * self.scale)
            height = int(self.resolution[1] * self.scale)
            frame = cv2.resize(frame, (width, height))

            # Convert to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.selfie_segmentation.process(frame_rgb)

            if results.segmentation_mask is None:
                return frame

            # Create and smooth mask
            mask = results.segmentation_mask
            mask = cv2.GaussianBlur(
                mask,
                (self.smooth_kernel, self.smooth_kernel),
                sigmaX=self.smooth_sigma,
                sigmaY=self.smooth_sigma
            )

            # Stack mask for BGR image
            mask = np.stack((mask,) * 3, axis=-1)

            # Combine foreground and background
            output_frame = (frame * mask + 
                          self.background_image * (1 - mask)).astype(np.uint8)

            # Add to preview queue if enabled
            if self.show_preview:
                try:
                    self.preview_queue.put_nowait(output_frame.copy())
                except queue.Full:
                    pass

            return output_frame

        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame

    def get_preview_frame(self) -> Optional[np.ndarray]:
        """Get the latest preview frame"""
        try:
            return self.preview_queue.get_nowait()
        except queue.Empty:
            return None