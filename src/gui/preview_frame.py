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
    def __init__(self, master):
        super().__init__(master, text=master.tr('camera_preview'))
        self.master = master
        
        # Initialize runtime variables
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=2)
        
        # Use master's variables
        self.show_preview = master.show_preview
        
        # Create preview label
        self.preview_label = ttk.Label(self)
        self.preview_label.pack(expand=True, fill=tk.BOTH)
        
        # Create control buttons
        self.create_controls()

    def create_controls(self):
        # Control buttons frame
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Start/Stop button
        self.start_button = ttk.Button(
            control_frame,
            text=self.master.tr('start_camera'),
            command=self.toggle_camera
        )
        self.start_button.pack(side=tk.RIGHT)
        
        # Show preview checkbox
        self.preview_check = ttk.Checkbutton(
            control_frame,
            text=self.master.tr('show_preview'),
            variable=self.show_preview
        )
        self.preview_check.pack(side=tk.LEFT)

    def toggle_camera(self):
        """Toggle camera on/off"""
        if not self.is_running:
            # Check if background is selected
            if not self.master.settings_frame.background_path.get():
                messagebox.showerror(
                    self.master.tr('error'),
                    self.master.tr('select_background_first')
                )
                return
            
            # Start camera
            self.is_running = True
            self.start_button.configure(text=self.master.tr('stop_camera'))
            self.camera_thread = threading.Thread(target=self.camera_loop)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            
            # Start preview updates if enabled
            if self.show_preview.get():
                self.update_preview()
        else:
            # Stop camera
            self.is_running = False
            self.start_button.configure(text=self.master.tr('start_camera'))

    def camera_loop(self):
        # Initialize MediaPipe
        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

        try:
            # Get device paths
            input_path = re.search(r"\((/dev/video\d+)\)", 
                self.master.settings_frame.input_device.get()).group(1)
            output_path = re.search(r"\((/dev/video\d+)\)", 
                self.master.settings_frame.output_device.get()).group(1)
            
            # Open input camera
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise Exception(f"Could not open input device: {input_path}")
            
            # Set resolution
            width, height = map(int, self.master.settings_frame.resolution.get().split('x'))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Track last FPS value
            last_fps = self.master.settings_frame.fps.get()
            
            # Create FFmpeg process
            def create_ffmpeg_process():
                command = [
                    'ffmpeg',
                    '-f', 'rawvideo',
                    '-pix_fmt', 'bgr24',
                    '-s', f'{width}x{height}',
                    '-r', str(self.master.settings_frame.fps.get()),
                    '-i', '-',
                    '-f', 'v4l2',
                    '-pix_fmt', 'yuv420p',
                    output_path
                ]
                return subprocess.Popen(command, stdin=subprocess.PIPE)
            
            self.ffmpeg_process = create_ffmpeg_process()
            
            # Load and store original background
            original_background = cv2.imread(self.master.settings_frame.background_path.get())
            if original_background is None:
                messagebox.showerror("Error", "Could not load background image")
                self.is_running = False
                return
            
            # Initial resize to match frame dimensions
            background_image = cv2.resize(original_background, (width, height))
            last_scale = self.master.settings_frame.scale.get()

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break

                # Check if FPS changed
                current_fps = self.master.settings_frame.fps.get()
                if current_fps != last_fps:
                    # Restart FFmpeg process with new FPS
                    self.ffmpeg_process.stdin.close()
                    self.ffmpeg_process.wait()
                    self.ffmpeg_process = create_ffmpeg_process()
                    last_fps = current_fps

                # Get current scale
                current_scale = self.master.settings_frame.scale.get()
                
                # Always resize both frame and background together
                scaled_width = int(width * current_scale)
                scaled_height = int(height * current_scale)
                frame = cv2.resize(frame, (scaled_width, scaled_height))
                
                # Only resize background from original if scale changed
                if current_scale != last_scale:
                    background_image = cv2.resize(original_background, (scaled_width, scaled_height))
                    last_scale = current_scale

                # Process frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = selfie_segmentation.process(frame_rgb)
                
                # Create mask
                mask = results.segmentation_mask
                kernel_size = self.master.settings_frame.smooth_kernel.get()
                if kernel_size % 2 == 0:
                    kernel_size += 1
                    
                sigma = max(0.1, self.master.settings_frame.smooth_sigma.get())
                
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
                self.ffmpeg_process.stdin.write(output_frame.tobytes())
                
                # Update preview
                try:
                    self.frame_queue.put_nowait(output_frame)
                except queue.Full:
                    pass

            # Cleanup
            cap.release()
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()
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
            # Calculate delay in milliseconds based on FPS
            delay = int(1000 / self.master.settings_frame.fps.get())
            self.master.after(delay, self.update_preview)

    def update_labels(self):
        """Update all labels to current language"""
        # Update the LabelFrame text
        self.configure(text=self.master.tr('camera_preview'))
        # Update other labels
        self.start_button.configure(
            text=self.master.tr('stop_camera') if self.is_running 
            else self.master.tr('start_camera')
        )
        self.preview_check.configure(text=self.master.tr('show_preview'))

    def update_values(self):
        """Update all widget values from settings"""
        # Update start/stop button text
        self.start_button.configure(
            text=self.master.tr('stop_camera') if self.is_running 
            else self.master.tr('start_camera')
        )
