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
    
    # Set simple window title
    root.title("VidMask")
    
    # Set window class using tk command
    try:
        root.tk.call('wm', 'class', '.', "VidMask")
    except tk.TclError:
        print("Could not set window class name")
    
    root.minsize(800, 600)
    
    # Create main window
    from src.gui.main_window import MainWindow
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 