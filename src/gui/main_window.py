import tkinter as tk
from tkinter import ttk, messagebox
from .settings_frame import SettingsFrame
from .preview_frame import PreviewFrame
from ..locales import TRANSLATIONS

class MainWindow(ttk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        
        # Initialize language and theme
        self.language = tk.StringVar(value="en")
        self.theme = tk.StringVar(value="light")  # Default to light theme
        
        # Set initial title
        self.update_title()
        
        # Configure root window
        self.root.minsize(800, 600)
        self.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create menu
        self.create_menu()
        
        # Create frames
        self.create_frames()
        
        # Load camera devices
        self.settings_frame.load_camera_devices()
        
        # Apply initial theme
        self.setup_theme(False)  # Start with light theme
        
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
        self.file_menu.add_command(label=self.tr('reset_settings'), command=self.reset_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self.tr('exit'), command=self.root.quit)
        
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