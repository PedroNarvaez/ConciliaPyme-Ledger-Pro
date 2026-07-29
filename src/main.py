import os
import sys

# Add repository root directory to sys.path dynamically
# This allows launching the application from anywhere using 'python src/main.py' or 'python3 src/main.py'
# without requiring PYTHONPATH=.
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import tkinter as tk
from src.database import init_db
from src.ui import ConciliaPymeApp

def main():
    # Initialize SQLite database
    init_db()

    # Initialize Tkinter Window
    root = tk.Tk()

    # Launch Application
    app = ConciliaPymeApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()
