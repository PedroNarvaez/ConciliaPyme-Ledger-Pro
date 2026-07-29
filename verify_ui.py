import os
import time
import tkinter as tk
import tkinter.messagebox
from mss import mss

# Mock messagebox to avoid blocking modal popups in headless execution
tkinter.messagebox.showinfo = lambda title, message: print(f"MOCKED INFO: [{title}] {message}")
tkinter.messagebox.showerror = lambda title, message: print(f"MOCKED ERROR: [{title}] {message}")
tkinter.messagebox.showwarning = lambda title, message: print(f"MOCKED WARNING: [{title}] {message}")

from src.database import init_db
from src.ui import ConciliaPymeApp

def run_headless_ui_verification():
    print("Initializing database...")
    init_db()

    print("Setting up Tkinter root...")
    root = tk.Tk()

    # Force a specific window size and position for consistent screenshots
    root.geometry("1100x750+0+0")

    print("Initializing ConciliaPymeApp...")
    app = ConciliaPymeApp(root)
    root.update()

    # Take screenshot of Login screen
    print("Capturing Login screen...")
    with mss() as sct:
        sct.shot(output="/home/jules/verification/screenshots/login.png")

    print("Performing programmatic login...")
    app.ent_user.delete(0, tk.END)
    app.ent_user.insert(0, "admin")
    app.ent_pass.delete(0, tk.END)
    app.ent_pass.insert(0, "Admin@2026!")

    app.handle_login()
    root.update()
    time.sleep(1)

    print("Loading demo files...")
    app.load_demo_files_action()
    root.update()
    time.sleep(1)

    print("Changing visual theme to Dark Mode (Oscuro)...")
    app.save_theme_preference("Oscuro")
    root.update()
    time.sleep(1)

    # Capture main application with loaded demo data and dark mode theme
    print("Capturing main Dashboard with loaded demo data...")
    with mss() as sct:
        sct.shot(output="/home/jules/verification/screenshots/verification.png")

    print("Changing theme back to Claro for Light Mode verification...")
    app.save_theme_preference("Claro")
    root.update()
    time.sleep(1)

    print("Capturing light mode dashboard...")
    with mss() as sct:
        sct.shot(output="/home/jules/verification/screenshots/dashboard_light.png")

    print("Verification completed successfully. Cleaning up...")
    root.destroy()

if __name__ == "__main__":
    run_headless_ui_verification()
