import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .settings_frame import SettingsFrame
from .preview_frame import PreviewFrame
from ..locales import TRANSLATIONS
import os
import json
import mediapipe as mp
import re
import cv2
import subprocess
import queue
import numpy as np
from src.version import VERSION

class MainWindow(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.config_file = os.path.expanduser("~/.config/vcam-bg/config.json")
        
        # Create default settings
        self.default_settings = {
            'input_device': '',
            'output_device': '/dev/video2',
            'background_path': '',
            'fps': 20.0,
            'scale': 1.0,
            'show_preview': True,
            'smooth_kernel': 21,
            'smooth_sigma': 10.0,
            'resolution': '1280x720',
            'language': 'en',
            'theme': 'light'
        }
        
        # Initialize variables with default values first
        self.fps = tk.DoubleVar(value=self.default_settings['fps'])
        self.scale = tk.DoubleVar(value=self.default_settings['scale'])
        self.smooth_kernel = tk.IntVar(value=self.default_settings['smooth_kernel'])
        self.smooth_sigma = tk.DoubleVar(value=self.default_settings['smooth_sigma'])
        self.input_device = tk.StringVar(value=self.default_settings['input_device'])
        self.output_device = tk.StringVar(value=self.default_settings['output_device'])
        self.background_path = tk.StringVar(value=self.default_settings['background_path'])
        self.show_preview = tk.BooleanVar(value=self.default_settings['show_preview'])
        self.resolution = tk.StringVar(value=self.default_settings['resolution'])
        self.language = tk.StringVar(value=self.default_settings['language'])
        self.theme = tk.StringVar(value=self.default_settings['theme'])
        
        # Load settings after initializing variables
        self.load_settings()
        
        # Create GUI
        self.create_menu()
        self.create_frames()
        
        # Bind settings changes to save
        self.settings_frame.input_device.trace_add('write', lambda *_: self.save_settings())
        self.settings_frame.output_device.trace_add('write', lambda *_: self.save_settings())
        self.settings_frame.background_path.trace_add('write', lambda *_: self.save_settings())
        self.settings_frame.fps.trace_add('write', lambda *_: self.save_settings())
        self.settings_frame.scale.trace_add('write', lambda *_: self.save_settings())
        self.settings_frame.smooth_kernel.trace_add('write', lambda *_: self.save_settings())
        self.settings_frame.smooth_sigma.trace_add('write', lambda *_: self.save_settings())
        self.settings_frame.resolution.trace_add('write', lambda *_: self.save_settings())
        self.preview_frame.show_preview.trace_add('write', lambda *_: self.save_settings())
        self.language.trace_add('write', lambda *_: self.save_settings())
        self.theme.trace_add('write', lambda *_: self.save_settings())
        
        # Apply loaded settings
        self.apply_loaded_settings()
        
        # Set initial title
        self.update_title()
        
        # Configure root window
        self.root.minsize(800, 600)
        self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Load camera devices
        self.settings_frame.load_camera_devices()
        
        # Add keyboard shortcuts
        self.root.bind('<Control-s>', lambda e: self.save_settings())
        self.root.bind('<Control-i>', lambda e: self.import_settings())
        self.root.bind('<Control-e>', lambda e: self.export_settings())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<space>', lambda e: self.preview_frame.toggle_camera())
        self.root.bind('<r>', lambda e: self.reset_settings())
        self.root.bind('<Escape>', lambda e: self.preview_frame.stop_camera())
        
        print("GUI created")

    def create_frames(self):
        """Create main application frames"""
        # Settings frame (left side)
        self.settings_frame = SettingsFrame(self)
        self.settings_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Preview frame (right side)
        self.preview_frame = PreviewFrame(self)
        self.preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        self.file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr('file'), menu=self.file_menu)
        self.file_menu.add_command(label=self.tr('import_settings'), command=self.import_settings, accelerator='Ctrl+I')
        self.file_menu.add_command(label=self.tr('export_settings'), command=self.export_settings, accelerator='Ctrl+E')
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self.tr('save_settings'), command=self.save_settings, accelerator='Ctrl+S')
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self.tr('reset_settings'), command=self.reset_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self.tr('exit'), command=self.root.quit, accelerator='Ctrl+Q')
        
        # View menu
        self.view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr('view'), menu=self.view_menu)
        
        # Language submenu
        self.language_menu = tk.Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label=self.tr('language'), menu=self.language_menu)
        
        # Add language options
        self.language_menu.add_radiobutton(
            label="English",
            value="en",
            variable=self.language,
            command=self.change_language
        )
        self.language_menu.add_radiobutton(
            label="Čeština",
            value="cs",
            variable=self.language,
            command=self.change_language
        )
        
        # Theme submenu
        self.theme_menu = tk.Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label=self.tr('theme'), menu=self.theme_menu)
        
        # Add theme options
        self.theme_menu.add_radiobutton(
            label=self.tr('light'),
            value="light",
            variable=self.theme,
            command=lambda: self.setup_theme(False)
        )
        self.theme_menu.add_radiobutton(
            label=self.tr('dark'),
            value="dark",
            variable=self.theme,
            command=lambda: self.setup_theme(True)
        )
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self.tr('help'), menu=help_menu)
        help_menu.add_command(label=self.tr('about'), command=self.show_about)

    def tr(self, key):
        """Get translated string"""
        return TRANSLATIONS[self.language.get()].get(key, key)

    def update_title(self):
        """Update window title"""
        self.root.title(self.tr('title'))

    def change_language(self):
        """Change application language"""
        # Update window title
        self.update_title()
        
        # Update menu labels
        self.create_menu()
        
        # Update frame labels
        self.settings_frame.update_labels()
        self.preview_frame.update_labels()

    def reset_settings(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to default?"):
            # Stop camera if running
            if self.preview_frame.is_running:
                self.preview_frame.toggle_camera()
            
            # Reset settings to defaults
            self.settings_frame.reset_to_defaults()
            messagebox.showinfo("Settings Reset", "All settings have been reset to default values")

    def show_about(self):
        """Show about dialog"""
        text = self.tr('about_text').format(version=VERSION)
        messagebox.showinfo(self.tr('about_title'), text)

    def setup_theme(self, is_dark=False):
        """Setup light/dark theme using ttk styles"""
        style = ttk.Style()
        
        if is_dark:
            # Dark theme colors
            style.theme_use('default')
            self.root.configure(bg='#2d2d2d')
            style.configure('.', background='#2d2d2d', foreground='#ffffff')
            style.configure('TLabel', background='#2d2d2d', foreground='#ffffff')
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabelframe', background='#2d2d2d', foreground='#ffffff')
            style.configure('TLabelframe.Label', background='#2d2d2d', foreground='#ffffff')
            style.configure('TButton', background='#3d3d3d', foreground='#ffffff')
            style.configure('TCheckbutton', background='#2d2d2d', foreground='#ffffff')
            style.configure('TRadiobutton', background='#2d2d2d', foreground='#ffffff')
            style.configure('TScale', background='#2d2d2d', troughcolor='#3d3d3d')
            style.configure('TCombobox',
                fieldbackground='#3d3d3d',
                background='#3d3d3d',
                foreground='#ffffff',
                selectbackground='#0078d7',
                selectforeground='#ffffff'
            )
            
            # Menu colors
            menubar = self.root.winfo_children()[0]
            if isinstance(menubar, tk.Menu):
                menubar.configure(
                    bg='#2d2d2d',
                    fg='#ffffff',
                    activebackground='#0078d7',
                    activeforeground='#ffffff'
                )
                for menu in [self.file_menu, self.view_menu, self.help_menu]:
                    if menu:
                        menu.configure(
                            bg='#2d2d2d',
                            fg='#ffffff',
                            activebackground='#0078d7',
                            activeforeground='#ffffff'
                        )
        else:
            # Light theme colors (from original script)
            style.theme_use('default')
            self.root.configure(bg='#f0f0f0')
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
                for menu in [self.file_menu, self.view_menu, self.help_menu]:
                    if menu:
                        menu.configure(
                            bg='#f0f0f0',
                            fg='#000000',
                            activebackground='#0078d7',
                            activeforeground='#ffffff'
                        )
        
        # Force redraw
        self.root.update_idletasks()

    def load_settings(self):
        """Load settings from config file or use defaults"""
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

    def save_settings(self):
        """Save current settings to config file"""
        try:
            settings = {
                'input_device': self.input_device.get(),
                'output_device': self.output_device.get(),
                'background_path': self.background_path.get(),
                'fps': self.fps.get(),
                'scale': self.scale.get(),
                'show_preview': self.show_preview.get(),
                'smooth_kernel': self.smooth_kernel.get(),
                'smooth_sigma': self.smooth_sigma.get(),
                'resolution': self.resolution.get(),
                'language': self.language.get(),
                'theme': self.theme.get()
            }
            
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=4)
                
        except Exception as e:
            print(f"Error saving settings: {e}")

    def export_settings(self):
        """Export settings to a user-specified file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                settings = {
                    'input_device': self.settings_frame.input_device.get(),
                    'output_device': self.settings_frame.output_device.get(),
                    'background_path': self.settings_frame.background_path.get(),
                    'fps': self.settings_frame.fps.get(),
                    'scale': self.settings_frame.scale.get(),
                    'show_preview': self.preview_frame.show_preview.get(),
                    'smooth_kernel': self.settings_frame.smooth_kernel.get(),
                    'smooth_sigma': self.settings_frame.smooth_sigma.get(),
                    'resolution': self.settings_frame.resolution.get(),
                    'language': self.language.get(),
                    'theme': self.theme.get()
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
                self.settings_frame.input_device.set(settings.get('input_device', ''))
                self.settings_frame.output_device.set(settings.get('output_device', '/dev/video2'))
                self.settings_frame.background_path.set(settings.get('background_path', ''))
                self.settings_frame.fps.set(settings.get('fps', 20.0))
                self.settings_frame.scale.set(settings.get('scale', 1.0))
                self.preview_frame.show_preview.set(settings.get('show_preview', True))
                self.settings_frame.smooth_kernel.set(settings.get('smooth_kernel', 21))
                self.settings_frame.smooth_sigma.set(settings.get('smooth_sigma', 10.0))
                self.settings_frame.resolution.set(settings.get('resolution', '1280x720'))
                self.language.set(settings.get('language', 'en'))
                self.theme.set(settings.get('theme', 'light'))
                
                # Apply imported settings
                self.apply_loaded_settings()
                messagebox.showinfo("Success", "Settings imported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import settings: {e}")

    def apply_loaded_settings(self):
        """Apply loaded settings to GUI elements"""
        # Update language
        self.change_language()
        
        # Update theme
        self.setup_theme('dark' in self.theme.get().lower())
        
        # Update frames
        self.settings_frame.update_values()
        self.preview_frame.update_values()

    def process_camera(self):
        # Initialize MediaPipe with fixed landscape model
        mp_selfie_segmentation = mp.solutions.selfie_segmentation
        selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)

        try:
            # Extract device number from path
            input_device = re.search(r"\((/dev/video\d+)\)", self.input_device.get()).group(1)
            output_device = re.search(r"\((/dev/video\d+)\)", self.output_device.get()).group(1)
            device_num = int(input_device.replace('/dev/video', ''))

            # Open camera
            cap = cv2.VideoCapture(device_num, cv2.CAP_V4L2)
            if not cap.isOpened():
                messagebox.showerror("Error", f"Could not open camera {input_device}")
                self.is_running = False
                return

            # Set initial resolution
            width, height = map(int, self.resolution_combo.get().split('x'))
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Get actual camera resolution
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if actual_width != width or actual_height != height:
                print(f"Warning: Camera using {actual_width}x{actual_height} instead of requested {width}x{height}")
                width, height = actual_width, actual_height

            # Load and resize background
            background_image = cv2.imread(self.background_path.get())
            if background_image is None:
                messagebox.showerror("Error", "Could not load background image")
                self.is_running = False
                return
            background_image = cv2.resize(background_image, (width, height))

            # Initialize FFmpeg process
            command = [
                'ffmpeg',
                '-f', 'rawvideo',
                '-pix_fmt', 'bgr24',
                '-s', f'{width}x{height}',
                '-r', str(self.fps.get()),
                '-i', '-',
                '-f', 'v4l2',
                output_device
            ]
            ffmpeg_process = subprocess.Popen(command, stdin=subprocess.PIPE)
            
            last_scale = self.scale.get()
            self.frame_queue = queue.Queue(maxsize=2)

            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break

                # Ensure frame matches target dimensions
                frame = cv2.resize(frame, (width, height))
                
                # Check if scale changed
                if last_scale != self.scale.get():
                    scaled_width = int(width * self.scale.get())
                    scaled_height = int(height * self.scale.get())
                    background_image = cv2.resize(background_image, (scaled_width, scaled_height))
                    last_scale = self.scale.get()
                    frame = cv2.resize(frame, (scaled_width, scaled_height))
                    width, height = scaled_width, scaled_height

                # Process frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = selfie_segmentation.process(frame_rgb)

                try:
                    # Create and smooth mask
                    kernel_size = int(self.smooth_kernel.get())
                    if kernel_size % 2 == 0:
                        kernel_size += 1
                    kernel_tuple = (kernel_size, kernel_size)
                    
                    mask = results.segmentation_mask
                    mask = cv2.GaussianBlur(
                        mask,
                        kernel_tuple,
                        sigmaX=float(self.smooth_sigma.get()),
                        sigmaY=float(self.smooth_sigma.get())
                    )
                    mask = np.stack((mask,) * 3, axis=-1)

                    # Combine foreground and background
                    output_frame = (frame * mask + background_image * (1 - mask)).astype(np.uint8)

                    # Update preview if enabled
                    if self.show_preview.get():
                        try:
                            self.frame_queue.put_nowait(output_frame)
                        except queue.Full:
                            pass

                    # Write to FFmpeg
                    ffmpeg_process.stdin.write(output_frame.tobytes())

                except Exception as e:
                    print(f"Error processing frame: {e}")
                    continue

            # Cleanup
            cap.release()
            ffmpeg_process.stdin.close()
            ffmpeg_process.wait()
            selfie_segmentation.close()

        except Exception as e:
            messagebox.showerror("Error", f"Camera error: {str(e)}")
            self.is_running = False
            return