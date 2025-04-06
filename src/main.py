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
    root.wm_classname("VidMask")
    
    # Create main window
    from src.gui.main_window import MainWindow
    app = MainWindow(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    # Set minimum window size
    root.minsize(800, 600)
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main() 