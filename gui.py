import threading
import organizer
import customtkinter as ctk
from tkinter import filedialog

# -----------------------------
# Variables
# -----------------------------
source_folder = ""
output_folder = ""


# -----------------------------
# Helper Functions
# -----------------------------
def check_ready():
    if source_folder and output_folder:
        start_button.configure(state="normal")
    else:
        start_button.configure(state="disabled")


def select_source_folder():
    global source_folder

    folder = filedialog.askdirectory()

    if folder:
        source_folder = folder
        source_status.configure(text=f"📂 {folder}")
        status.configure(text="Source folder selected.")
        check_ready()


def select_output_folder():
    global output_folder

    folder = filedialog.askdirectory()

    if folder:
        output_folder = folder
        output_status.configure(text=f"📁 {folder}")
        status.configure(text="Output folder selected.")
        check_ready()

def run_organizer(dry_run):
    try:
        if dry_run:
            status.configure(text="🧪 Running Dry Run...")
        else:
            status.configure(text="📂 Organizing Files...")

        organizer.organize(
            source_dirs=[source_folder],
            output_dir=output_folder,
            dry_run=dry_run,
            move=False
        )

        status.configure(text="✅ Finished Successfully!")

    except Exception as e:
        status.configure(text=f"❌ Error: {e}")
# -----------------------------
# Popup Actions
# -----------------------------
def dry_run():
    popup.destroy()

    threading.Thread(
        target=run_organizer,
        args=(True,),
        daemon=True
    ).start()

def organize_files():
    popup.destroy()

    threading.Thread(
        target=run_organizer,
        args=(False,),
        daemon=True
    ).start()

def start_organizing():
    global popup

    popup = ctk.CTkToplevel(app)
    popup.title("Start Organizing")
    popup.geometry("500x420")
    popup.resizable(False, False)

    ctk.CTkLabel(
        popup,
        text="🚀 Start Organizing",
        font=("Segoe UI", 22, "bold")
    ).pack(pady=(20, 10))

    ctk.CTkLabel(
        popup,
        text="Source Folder",
        font=("Segoe UI", 15, "bold")
    ).pack()

    ctk.CTkLabel(
        popup,
        text=source_folder,
        wraplength=450
    ).pack(pady=(0, 15))

    ctk.CTkLabel(
        popup,
        text="Output Folder",
        font=("Segoe UI", 15, "bold")
    ).pack()

    ctk.CTkLabel(
        popup,
        text=output_folder,
        wraplength=450
    ).pack(pady=(0, 20))

    ctk.CTkButton(
        popup,
        text="🧪 Dry Run",
        width=220,
        command=dry_run
    ).pack(pady=8)

    ctk.CTkButton(
        popup,
        text="📂 Organize Files",
        width=220,
        command=organize_files
    ).pack(pady=8)

    ctk.CTkButton(
        popup,
        text="Cancel",
        width=220,
        fg_color="gray40",
        hover_color="gray25",
        command=popup.destroy
    ).pack(pady=20)


# -----------------------------
# App Configuration
# -----------------------------
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# -----------------------------
# Main Window
# -----------------------------
app = ctk.CTk()

app.title("ClearDrive")
app.geometry("900x600")
app.minsize(750, 500)


# -----------------------------
# Title
# -----------------------------
ctk.CTkLabel(
    app,
    text="📁 ClearDrive",
    font=("Segoe UI", 28, "bold")
).pack(pady=(20, 10))

ctk.CTkLabel(
    app,
    text="Organize your files effortlessly",
    font=("Segoe UI", 14)
).pack()


# -----------------------------
# Source Folder
# -----------------------------
ctk.CTkLabel(
    app,
    text="Source Folder",
    font=("Segoe UI", 16, "bold")
).pack(pady=(25, 5))

source_status = ctk.CTkLabel(
    app,
    text="No source folder selected",
    wraplength=700
)
source_status.pack()

ctk.CTkButton(
    app,
    text="Browse Source Folder",
    command=select_source_folder
).pack(pady=10)


# -----------------------------
# Output Folder
# -----------------------------
ctk.CTkLabel(
    app,
    text="Output Folder",
    font=("Segoe UI", 16, "bold")
).pack(pady=(20, 5))

output_status = ctk.CTkLabel(
    app,
    text="No output folder selected",
    wraplength=700
)
output_status.pack()

ctk.CTkButton(
    app,
    text="Browse Output Folder",
    command=select_output_folder
).pack(pady=10)


# -----------------------------
# Start Button
# -----------------------------
start_button = ctk.CTkButton(
    app,
    text="Start Organizing",
    state="disabled",
    command=start_organizing
)
start_button.pack(pady=30)


# -----------------------------
# Progress Bar
# -----------------------------
progress = ctk.CTkProgressBar(app, width=500)
progress.set(0)
progress.pack(pady=20)


# -----------------------------
# Status
# -----------------------------
status = ctk.CTkLabel(
    app,
    text="Waiting for folders..."
)
status.pack()


# -----------------------------
# Run App
# -----------------------------
app.mainloop()