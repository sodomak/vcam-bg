import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import re
import os

class SettingsFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="Settings", padding=10)
        
        # Create variables
        self.input_device = tk.StringVar()
        self.output_device = tk.StringVar(value='/dev/video2')
        self.background_path = tk.StringVar()
        self.model_selection = tk.IntVar(value=1)
        self.fps = tk.DoubleVar(value=20.0)
        self.scale = tk.DoubleVar(value=1.0)
        self.resolution = tk.StringVar(value='1280x720')
        self.smooth_kernel = tk.IntVar(value=21)
        self.smooth_sigma = tk.DoubleVar(value=10.0)
        
        # Store controls that need to be disabled when camera is running
        self.runtime_controls = []
        
        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Input Device
        ttk.Label(self, text="Input Device:").pack(anchor=tk.W)
        self.input_combo = ttk.Combobox(
            self, 
            textvariable=self.input_device,
            state="readonly"
        )
        self.input_combo.pack(fill=tk.X, pady=(0, 10))
        self.runtime_controls.append(self.input_combo)
        
        # Output Device
        ttk.Label(self, text="Output Device:").pack(anchor=tk.W)
        self.output_combo = ttk.Combobox(
            self,
            textvariable=self.output_device,
            state="readonly"
        )
        self.output_combo.pack(fill=tk.X, pady=(0, 10))
        self.runtime_controls.append(self.output_combo)
        
        # Background
        ttk.Label(self, text="Background:").pack(anchor=tk.W)
        bg_frame = ttk.Frame(self)
        bg_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.bg_button = ttk.Button(
            bg_frame,
            text="Select Background",
            command=self.select_background
        )
        self.bg_button.pack(side=tk.LEFT)
        self.runtime_controls.append(self.bg_button)
        
        self.bg_label = ttk.Label(bg_frame, textvariable=self.background_path)
        self.bg_label.pack(side=tk.LEFT, padx=5)
        
        # Model
        ttk.Label(self, text="Model:").pack(anchor=tk.W)
        model_frame = ttk.Frame(self)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        landscape_radio = ttk.Radiobutton(
            model_frame,
            text="Landscape",
            variable=self.model_selection,
            value=0
        )
        landscape_radio.pack(side=tk.LEFT)
        self.runtime_controls.append(landscape_radio)
        
        portrait_radio = ttk.Radiobutton(
            model_frame,
            text="Portrait",
            variable=self.model_selection,
            value=1
        )
        portrait_radio.pack(side=tk.LEFT)
        self.runtime_controls.append(portrait_radio)
        
        # Resolution
        ttk.Label(self, text="Resolution:").pack(anchor=tk.W)
        self.resolution_combo = ttk.Combobox(
            self,
            textvariable=self.resolution,
            values=['640x480', '1280x720', '1920x1080'],
            state="readonly"
        )
        self.resolution_combo.pack(fill=tk.X, pady=(0, 10))
        self.runtime_controls.append(self.resolution_combo)

        # Create sliders
        self.create_sliders()

    def create_sliders(self):
        # FPS control
        fps_frame = ttk.Frame(self)
        fps_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT)
        self.fps_label = ttk.Label(fps_frame, text="20.0")
        self.fps_label.pack(side=tk.RIGHT)
        
        self.fps_scale = ttk.Scale(
            self,
            from_=1,
            to=60,
            variable=self.fps,
            orient=tk.HORIZONTAL,
            command=lambda v: self.fps_label.configure(text=f"{float(v):.1f}")
        )
        self.fps_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Scale control
        scale_frame = ttk.Frame(self)
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(scale_frame, text="Scale:").pack(side=tk.LEFT)
        self.scale_label = ttk.Label(scale_frame, text="1.0")
        self.scale_label.pack(side=tk.RIGHT)
        
        self.scale_scale = ttk.Scale(
            self,
            from_=0.1,
            to=2.0,
            variable=self.scale,
            orient=tk.HORIZONTAL,
            command=lambda v: self.scale_label.configure(text=f"{float(v):.1f}")
        )
        self.scale_scale.pack(fill=tk.X, pady=(0, 10))
        
        # Smoothing settings
        smooth_frame = ttk.LabelFrame(self, text="Smoothing", padding=5)
        smooth_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Kernel control
        kernel_frame = ttk.Frame(smooth_frame)
        kernel_frame.pack(fill=tk.X)
        ttk.Label(kernel_frame, text="Kernel:").pack(side=tk.LEFT)
        self.kernel_label = ttk.Label(kernel_frame, text="21")
        self.kernel_label.pack(side=tk.RIGHT)
        
        self.kernel_scale = ttk.Scale(
            smooth_frame,
            from_=3,
            to=51,
            variable=self.smooth_kernel,
            orient=tk.HORIZONTAL,
            command=self.update_kernel_value
        )
        self.kernel_scale.pack(fill=tk.X)
        
        # Sigma control
        sigma_frame = ttk.Frame(smooth_frame)
        sigma_frame.pack(fill=tk.X)
        ttk.Label(sigma_frame, text="Sigma:").pack(side=tk.LEFT)
        self.sigma_label = ttk.Label(sigma_frame, text="10.0")
        self.sigma_label.pack(side=tk.RIGHT)
        
        self.sigma_scale = ttk.Scale(
            smooth_frame,
            from_=0.1,
            to=20.0,
            variable=self.smooth_sigma,
            orient=tk.HORIZONTAL,
            command=lambda v: self.sigma_label.configure(text=f"{float(v):.1f}")
        )
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
        """Get list of available camera devices"""
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
            
            # Set first available device if none selected
            if not self.input_device.get() and input_devices:
                self.input_device.set(input_devices[0])
            if not self.output_device.get() and output_devices:
                self.output_device.set(output_devices[0])
                
            # Update resolutions for selected input device
            self.update_resolutions()
                
        except subprocess.CalledProcessError:
            print("Error: Could not retrieve camera list")

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
        
        # Labels for devices
        self.input_label.configure(text=self.master.tr('input_device'))
        self.output_label.configure(text=self.master.tr('output_device'))
        
        # Background section
        self.bg_label.configure(text=self.master.tr('background'))
        self.bg_button.configure(text=self.master.tr('select_background'))
        
        # Model section
        self.model_label.configure(text=self.master.tr('model'))
        self.landscape_radio.configure(text=self.master.tr('landscape'))
        self.portrait_radio.configure(text=self.master.tr('portrait'))
        
        # Resolution section
        self.resolution_label.configure(text=self.master.tr('resolution'))
        
        # FPS section
        self.fps_frame_label.configure(text=self.master.tr('fps'))
        
        # Scale section
        self.scale_frame_label.configure(text=self.master.tr('scale'))
        
        # Smoothing section
        self.smooth_frame.configure(text=self.master.tr('smoothing'))
        self.kernel_frame_label.configure(text=self.master.tr('kernel'))
        self.sigma_frame_label.configure(text=self.master.tr('sigma'))
