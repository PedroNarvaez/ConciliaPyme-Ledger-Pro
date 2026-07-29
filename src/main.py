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
