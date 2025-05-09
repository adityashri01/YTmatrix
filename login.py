from customtkinter import *
from tkinter import messagebox
import json
import hashlib
import os
import sys
from PIL import Image

set_appearance_mode("light")
set_default_color_theme("blue")

root = CTk()
root.title("Login")
root.geometry("700x500")
root.resizable(0, 0)

# Background image
bg_image = CTkImage(light_image=Image.open("WhatsApp Image 2025-05-02 at 19.36.10_435a3730.jpg"), size=(700, 500))
image_label = CTkLabel(root, image=bg_image, text="")
image_label.place(x=0, y=0, relwidth=1, relheight=1)

# --- Authentication Function ---
def authenticate_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Required", "⚠️ Please fill in both Username and Password.")
        return

    # Check credentials against users.json file
    try:
        with open("users.json", "r") as file:
            users = json.load(file)
            if username in users and check_password(users[username], password):
                messagebox.showinfo("Login Success", f"✅ Welcome back, {username}!")
                root.destroy()
                import Gui  # Opens the dashboard
            else:
                messagebox.showerror("Login Failed", "❌ Invalid credentials")
                username_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
                username_entry.focus()

    except FileNotFoundError:
        messagebox.showerror("Error", "❌ Users file not found.")

def check_password(stored_hash, password):
    return stored_hash == hashlib.sha256(password.encode()).hexdigest()

# --- Registration Function ---
def register_user():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Required", "⚠️ Please fill in both Username and Password.")
        return

    # Check if user already exists
    try:
        with open("users.json", "r") as file:
            users = json.load(file)
            if username in users:
                messagebox.showerror("Registration Failed", "❌ Username already exists.")
                return
    except FileNotFoundError:
        users = {}

    # Hash password and save new user
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    users[username] = password_hash

    with open("users.json", "w") as file:
        json.dump(users, file)

    messagebox.showinfo("Registration Success", "✅ User registered successfully!")
    username_entry.delete(0, 'end')
    password_entry.delete(0, 'end')

# --- Login Frame ---
frame = CTkFrame(root, corner_radius=20, fg_color=("white", "lightgray"), width=400, height=300)
frame.place(relx=0.5, rely=0.5, anchor="center")

CTkLabel(frame, text="🔐 Login to YTmatrix", font=("Arial", 20, "bold"), text_color="lightblue").pack(pady=(10, 20))

# Username
CTkLabel(frame, text="Username:").pack()
username_entry = CTkEntry(frame, width=250, border_width=2)
username_entry.pack(pady=5)

# Password
CTkLabel(frame, text="Password:").pack()
password_entry = CTkEntry(frame, show="*", width=250, border_width=2)
password_entry.pack(pady=5)

# --- Password Toggle ---
def toggle_password():
    if password_entry.cget("show") == "*":
        password_entry.configure(show="")
        toggle_btn.configure(text="🙈 Hide")
    else:
        password_entry.configure(show="*")
        toggle_btn.configure(text="👁 Show")

toggle_btn = CTkButton(frame, text="👁 Show", command=toggle_password, width=60, height=28, fg_color="lightgray")
toggle_btn.pack(pady=(0, 10))

# --- Login Button ---
def on_hover(event): login_button.configure(fg_color="lightblue")
def on_leave(event): login_button.configure(fg_color="lightgray")

login_button = CTkButton(frame, text="Login", command=authenticate_login, fg_color="lightgray", text_color="black")
login_button.pack(pady=10)
login_button.bind("<Enter>", on_hover)
login_button.bind("<Leave>", on_leave)

# --- Registration Button ---
register_button = CTkButton(frame, text="Register", command=register_user, fg_color="lightgray", text_color="black")
register_button.pack(pady=5)

# --- Input Field Focus Effect ---
def on_focus_in(event): event.widget.configure(border_width=2, border_color="lightblue")
def on_focus_out(event): event.widget.configure(border_width=2, border_color="lightgray")

username_entry.bind("<FocusIn>", on_focus_in)
username_entry.bind("<FocusOut>", on_focus_out)
password_entry.bind("<FocusIn>", on_focus_in)
password_entry.bind("<FocusOut>", on_focus_out)

# Trigger login on Enter key
root.bind('<Return>', lambda event: authenticate_login())

root.mainloop()