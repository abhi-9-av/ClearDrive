import customtkinter as ctk
from tkinter import filedialog


# -----------------------------
# Function to Select Folder
# -----------------------------
def select_folder():
    folder = filedialog.askdirectory()

    if folder:
        status.configure(
            text=f"📂 Selected Folder:\n{folder}"
        )

        # Enable the Start button
        start_button.configure(state="normal")

        print(folder)


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
app.geometry("900x550")
app.minsize(700, 450)


# -----------------------------
# Title
# -----------------------------
title = ctk.CTkLabel(
    app,
    text="📁 ClearDrive",
    font=("Segoe UI", 28, "bold")
)
title.pack(pady=(25, 10))


subtitle = ctk.CTkLabel(
    app,
    text="Organize your files effortlessly",
    font=("Segoe UI", 14)
)
subtitle.pack()


# -----------------------------
# Buttons
# -----------------------------
select_button = ctk.CTkButton(
    app,
    text="Select Folder",
    width=200,
    height=40,
    command=select_folder
)
select_button.pack(pady=30)


start_button = ctk.CTkButton(
    app,
    text="Start Organizing",
    width=200,
    height=40,
    state="disabled"          # Disabled initially
)
start_button.pack()


# -----------------------------
# Progress Bar
# -----------------------------
progress = ctk.CTkProgressBar(app, width=500)
progress.set(0)
progress.pack(pady=40)


# -----------------------------
# Status Label
# -----------------------------
status = ctk.CTkLabel(
    app,
    text="Waiting for folder...",
    font=("Segoe UI", 13)
)
status.pack()


# -----------------------------
# Run App
# -----------------------------
app.mainloop()