import customtkinter as ctk
from tkinter import filedialog

# -----------------------------
# Variables
# -----------------------------
source_folder = ""
output_folder = ""


# -----------------------------
# Helper Function
# -----------------------------
def check_ready():
    if source_folder and output_folder:
        start_button.configure(state="normal")
    else:
        start_button.configure(state="disabled")


# -----------------------------
# Select Source Folder
# -----------------------------
def select_source_folder():
    global source_folder

    folder = filedialog.askdirectory()

    if folder:
        source_folder = folder

        source_status.configure(
            text=f"📂 {folder}"
        )

        status.configure(
            text="Source folder selected."
        )

        check_ready()


# -----------------------------
# Select Output Folder
# -----------------------------
def select_output_folder():
    global output_folder

    folder = filedialog.askdirectory()

    if folder:
        output_folder = folder

        output_status.configure(
            text=f"📁 {folder}"
        )

        status.configure(
            text="Output folder selected."
        )

        check_ready()


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
title = ctk.CTkLabel(
    app,
    text="📁 ClearDrive",
    font=("Segoe UI", 28, "bold")
)
title.pack(pady=(20, 10))

subtitle = ctk.CTkLabel(
    app,
    text="Organize your files effortlessly",
    font=("Segoe UI", 14)
)
subtitle.pack()


# -----------------------------
# Source Folder
# -----------------------------
source_label = ctk.CTkLabel(
    app,
    text="Source Folder",
    font=("Segoe UI", 16, "bold")
)
source_label.pack(pady=(25, 5))

source_status = ctk.CTkLabel(
    app,
    text="No source folder selected",
    wraplength=700
)
source_status.pack()

source_button = ctk.CTkButton(
    app,
    text="Browse Source Folder",
    command=select_source_folder
)
source_button.pack(pady=10)


# -----------------------------
# Output Folder
# -----------------------------
output_label = ctk.CTkLabel(
    app,
    text="Output Folder",
    font=("Segoe UI", 16, "bold")
)
output_label.pack(pady=(20, 5))

output_status = ctk.CTkLabel(
    app,
    text="No output folder selected",
    wraplength=700
)
output_status.pack()

output_button = ctk.CTkButton(
    app,
    text="Browse Output Folder",
    command=select_output_folder
)
output_button.pack(pady=10)


# -----------------------------
# Start Button
# -----------------------------
start_button = ctk.CTkButton(
    app,
    text="Start Organizing",
    state="disabled"
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