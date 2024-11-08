import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk
import threading
import queue
import re
import subprocess

class PreviewFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Camera Preview")
        self.parent = parent  # Store parent reference
        
        # Get references to settings
        self.settings = parent.settings_frame
        
        # Create preview area
        self.preview_label = ttk.Label(self)
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Create start button
        self.start_button = ttk.Button(
            self,
            text="Start Camera",
            command=self.toggle_camera
        )
        self.start_button.pack(side=tk.BOTTOM, pady=5)
        
        # Initialize processing variables
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=2)
        self.processing_thread = None

    def toggle_camera(self):
        if not self.is_running:
            if not self.settings.background_path.get():
                messagebox.showerror("Error", "Please select a background image first")
                return
                
            self.is_running = True
            self.start_button.config(text="Stop")
            
            # Disable runtime controls
            self.settings.disable_runtime_controls()
            
            self.processing_thread = threading.Thread(target=self.process_camera)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            self.update_preview()
        else:
            self.is_running = False
            self.start_button.config(text="Start Camera")
            
            # Re-enable runtime controls
            self.settings.enable_runtime_controls()

    def process_camera(self):
        # Initialize MediaPipe
        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(
            model_selection=self.settings.model_selection.get()
        )

        try:
            # Extract device paths
            input_match = re.search(r"\((/dev/video\d+)\)", self.settings.input_device.get())
            output_match = re.search(r"\((/dev/video\d+)\)", self.settings.output_device.get())
            
            if not input_match or not output_match:
                raise ValueError("Invalid device selection")
                
            input_device = input_match.group(1)
            output_device = output_match.group(1)
            device_num = int(input_device.replace('/dev/video', ''))
            
            # Open camera with V4L2
            cap = cv2.VideoCapture(device_num, cv2.CAP_V4L2)
            if not cap.isOpened():
                raise RuntimeError(f"Could not open camera {input_device}")

            # Set camera properties
            width, height = map(int, self.settings.resolution.get().split('x'))
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

            # Set up FFmpeg process
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-f', 'rawvideo',
                '-pixel_format', 'bgr24',
                '-video_size', f'{width}x{height}',
                '-framerate', str(self.settings.fps.get()),
                '-i', '-',
                '-f', 'v4l2',
                output_device
            ]

            ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

            # Load background
            background_image = cv2.imread(self.settings.background_path.get())
            background_image = cv2.resize(background_image, (width, height))

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break

                # Apply scaling if needed
                scale = self.settings.scale.get()
                if scale != 1.0:
                    new_width = int(frame.shape[1] * scale)
                    new_height = int(frame.shape[0] * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                    background_image = cv2.resize(background_image, (new_width, new_height))

                # Process frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = selfie_segmentation.process(frame_rgb)
                
                # Create mask
                mask = results.segmentation_mask
                kernel_size = self.settings.smooth_kernel.get()
                if kernel_size % 2 == 0:
                    kernel_size += 1
                    
                sigma = max(0.1, self.settings.smooth_sigma.get())
                
                mask = cv2.GaussianBlur(
                    mask.astype(np.float32),
                    (kernel_size, kernel_size),
                    sigma
                )
                
                # Ensure mask is in correct range [0,1]
                mask = np.clip(mask, 0, 1)
                mask = np.stack((mask,) * 3, axis=-1)
                
                # Combine foreground and background
                output_frame = (frame * mask + background_image * (1 - mask)).astype(np.uint8)
                
                # Write to FFmpeg
                ffmpeg_process.stdin.write(output_frame.tobytes())
                
                # Update preview
                try:
                    self.frame_queue.put_nowait(output_frame)
                except queue.Full:
                    pass

            # Cleanup
            cap.release()
            ffmpeg_process.stdin.close()
            ffmpeg_process.wait()
            selfie_segmentation.close()

        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {str(e)}")
            self.is_running = False

    def update_preview(self):
        if not self.frame_queue.empty():
            frame = self.frame_queue.get_nowait()
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            photo = ImageTk.PhotoImage(image=image)
            self.preview_label.configure(image=photo)
            self.preview_label.image = photo
            
        if self.is_running:
            self.parent.after(10, self.update_preview)  # Use parent instead of root
