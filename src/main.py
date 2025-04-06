#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Starting application...")

def main():
    # Set the class name before creating the window
    tk.Tk.wm_class("VidMask", "VidMask")
    
    root = tk.Tk()
    
    # Set both the window title and class name
    root.title("VidMask")
    
    # Remove any previous wm_class calls as they're not needed
    # The title() method handles both the window title and taskbar name
    
    root.minsize(800, 600)
    
    # Create main window
    from src.gui.main_window import MainWindow
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 