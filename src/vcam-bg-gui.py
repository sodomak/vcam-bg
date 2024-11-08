#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import mediapipe as mp
import numpy as np
import subprocess
import re
import os
import time
from PIL import Image, ImageTk
from threading import Thread
import queue
import json
import os.path

class VCamBackgroundGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Camera Background")
        self.config_file = os.path.expanduser("~/.config/vcam-bg/config.json")
        
        # Create menu references
        self.file_menu = None
        self.view_menu = None
        
        # Create default settings
        self.default_settings = {
            'input_device': '',
            'output_device': '/dev/video2',
            'background_path': '',
            'model_selection': 1,
            'fps': 20.0,
            'scale': 1.0,
            'show_preview': True,
            'smooth_kernel': 21,
            'smooth_sigma': 10.0,
            'resolution': '1280x720'
        }
        
        # Initialize variables with loaded or default settings
        self.load_settings()
        
        # Create GUI (after settings are loaded)
        self.create_gui()
        
        # Set up theme (after GUI is created)
        self.setup_theme()
        
        # Runtime variables
        self.is_running = False
        self.frame_queue = queue.Queue(maxsize=2)
        
        # Load camera devices
        self.load_camera_devices()
        
        # Update GUI with loaded settings
        self.apply_loaded_settings()

    def setup_theme(self, force_dark=None):
        """Configure application theme based on system settings or force a theme
        Args:
            force_dark (bool|None): Force dark theme if True, light if False, or use system setting if None
        """
        try:
            if force_dark is None:
                # Try to detect system theme (GNOME)
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                    capture_output=True, text=True
                )
                is_dark = 'dark' in result.stdout.lower()
            else:
                is_dark = force_dark

            style = ttk.Style()
            
            if is_dark:
                # Dark theme colors
                style.theme_use('clam')
                self.root.configure(bg='#2e2e2e')
                style.configure('.', background='#2e2e2e', foreground='#ffffff')
                style.configure('TLabel', background='#2e2e2e', foreground='#ffffff')
                style.configure('TFrame', background='#2e2e2e')
                style.configure('TLabelframe', background='#2e2e2e', foreground='#ffffff')
                style.configure('TLabelframe.Label', background='#2e2e2e', foreground='#ffffff')
                style.configure('TButton', background='#404040', foreground='#ffffff')
                style.configure('TCheckbutton', background='#2e2e2e', foreground='#ffffff')
                style.configure('TRadiobutton', background='#2e2e2e', foreground='#ffffff')
                style.configure('TScale', background='#2e2e2e', troughcolor='#404040')
                style.configure('TCombobox', 
                    fieldbackground='#404040', 
                    background='#404040',
                    foreground='#ffffff',
                    selectbackground='#606060',
                    selectforeground='#ffffff'
                )
                
                # Menu colors
                menubar = self.root.winfo_children()[0]
                if isinstance(menubar, tk.Menu):
                    menubar.configure(
                        bg='#2e2e2e',
                        fg='#ffffff',
                        activebackground='#404040',
                        activeforeground='#ffffff'
                    )
                    for menu in [self.file_menu, self.view_menu]:
                        if menu:
                            menu.configure(
                                bg='#2e2e2e',
                                fg='#ffffff',
                                activebackground='#404040',
                                activeforeground='#ffffff'
                            )
            else:
                # Light theme colors
                style.theme_use('default')
                self.root.configure(bg='#f0f0f0')  # Light gray background
                style.configure('.', background='#f0f0f0', foreground='#000000')
                style.configure('TLabel', background='#f0f0f0', foreground='#000000')
                style.configure('TFrame', background='#f0f0f0')
                style.configure('TLabelframe', background='#f0f0f0', foreground='#000000')
                style.configure('TLabelframe.Label', background='#f0f0f0', foreground='#000000')
                style.configure('TButton', background='#e0e0e0', foreground='#000000')
                style.configure('TCheckbutton', background='#f0f0f0', foreground='#000000')
                style.configure('TRadiobutton', background='#f0f0f0', foreground='#000000')
                style.configure('TScale', background='#f0f0f0', troughcolor='#e0e0e0')
                style.configure('TCombobox', 
                    fieldbackground='#ffffff', 
                    background='#ffffff',
                    foreground='#000000',
                    selectbackground='#0078d7',
                    selectforeground='#ffffff'
                )
                
                # Menu colors
                menubar = self.root.winfo_children()[0]
                if isinstance(menubar, tk.Menu):
                    menubar.configure(
                        bg='#f0f0f0',
                        fg='#000000',
                        activebackground='#0078d7',
                        activeforeground='#ffffff'
                    )
                    for menu in [self.file_menu, self.view_menu]:
                        if menu:
                            menu.configure(
                                bg='#f0f0f0',
                                fg='#000000',
                                activebackground='#0078d7',
                                activeforeground='#ffffff'
                            )

            # Force redraw
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"Error setting theme: {e}")
            # Continue with default theme if something goes wrong
            pass

    def load_settings(self):
        """Load settings from config file or use defaults"""
        # Initialize variables with default values first
        self.input_device = tk.StringVar(value=self.default_settings['input_device'])
        self.output_device = tk.StringVar(value=self.default_settings['output_device'])
        self.background_path = tk.StringVar(value=self.default_settings['background_path'])
        self.model_selection = tk.IntVar(value=self.default_settings['model_selection'])
        self.fps = tk.DoubleVar(value=self.default_settings['fps'])
        self.scale = tk.DoubleVar(value=self.default_settings['scale'])
        self.show_preview = tk.BooleanVar(value=self.default_settings['show_preview'])
        self.smooth_kernel = tk.IntVar(value=self.default_settings['smooth_kernel'])
        self.smooth_sigma = tk.DoubleVar(value=self.default_settings['smooth_sigma'])
        self.resolution = tk.StringVar(value=self.default_settings['resolution'])
        
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    settings = json.load(f)
                    
                    # Update variables with saved settings
                    for key, value in settings.items():
                        if hasattr(self, key):
                            getattr(self, key).set(value)
                
        except Exception as e:
            print(f"Error loading settings: {e}")

    def apply_loaded_settings(self):
        """Apply loaded settings to GUI elements"""
        # Update resolution combo
        if hasattr(self, 'resolution_combo'):
            self.resolution_combo.set(self.resolution.get())
        
        # Update FPS label
        if hasattr(self, 'fps_label'):
            self.fps_label.config(text=f"{self.fps.get():.1f}")
        
        # Update scale label
        if hasattr(self, 'scale_label'):
            self.scale_label.config(text=f"{self.scale.get():.2f}")
        
        # Update kernel label
        if hasattr(self, 'kernel_label'):
            self.kernel_label.config(text=str(self.smooth_kernel.get()))
        
        # Update sigma label
        if hasattr(self, 'sigma_label'):
            self.sigma_label.config(text=f"{self.smooth_sigma.get():.1f}")
        
        # Update preview checkbox
        if hasattr(self, 'preview_check'):
            if self.show_preview.get():
                self.preview_check.invoke()
        
        # Update model selection
        if hasattr(self, 'model_radio'):
            for radio in self.model_radio:
                if radio['value'] == self.model_selection.get():
                    radio.invoke()
        
        # Update background path label
        if hasattr(self, 'bg_label'):
            self.bg_label.config(text=self.background_path.get())

    def save_settings(self):
        """Save current settings to config file"""
        settings = {
            'input_device': self.input_device.get(),
            'output_device': self.output_device.get(),
            'background_path': self.background_path.get(),
            'model_selection': self.model_selection.get(),
            'fps': self.fps.get(),
            'scale': self.scale.get(),
            'show_preview': self.show_preview.get(),
            'smooth_kernel': self.smooth_kernel.get(),
            'smooth_sigma': self.smooth_sigma.get(),
            'resolution': self.resolution_combo.get()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def export_settings(self):
        """Export settings to a user-specified file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                settings = {
                    'input_device': self.input_device.get(),
                    'output_device': self.output_device.get(),
                    'background_path': self.background_path.get(),
                    'model_selection': self.model_selection.get(),
                    'fps': self.fps.get(),
                    'scale': self.scale.get(),
                    'show_preview': self.show_preview.get(),
                    'smooth_kernel': self.smooth_kernel.get(),
                    'smooth_sigma': self.smooth_sigma.get(),
                    'resolution': self.resolution_combo.get()
                }
                with open(filename, 'w') as f:
                    json.dump(settings, f, indent=4)
                messagebox.showinfo("Success", "Settings exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export settings: {e}")

    def import_settings(self):
        """Import settings from a user-specified file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    settings = json.load(f)
                
                # Update all settings
                self.input_device.set(settings.get('input_device', ''))
                self.output_device.set(settings.get('output_device', '/dev/video2'))
                self.background_path.set(settings.get('background_path', ''))
                self.model_selection.set(settings.get('model_selection', 1))
                self.fps.set(settings.get('fps', 20.0))
                self.scale.set(settings.get('scale', 1.0))
                self.show_preview.set(settings.get('show_preview', True))
                self.smooth_kernel.set(settings.get('smooth_kernel', 21))
                self.smooth_sigma.set(settings.get('smooth_sigma', 10.0))
                if 'resolution' in settings:
                    self.resolution_combo.set(settings['resolution'])
                
                messagebox.showinfo("Success", "Settings imported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {e}")

    def create_gui(self):
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        self.file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Import Settings", command=self.import_settings)
        self.file_menu.add_command(label="Export Settings", command=self.export_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save Settings", command=self.save_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        self.view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Light Theme", command=lambda: self.setup_theme(force_dark=False))
        self.view_menu.add_command(label="Dark Theme", command=lambda: self.setup_theme(force_dark=True))
        self.view_menu.add_command(label="System Theme", command=lambda: self.setup_theme(force_dark=None))
        
        # Camera Settings Frame
        camera_frame = ttk.LabelFrame(self.root, text="Camera Settings", padding=10)
        camera_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Label(camera_frame, text="Input Device:").grid(row=0, column=0, sticky="w")
        self.input_combo = ttk.Combobox(camera_frame, textvariable=self.input_device)
        self.input_combo.grid(row=0, column=1, padx=5, sticky="ew")
        
        ttk.Label(camera_frame, text="Output Device:").grid(row=1, column=0, sticky="w")
        self.output_combo = ttk.Combobox(camera_frame, textvariable=self.output_device)
        self.output_combo.grid(row=1, column=1, padx=5, sticky="ew")
        
        # Background Frame
        bg_frame = ttk.LabelFrame(self.root, text="Background", padding=10)
        bg_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Button(bg_frame, text="Select Background", command=self.select_background).grid(row=0, column=0, sticky="ew")
        self.bg_label = ttk.Label(bg_frame, textvariable=self.background_path)
        self.bg_label.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Advanced Settings Frame
        settings_frame = ttk.LabelFrame(self.root, text="Advanced Settings", padding=10)
        settings_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # Model Selection
        ttk.Label(settings_frame, text="Model:").grid(row=0, column=0, sticky="w")
        self.model_radio = []
        rb1 = ttk.Radiobutton(settings_frame, text="Landscape", variable=self.model_selection, value=0)
        rb1.grid(row=0, column=1)
        rb2 = ttk.Radiobutton(settings_frame, text="Portrait", variable=self.model_selection, value=1)
        rb2.grid(row=0, column=2)
        self.model_radio = [rb1, rb2]
        
        # FPS Slider with value label
        ttk.Label(settings_frame, text="FPS:").grid(row=1, column=0, sticky="w")
        self.fps_entry = ttk.Scale(settings_frame, 
            from_=1, to=60, 
            orient="horizontal", 
            variable=self.fps,
            command=lambda v: self.fps_label.config(text=f"{float(v):.1f}"))
        self.fps_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)
        self.fps_label = ttk.Label(settings_frame, text=f"{self.fps.get():.1f}")
        self.fps_label.grid(row=1, column=3, padx=5)
        
        # Resolution
        ttk.Label(settings_frame, text="Resolution:").grid(row=2, column=0, sticky="w")
        self.resolution_combo = ttk.Combobox(settings_frame, width=20)
        self.resolution_combo.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5)
        
        # Bind input device changes to resolution update
        self.input_combo.bind('<<ComboboxSelected>>', self.update_resolutions)
        
        # Scale Slider with value label
        ttk.Label(settings_frame, text="Scale:").grid(row=3, column=0, sticky="w")
        self.scale_entry = ttk.Scale(settings_frame, 
            from_=0.1, to=2.0, 
            orient="horizontal",
            variable=self.scale,
            command=lambda v: self.scale_label.config(text=f"{float(v):.2f}"))
        self.scale_entry.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5)
        self.scale_label = ttk.Label(settings_frame, text=f"{self.scale.get():.2f}")
        self.scale_label.grid(row=3, column=3, padx=5)
        
        # Smoothing Sliders with value labels
        smooth_frame = ttk.LabelFrame(settings_frame, text="Smoothing", padding=5)
        smooth_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=5)
        
        ttk.Label(smooth_frame, text="Kernel:").grid(row=0, column=0, sticky="w")
        self.kernel_entry = ttk.Scale(smooth_frame, 
            from_=3, to=51, 
            orient="horizontal",
            variable=self.smooth_kernel,
            command=lambda v: self.update_kernel_value(v))
        self.kernel_entry.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5)
        self.kernel_label = ttk.Label(smooth_frame, text=str(self.smooth_kernel.get()))
        self.kernel_label.grid(row=0, column=3, padx=5)
        
        ttk.Label(smooth_frame, text="Sigma:").grid(row=1, column=0, sticky="w")
        self.sigma_entry = ttk.Scale(smooth_frame, 
            from_=0.1, to=20.0, 
            orient="horizontal",
            variable=self.smooth_sigma,
            command=lambda v: self.sigma_label.config(text=f"{float(v):.1f}"))
        self.sigma_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)
        self.sigma_label = ttk.Label(smooth_frame, text=f"{self.smooth_sigma.get():.1f}")
        self.sigma_label.grid(row=1, column=3, padx=5)
        
        # Preview checkbox
        ttk.Checkbutton(settings_frame, text="Show Preview", variable=self.show_preview).grid(row=5, column=0, columnspan=2)
        
        # Preview Frame
        preview_frame = ttk.LabelFrame(self.root, text="Preview", padding=10)
        preview_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.grid(row=0, column=0, sticky="nsew")
        
        # Control buttons
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.grid(row=4, column=0, padx=10, pady=5, sticky="ew")
        
        self.start_button = ttk.Button(control_frame, text="Start", command=self.toggle_camera)
        self.start_button.grid(row=0, column=0, padx=5)

    def load_camera_devices(self):
        try:
            output = subprocess.check_output("v4l2-ctl --list-devices", shell=True).decode("utf-8")
            devices = re.findall(r"(.*):\n\t(/dev/video\d+)", output)
            
            input_devices = []
            output_devices = []
            
            for name, path in devices:
                name = name.strip()
                if "v4l2loopback" in name:
                    output_devices.append(f"{name} ({path})")
                else:
                    input_devices.append(f"{name} ({path})")
            
            self.input_combo['values'] = input_devices
            self.output_combo['values'] = output_devices
            
            # Set saved values if they exist in the available devices
            saved_input = self.input_device.get()
            saved_output = self.output_device.get()
            
            if saved_input and saved_input in input_devices:
                self.input_device.set(saved_input)
            elif input_devices:
                self.input_device.set(input_devices[0])
                
            if saved_output and saved_output in output_devices:
                self.output_device.set(saved_output)
            elif output_devices:
                self.output_device.set(output_devices[0])
                
            # Update resolutions for selected input device
            self.update_resolutions()
                
        except subprocess.CalledProcessError:
            print("Error: Could not retrieve camera list")

    def select_background(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if filename:
            self.background_path.set(filename)

    def toggle_camera(self):
        if not self.is_running:
            if not self.background_path.get():
                tk.messagebox.showerror("Error", "Please select a background image first")
                return
                
            self.is_running = True
            self.start_button.config(text="Stop")
            
            # Disable controls that require restart
            self.input_combo.config(state='disabled')
            self.output_combo.config(state='disabled')
            self.fps_entry.config(state='disabled')
            self.resolution_combo.config(state='disabled')  # Disable resolution combo
            
            self.camera_thread = Thread(target=self.process_camera)
            self.camera_thread.daemon = True
            self.camera_thread.start()
            self.update_preview()
        else:
            self.is_running = False
            self.start_button.config(text="Start")
            
            # Re-enable controls
            self.input_combo.config(state='normal')
            self.output_combo.config(state='normal')
            self.fps_entry.config(state='normal')
            self.resolution_combo.config(state='normal')  # Re-enable resolution combo
            
            # Save settings when stopping
            self.save_settings()

    def process_camera(self):
        # Initialize MediaPipe
        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=self.model_selection.get())

        try:
            # Extract device number from path
            input_device = re.search(r"\((/dev/video\d+)\)", self.input_device.get()).group(1)
            output_device = re.search(r"\((/dev/video\d+)\)", self.output_device.get()).group(1)
            device_num = int(input_device.replace('/dev/video', ''))

            # Open camera with direct V4L2 backend
            cap = cv2.VideoCapture(device_num, cv2.CAP_V4L2)
            if not cap.isOpened():
                messagebox.showerror("Error", f"Could not open camera {input_device}")
                self.is_running = False
                return

            # Get and set resolution
            if self.resolution_combo.get():
                width, height = map(int, self.resolution_combo.get().split('x'))
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                
                # Verify the settings were applied
                actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                if actual_width != width or actual_height != height:
                    print(f"Warning: Camera using {actual_width}x{actual_height} instead of requested {width}x{height}")
                    width, height = actual_width, actual_height

            # Apply scaling
            width = int(width * self.scale.get())
            height = int(height * self.scale.get())

            # Load and resize background image
            background_image = cv2.imread(self.background_path.get())
            background_image = cv2.resize(background_image, (width, height))

            # Set up FFmpeg process
            ffmpeg_cmd = [
                'ffmpeg', '-y', 
                '-f', 'rawvideo',
                '-pixel_format', 'bgr24',
                '-video_size', f'{width}x{height}',
                '-framerate', str(self.fps.get()),
                '-i', '-',
                '-f', 'v4l2',
                output_device  # Use extracted path
            ]

            try:
                ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start FFmpeg: {e}")
                self.is_running = False
                return

            # Add variables to track changes
            last_background = self.background_path.get()
            last_scale = self.scale.get()

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break

                # Check if background changed
                if last_background != self.background_path.get():
                    background_image = cv2.imread(self.background_path.get())
                    background_image = cv2.resize(background_image, (width, height))
                    last_background = self.background_path.get()

                # Check if scale changed
                if last_scale != self.scale.get():
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * self.scale.get())
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * self.scale.get())
                    background_image = cv2.resize(background_image, (width, height))
                    last_scale = self.scale.get()

                frame = cv2.resize(frame, (width, height))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = selfie_segmentation.process(frame_rgb)
                
                # Create and smooth mask - fixed kernel size handling
                try:
                    # Ensure kernel size is an odd integer tuple
                    kernel_size = int(self.smooth_kernel.get())
                    if kernel_size % 2 == 0:
                        kernel_size += 1
                    kernel_tuple = (kernel_size, kernel_size)
                    
                    mask = results.segmentation_mask
                    mask = cv2.GaussianBlur(
                        mask, 
                        kernel_tuple,  # Pass as tuple
                        sigmaX=float(self.smooth_sigma.get()),
                        sigmaY=float(self.smooth_sigma.get())
                    )
                    mask = np.stack((mask,) * 3, axis=-1)
                except Exception as e:
                    print(f"Error applying smoothing: {e}")
                    continue
                
                # Combine foreground and background
                output_frame = (frame * mask + background_image * (1 - mask)).astype(np.uint8)
                
                # Put frame in queue for preview if enabled
                if self.show_preview.get():
                    try:
                        self.frame_queue.put_nowait(output_frame)
                    except queue.Full:
                        pass
                    
                # Write to FFmpeg process
                try:
                    ffmpeg_process.stdin.write(output_frame.tobytes())
                except BrokenPipeError:
                    print("FFmpeg pipe closed unexpectedly.")
                    break

            # Cleanup
            cap.release()
            ffmpeg_process.stdin.close()
            ffmpeg_process.wait()
            selfie_segmentation.close()

        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {str(e)}")
            self.is_running = False
            return

    def update_preview(self):
        try:
            if not self.frame_queue.empty():
                frame = self.frame_queue.get_nowait()
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                photo = ImageTk.PhotoImage(image)
                self.preview_label.configure(image=photo)
                self.preview_label.image = photo
        except queue.Empty:
            pass
            
        if self.is_running:
            self.root.after(10, self.update_preview)

    def update_kernel_value(self, value):
        # Ensure kernel size is odd
        kernel_size = int(float(value))
        if kernel_size % 2 == 0:
            kernel_size += 1
        self.smooth_kernel.set(kernel_size)
        self.kernel_label.config(text=str(kernel_size))

    def get_device_resolutions(self, device_path):
        try:
            # Get supported formats
            output = subprocess.check_output(f"v4l2-ctl --device={device_path} --list-formats-ext", shell=True).decode()
            
            # Parse resolutions from the output
            resolutions = set()  # Using set to avoid duplicates
            for match in re.finditer(r"Size: Discrete (\d+x\d+)", output):
                resolutions.add(match.group(1))
            
            # Add some common fallback resolutions if none found
            if not resolutions:
                common_res = ['640x480', '1280x720', '1920x1080']
                for res in common_res:
                    resolutions.add(res)
            
            return sorted(list(resolutions), 
                         key=lambda x: tuple(map(int, x.split('x'))))  # Sort by resolution size
        except subprocess.CalledProcessError:
            print(f"Error: Could not get resolutions for {device_path}")
            return ['640x480', '1280x720', '1920x1080']  # Return common defaults

    def update_resolutions(self, *args):
        # Called when input device is changed
        if not self.input_device.get():
            return
            
        try:
            device_path = re.search(r"\((/dev/video\d+)\)", self.input_device.get()).group(1)
            resolutions = self.get_device_resolutions(device_path)
            self.resolution_combo['values'] = resolutions
            if resolutions:
                self.resolution_combo.set(resolutions[0])
        except (AttributeError, IndexError):
            print("Error parsing device path")

def main():
    root = tk.Tk()
    app = VCamBackgroundGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 