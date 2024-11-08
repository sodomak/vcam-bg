import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import re
import os
import cv2

class SettingsFrame(ttk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text=master.tr('settings'))
        self.master = master
        
        # Initialize variables with settings from master
        self.input_device = tk.StringVar(value=master.settings['input_device'])
        self.output_device = tk.StringVar(value=master.settings['output_device'])
        self.background_path = tk.StringVar(value=master.settings['background_path'])
        self.model_selection = tk.IntVar(value=master.settings['model_selection'])
        self.fps = tk.DoubleVar(value=master.settings['fps'])
        self.scale = tk.DoubleVar(value=master.settings['scale'])
        self.smooth_kernel = tk.IntVar(value=master.settings['smooth_kernel'])
        self.smooth_sigma = tk.DoubleVar(value=master.settings['smooth_sigma'])
        self.resolution = tk.StringVar(value=master.settings['resolution'])
        
        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        """Create all widgets in the settings frame"""
        # Input device
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        self.input_label = ttk.Label(input_frame, text=self.master.tr('input_device'))
        self.input_label.pack(side=tk.LEFT)
        self.input_combo = ttk.Combobox(input_frame, textvariable=self.input_device, state='readonly')
        self.input_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Output device
        output_frame = ttk.Frame(self)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        self.output_label = ttk.Label(output_frame, text=self.master.tr('output_device'))
        self.output_label.pack(side=tk.LEFT)
        self.output_combo = ttk.Combobox(output_frame, textvariable=self.output_device, state='readonly')
        self.output_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Background
        bg_frame = ttk.Frame(self)
        bg_frame.pack(fill=tk.X, pady=(0, 10))
        self.bg_label = ttk.Label(bg_frame, text=self.master.tr('background'))
        self.bg_label.pack(side=tk.LEFT)
        self.bg_button = ttk.Button(bg_frame, text=self.master.tr('select_background'), command=self.select_background)
        self.bg_button.pack(side=tk.RIGHT)

        # Model selection
        model_frame = ttk.Frame(self)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        self.model_label = ttk.Label(model_frame, text=self.master.tr('model'))
        self.model_label.pack(side=tk.LEFT)
        self.landscape_radio = ttk.Radiobutton(model_frame, text=self.master.tr('landscape'), value=1, variable=self.model_selection)
        self.landscape_radio.pack(side=tk.LEFT)
        self.portrait_radio = ttk.Radiobutton(model_frame, text=self.master.tr('portrait'), value=2, variable=self.model_selection)
        self.portrait_radio.pack(side=tk.LEFT)

        # Resolution
        res_frame = ttk.Frame(self)
        res_frame.pack(fill=tk.X, pady=(0, 10))
        self.resolution_label = ttk.Label(res_frame, text=self.master.tr('resolution'))
        self.resolution_label.pack(side=tk.LEFT)
        self.resolution_combo = ttk.Combobox(res_frame, textvariable=self.resolution, state='readonly')
        self.resolution_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # FPS
        fps_frame = ttk.Frame(self)
        fps_frame.pack(fill=tk.X, pady=(0, 10))
        self.fps_label = ttk.Label(fps_frame, text=self.master.tr('fps'))
        self.fps_label.pack(side=tk.LEFT)
        self.fps_value_label = ttk.Label(fps_frame, text="20.0")
        self.fps_value_label.pack(side=tk.RIGHT)
        self.fps_scale = ttk.Scale(self, from_=1, to=60, variable=self.fps, orient=tk.HORIZONTAL)
        self.fps_scale.pack(fill=tk.X)

        # Scale
        scale_frame = ttk.Frame(self)
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        self.scale_label = ttk.Label(scale_frame, text=self.master.tr('scale'))
        self.scale_label.pack(side=tk.LEFT)
        self.scale_value_label = ttk.Label(scale_frame, text="1.0")
        self.scale_value_label.pack(side=tk.RIGHT)
        self.scale_scale = ttk.Scale(self, from_=0.1, to=2.0, variable=self.scale, orient=tk.HORIZONTAL)
        self.scale_scale.pack(fill=tk.X)

        # Smoothing
        self.smooth_frame = ttk.LabelFrame(self, text=self.master.tr('smoothing'))
        self.smooth_frame.pack(fill=tk.X, pady=(0, 10))

        # Kernel
        kernel_frame = ttk.Frame(self.smooth_frame)
        kernel_frame.pack(fill=tk.X, pady=(5, 5))
        self.kernel_label = ttk.Label(kernel_frame, text=self.master.tr('kernel'))
        self.kernel_label.pack(side=tk.LEFT)
        self.kernel_value_label = ttk.Label(kernel_frame, text="21")
        self.kernel_value_label.pack(side=tk.RIGHT)
        self.kernel_scale = ttk.Scale(self.smooth_frame, from_=3, to=51, variable=self.smooth_kernel, orient=tk.HORIZONTAL)
        self.kernel_scale.pack(fill=tk.X)

        # Sigma
        sigma_frame = ttk.Frame(self.smooth_frame)
        sigma_frame.pack(fill=tk.X, pady=(5, 5))
        self.sigma_label = ttk.Label(sigma_frame, text=self.master.tr('sigma'))
        self.sigma_label.pack(side=tk.LEFT)
        self.sigma_value_label = ttk.Label(sigma_frame, text="10.0")
        self.sigma_value_label.pack(side=tk.RIGHT)
        self.sigma_scale = ttk.Scale(self.smooth_frame, from_=0.1, to=20.0, variable=self.smooth_sigma, orient=tk.HORIZONTAL)
        self.sigma_scale.pack(fill=tk.X)

    def select_background(self):
        """Open file dialog to select background image"""
        filename = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.background_path.set(filename)

    def load_camera_devices(self):
        """Load available input and output devices"""
        try:
            # Input devices (webcams)
            input_devices = []
            for i in range(10):  # Check first 10 video devices
                device = f"/dev/video{i}"
                if os.path.exists(device):
                    # Check if it's a capture device
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        name = self.get_device_name(device)
                        input_devices.append(f"{name} ({device})")
                    cap.release()
            
            # Output devices (v4l2loopback)
            output_devices = []
            for i in range(10):  # Check first 10 video devices
                device = f"/dev/video{i}"
                if os.path.exists(device):
                    # Check if it's a v4l2loopback device
                    try:
                        result = subprocess.run(
                            ['v4l2-ctl', '--device', device, '--all'],
                            capture_output=True,
                            text=True
                        )
                        if 'v4l2loopback' in result.stdout:
                            name = self.get_device_name(device)
                            output_devices.append(f"{name} ({device})")
                    except subprocess.CalledProcessError:
                        continue

            # Update comboboxes
            self.input_combo['values'] = input_devices
            self.output_combo['values'] = output_devices
            
            # Set defaults if no selection
            if not self.input_device.get() and input_devices:
                self.input_device.set(input_devices[0])
            if not self.output_device.get() and output_devices:
                self.output_device.set(output_devices[0])
                
        except Exception as e:
            print(f"Error loading camera devices: {e}")

    def get_device_name(self, device_path):
        """Get friendly name of a video device"""
        try:
            result = subprocess.run(
                ['v4l2-ctl', '--device', device_path, '--all'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if 'Card type' in line:
                    return line.split(':')[1].strip()
        except:
            pass
        return os.path.basename(device_path)

    def update_resolutions(self, *args):
        """Update available resolutions for selected camera"""
        if not self.input_device.get():
            return
            
        try:
            device_path = re.search(r"\((/dev/video\d+)\)", self.input_device.get()).group(1)
            resolutions = self.get_device_resolutions(device_path)
            self.resolution_combo['values'] = resolutions
            if resolutions and not self.resolution.get():
                self.resolution.set(resolutions[0])
        except (AttributeError, IndexError):
            print("Error parsing device path")

    def get_device_resolutions(self, device_path):
        """Get available resolutions for camera device"""
        try:
            output = subprocess.check_output(
                f"v4l2-ctl --device={device_path} --list-formats-ext",
                shell=True
            ).decode()
            
            resolutions = set()
            for match in re.finditer(r"Size: Discrete (\d+x\d+)", output):
                resolutions.add(match.group(1))
            
            if not resolutions:
                resolutions = {'640x480', '1280x720', '1920x1080'}
            
            return sorted(list(resolutions), 
                         key=lambda x: tuple(map(int, x.split('x'))))
        except subprocess.CalledProcessError:
            print(f"Error: Could not get resolutions for {device_path}")
            return ['640x480', '1280x720', '1920x1080']

    def update_kernel_value(self, value):
        """Ensure kernel size is always odd and update label"""
        kernel_size = int(float(value))
        if kernel_size % 2 == 0:
            kernel_size += 1
        self.smooth_kernel.set(kernel_size)
        self.kernel_label.configure(text=str(kernel_size))

    def disable_runtime_controls(self):
        """Disable controls that can't be changed while camera is running"""
        for control in self.runtime_controls:
            control.configure(state='disabled')

    def enable_runtime_controls(self):
        """Enable controls after camera is stopped"""
        for control in self.runtime_controls:
            control.configure(state='readonly' if isinstance(control, ttk.Combobox) else 'normal')

    def reset_to_defaults(self):
        """Reset all settings to default values"""
        self.input_device.set('')
        self.output_device.set('/dev/video2')
        self.background_path.set('')
        self.model_selection.set(1)
        self.fps.set(20.0)
        self.scale.set(1.0)
        self.resolution.set('1280x720')
        self.smooth_kernel.set(21)
        self.smooth_sigma.set(10.0)
        
        # Update labels
        self.fps_label.configure(text="20.0")
        self.scale_label.configure(text="1.0")
        self.kernel_label.configure(text="21")
        self.sigma_label.configure(text="10.0")
        
        # Reload camera devices
        self.load_camera_devices()

    def update_labels(self):
        """Update all labels to current language"""
        self.configure(text=self.master.tr('settings'))
        
        # Update all labels
        self.input_label.configure(text=self.master.tr('input_device'))
        self.output_label.configure(text=self.master.tr('output_device'))
        self.bg_label.configure(text=self.master.tr('background'))
        self.bg_button.configure(text=self.master.tr('select_background'))
        self.model_label.configure(text=self.master.tr('model'))
        self.landscape_radio.configure(text=self.master.tr('landscape'))
        self.portrait_radio.configure(text=self.master.tr('portrait'))
        self.resolution_label.configure(text=self.master.tr('resolution'))
        self.fps_label.configure(text=self.master.tr('fps'))
        self.scale_label.configure(text=self.master.tr('scale'))
        self.smooth_frame.configure(text=self.master.tr('smoothing'))
        self.kernel_label.configure(text=self.master.tr('kernel'))
        self.sigma_label.configure(text=self.master.tr('sigma'))

    def update_values(self):
        """Update all widget values from settings"""
        # Update input device
        if self.input_device.get() in self.input_combo['values']:
            self.input_combo.set(self.input_device.get())
        
        # Update output device
        if self.output_device.get() in self.output_combo['values']:
            self.output_combo.set(self.output_device.get())
        
        # Update model selection
        self.model_selection.set(self.model_selection.get())
        
        # Update resolution
        if self.resolution.get() in self.resolution_combo['values']:
            self.resolution_combo.set(self.resolution.get())
        
        # Update FPS
        self.fps_scale.set(self.fps.get())
        self.fps_value_label.configure(text=f"{self.fps.get():.1f}")
        
        # Update scale
        self.scale_scale.set(self.scale.get())
        self.scale_value_label.configure(text=f"{self.scale.get():.1f}")
        
        # Update smoothing
        self.kernel_scale.set(self.smooth_kernel.get())
        self.kernel_value_label.configure(text=str(self.smooth_kernel.get()))
        
        self.sigma_scale.set(self.smooth_sigma.get())
        self.sigma_value_label.configure(text=f"{self.smooth_sigma.get():.1f}")
