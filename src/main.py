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
    root.title("VidMask")
    
    # Set window class name for X11
    try:
        root.tk.call('wm', 'withdraw', '.')
        root.tk.call('wm', 'client', '.', 'io.github.sodomak.vidmask')
        root.tk.call('wm', 'deiconify', '.')
    except tk.TclError:
        print("Could not set X11 window class name")
    
    # Set window class name for Wayland
    try:
        root.tk.call('tk', 'windowingsystem')
        root.tk.call('wm', 'attributes', '.', '-type', 'normal')
        root.tk.call('wm', 'attributes', '.', '-name', 'io.github.sodomak.vidmask')
    except tk.TclError:
        print("Could not set Wayland window properties")
    
    root.minsize(800, 600)
    
    # Create main window
    from src.gui.main_window import MainWindow
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 