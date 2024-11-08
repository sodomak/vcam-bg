import tkinter as tk
from tkinter import ttk
import subprocess
from typing import Optional, Literal

ThemeType = Literal["light", "dark", "system"]

class ThemeManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_theme: ThemeType = "system"
        
        # Initialize theme
        self.set_theme("system")
        
        # Monitor system theme changes (if possible)
        self.start_theme_monitor()

    def set_theme(self, theme: ThemeType):
        """Set application theme"""
        self.current_theme = theme
        
        if theme == "system":
            is_dark = self.detect_system_theme()
        else:
            is_dark = theme == "dark"
            
        self.apply_theme(is_dark)

    def detect_system_theme(self) -> bool:
        """Detect system theme (dark/light)"""
        try:
            # Try GNOME
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                capture_output=True,
                text=True
            )
            return 'dark' in result.stdout.lower()
        except Exception:
            try:
                # Try GTK
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                    capture_output=True,
                    text=True
                )
                return 'dark' in result.stdout.lower()
            except Exception:
                # Default to light theme
                return False

    def apply_theme(self, is_dark: bool):
        """Apply theme colors"""
        style = ttk.Style()
        
        if is_dark:
            # Dark theme colors
            style.theme_use('clam')
            
            # Configure root window
            self.root.configure(bg='#2e2e2e')
            
            # Configure ttk styles
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
            
            # Configure tk widgets
            self.configure_tk_widgets(
                bg='#2e2e2e',
                fg='#ffffff',
                activebackground='#404040',
                activeforeground='#ffffff',
                selectbackground='#606060',
                selectforeground='#ffffff'
            )
            
        else:
            # Light theme colors
            style.theme_use('default')
            
            # Configure root window
            self.root.configure(bg='#f0f0f0')
            
            # Configure ttk styles
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
            
            # Configure tk widgets
            self.configure_tk_widgets(
                bg='#f0f0f0',
                fg='#000000',
                activebackground='#0078d7',
                activeforeground='#ffffff',
                selectbackground='#0078d7',
                selectforeground='#ffffff'
            )
        
        # Force redraw
        self.root.update_idletasks()

    def configure_tk_widgets(self, **kwargs):
        """Configure all tk widgets with given options"""
        def configure_widget(widget):
            try:
                # Skip ttk widgets
                if not isinstance(widget, (ttk.Widget, ttk.Frame, ttk.LabelFrame)):
                    widget_class = widget.winfo_class()
                    if widget_class in ('Menu', 'Menubutton'):
                        # Configure menu-specific options
                        menu_opts = {
                            'bg': kwargs['bg'],
                            'fg': kwargs['fg'],
                            'activebackground': kwargs['activebackground'],
                            'activeforeground': kwargs['activeforeground']
                        }
                        widget.configure(**menu_opts)
                    else:
                        # Configure standard widget options
                        widget.configure(**kwargs)
            except tk.TclError:
                pass  # Skip widgets that don't support these options
            
            # Recursively configure children
            for child in widget.winfo_children():
                configure_widget(child)
        
        configure_widget(self.root)

    def start_theme_monitor(self):
        """Start monitoring system theme changes"""
        if self.current_theme == "system":
            # Check every 5 seconds for theme changes
            self.check_system_theme()
    
    def check_system_theme(self):
        """Check for system theme changes"""
        if self.current_theme == "system":
            is_dark = self.detect_system_theme()
            self.apply_theme(is_dark)
            # Schedule next check
            self.root.after(5000, self.check_system_theme)