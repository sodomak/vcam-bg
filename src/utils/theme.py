import tkinter as tk
from tkinter import ttk
import subprocess
from typing import Optional, Literal
import os

ThemeType = Literal["light", "dark", "system", "gtk"]

class ThemeManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_theme: ThemeType = "system"
        
        # Get available themes and choose the most appropriate default
        self.available_themes = ttk.Style().theme_names()
        self.base_theme = self._get_base_theme()
        
        # Set theme before any widgets are created
        self._setup_initial_theme()
        
        # Monitor system theme changes (if possible)
        self.start_theme_monitor()

    def _get_base_theme(self) -> str:
        """Choose the most appropriate base theme"""
        # Priority order for themes
        preferred_themes = ['clam', 'alt', 'default']
        for theme in preferred_themes:
            if theme in self.available_themes:
                return theme
        # If none of preferred themes found, use the first available
        return self.available_themes[0]

    def _setup_initial_theme(self):
        """Setup initial theme before widget creation"""
        style = ttk.Style()
        style.theme_use(self.base_theme)
        
        # Ensure these options are set before any widgets are created
        self.root.option_add('*tearOff', False)  # Disable tear-off menus
        
        # Initialize with system theme
        self.set_theme("system")

    def set_theme(self, theme: ThemeType):
        """Set application theme"""
        self.current_theme = theme
        
        if theme == "system":
            is_dark = self.detect_system_theme()
        elif theme == "gtk":
            # Use GTK theme explicitly
            try:
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                    capture_output=True,
                    text=True
                )
                is_dark = 'dark' in result.stdout.lower()
            except Exception:
                is_dark = False
        else:
            is_dark = theme == "dark"
            
        self.apply_theme(is_dark)

    def detect_system_theme(self) -> bool:
        """Detect system theme (dark/light)"""
        # Try GTK theme first
        try:
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                capture_output=True,
                text=True
            )
            if 'dark' in result.stdout.lower():
                return True
            elif result.stdout.strip():  # If we got a valid response, trust it
                return False
        except Exception:
            pass
        
        # Fallback to GNOME color-scheme
        try:
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
                capture_output=True,
                text=True
            )
            if 'dark' in result.stdout.lower():
                return True
        except Exception:
            pass
        
        # Try Qt settings as last resort
        try:
            if os.path.exists(os.path.expanduser('~/.config/qt5ct/qt5ct.conf')):
                with open(os.path.expanduser('~/.config/qt5ct/qt5ct.conf')) as f:
                    if 'dark' in f.read().lower():
                        return True
        except Exception:
            pass
        
        # Default to light theme
        return False

    def apply_theme(self, is_dark: bool):
        """Apply theme colors"""
        style = ttk.Style()
        
        # Base colors
        bg_color = '#2e2e2e' if is_dark else '#f0f0f0'
        fg_color = '#ffffff' if is_dark else '#000000'
        select_bg = '#404040' if is_dark else '#0078d7'
        select_fg = '#ffffff'
        
        # Configure root window
        self.root.configure(bg=bg_color)
        
        # Configure ttk styles
        style.configure('.',
            background=bg_color,
            foreground=fg_color,
            troughcolor=select_bg if is_dark else '#e0e0e0',
            selectbackground=select_bg,
            selectforeground=select_fg
        )
        
        # Configure specific widget styles
        style.configure('TCombobox',
            fieldbackground=bg_color,
            background=bg_color,
            foreground=fg_color,
            arrowcolor=fg_color,
            selectbackground=select_bg,
            selectforeground=select_fg
        )
        
        # Map states for hover/focus effects
        style.map('TCombobox',
            fieldbackground=[('readonly', bg_color)],
            selectbackground=[('readonly', select_bg)],
            selectforeground=[('readonly', select_fg)]
        )
        
        # Configure menu colors globally
        menu_options = {
            '*Menu.background': bg_color,
            '*Menu.foreground': fg_color,
            '*Menu.activeBackground': select_bg,
            '*Menu.activeForeground': select_fg,
            '*Menu.selectColor': fg_color,
            '*Menu.relief': 'flat',
            '*Menu.borderWidth': 0,
            '*Menu.activeBorderWidth': 0,
            '*Listbox.background': bg_color,
            '*Listbox.foreground': fg_color,
            '*Listbox.selectBackground': select_bg,
            '*Listbox.selectForeground': select_fg
        }
        
        # Apply options with high priority
        for option, value in menu_options.items():
            self.root.option_add(option, value, 'interactive')
        
        # Update existing menus
        def configure_menu(menu):
            menu.configure(
                bg=bg_color,
                fg=fg_color,
                activebackground=select_bg,
                activeforeground=select_fg,
                selectcolor=fg_color,
                relief='flat',
                borderwidth=0
            )
            for i in range(menu.index('end') + 1 if menu.index('end') is not None else 0):
                try:
                    if menu.type(i) == 'cascade':
                        submenu = menu.nametowidget(menu.entrycget(i, 'menu'))
                        configure_menu(submenu)
                except:
                    continue
        
        # Force update all existing menus
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Menu):
                configure_menu(widget)
        
        # Configure tk widgets (non-ttk)
        self.configure_tk_widgets(
            bg=bg_color,
            fg=fg_color,
            activebackground=select_bg,
            activeforeground=select_fg,
            selectbackground=select_bg,
            selectforeground=select_fg
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