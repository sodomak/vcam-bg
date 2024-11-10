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
            
            # Load and store original background at original resolution
            original_background = cv2.imread(self.master.settings_frame.background_path.get())
            if original_background is None:
                messagebox.showerror("Error", "Could not load background image")
                self.is_running = False
                return
            
            # Initial resize to match frame dimensions
            background_image = cv2.resize(original_background, (width, height))

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break

                # Ensure frame matches target dimensions
                frame = cv2.resize(frame, (width, height))
                
                # Process frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = selfie_segmentation.process(frame_rgb)
                
                # Create and smooth mask
                mask = results.segmentation_mask
                
                # Get kernel size and ensure it's odd
                kernel_size = max(3, self.master.settings_frame.smooth_kernel.get())
                if kernel_size % 2 == 0:
                    kernel_size += 1
                kernel_tuple = (kernel_size, kernel_size)
                
                mask = cv2.GaussianBlur(
                    mask.astype(np.float32),
                    kernel_tuple,
                    sigmaX=float(self.master.settings_frame.smooth_sigma.get()),
                    sigmaY=float(self.master.settings_frame.smooth_sigma.get())
                )

                # Extract person and apply flips before positioning
                person_only = frame.copy()
                if self.master.settings_frame.flip_h.get():
                    person_only = cv2.flip(person_only, 1)
                    mask = cv2.flip(mask, 1)  # Also flip the mask
                if self.master.settings_frame.flip_v.get():
                    person_only = cv2.flip(person_only, 0)
                    mask = cv2.flip(mask, 0)  # Also flip the mask

                # Continue with positioning and scaling...

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
                
                # Get current scale and position
                scaled_width = int(width * current_scale)
                scaled_height = int(height * current_scale)
                
                # Calculate position based on offset settings
                x_pos = int((width - scaled_width) * self.master.settings_frame.x_offset.get())
                y_pos = int((height - scaled_height) * self.master.settings_frame.y_offset.get())
                
                # Create output frame with background
                output_frame = background_image.copy()
                
                # Scale person and mask if needed
                if current_scale != 1.0:
                    scaled_person = cv2.resize(person_only, (scaled_width, scaled_height))
                    scaled_mask = cv2.resize(mask, (scaled_width, scaled_height))
                else:
                    scaled_person = person_only
                    scaled_mask = mask
                
                # Create a full-size mask with the person at offset position
                full_mask = np.zeros((height, width))
                # Ensure we don't exceed image boundaries
                y_start = max(0, y_pos)
                y_end = min(height, y_pos + scaled_height)
                x_start = max(0, x_pos)
                x_end = min(width, x_pos + scaled_width)
                
                # Calculate source region for person
                src_y_start = max(0, -y_pos)
                src_x_start = max(0, -x_pos)
                
                # Place person and mask
                full_mask[y_start:y_end, x_start:x_end] = \
                    scaled_mask[src_y_start:src_y_start + (y_end - y_start),
                              src_x_start:src_x_start + (x_end - x_start)]
                output_frame[y_start:y_end, x_start:x_end] = \
                    scaled_person[src_y_start:src_y_start + (y_end - y_start),
                                src_x_start:src_x_start + (x_end - x_start)]
                
                # Stack mask for final composition
                full_mask = np.stack((full_mask,) * 3, axis=-1)
                
                # Combine with background
                output_frame = (output_frame * full_mask + 
                               background_image * (1 - full_mask)).astype(np.uint8)
                
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
