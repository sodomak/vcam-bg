#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting application...")

def main():
    root = tk.Tk()
    
    # Set window title and class to match desktop entry
    root.title("VidMask")
    root.wm_class("VidMask", "VidMask")  # This should now match StartupWMClass
    
    # Try to set window properties for Wayland
    try:
        root.tk.call('tk', 'windowingsystem')
        root.tk.call('wm', 'attributes', '.', '-type', 'normal')
        # Only set the class name, not affecting the title
        root.tk.call('wm', 'attributes', '.', '-class', 'io.github.sodomak.vidmask')
    except tk.TclError:
        print("Could not set Wayland window properties")
    
    root.minsize(800, 600)
    
    # Create main window
    from src.gui.main_window import MainWindow
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 