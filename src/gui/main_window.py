import tkinter as tk
from tkinter import ttk, messagebox
from .settings_frame import SettingsFrame
from .preview_frame import PreviewFrame

class MainWindow(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("Virtual Camera Background")
        
        # Configure root window
        self.root.minsize(800, 600)
        self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create menu
        self.create_menu()
        
        # Create frames
        self.create_frames()
        
        # Load camera devices
        self.settings_frame.load_camera_devices()
        
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
        menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Reset Settings", command=self.reset_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        self.view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=self.view_menu)
        
        # Language submenu
        self.language_menu = tk.Menu(self.view_menu, tearoff=0)
        self.view_menu.add_cascade(label="Language", menu=self.language_menu)
        
        # Add language options
        self.language = tk.StringVar(value="en")
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
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def change_language(self):
        """Change application language"""
        # TODO: Implement language change
        pass

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
        text = """Virtual Camera Background

A simple application for replacing webcam background using AI segmentation.

Features:
- Background replacement
- Virtual camera output
- Multiple resolutions support
- Adjustable smoothing
- Configuration saving

License: MIT
Author: sodomak
Repository: https://github.com/sodomak/vcam-bg

Built with:
- Python 3
- OpenCV
- MediaPipe
- Tkinter"""

        messagebox.showinfo("About Virtual Camera Background", text)