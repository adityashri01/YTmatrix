from customtkinter import *
from tkinter import messagebox
import hashlib
from firebase import db

# Force Dark Mode and Theme
set_appearance_mode("dark")
set_default_color_theme("dark-blue")

root = CTk()
root.title("Login - YTmatrix")

# Start in fullscreen mode
root.attributes('-fullscreen', True)

def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)
    root.geometry("720x520")  # Resize window to normal size if you want

# Bind ESC key to exit fullscreen
root.bind('<Escape>', exit_fullscreen)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Required", "⚠️ Please fill in both Username and Password.")
        return

    users_ref = db.collection("users")
    try:
        query = users_ref.where("username", "==", username).get()
        if not query:
            messagebox.showerror("Login Failed", "❌ Username not found.")
            username_entry.delete(0, 'end')
            password_entry.delete(0, 'end')
            username_entry.focus()
            return

        for doc in query:
            user_data = doc.to_dict()
            stored_hash = user_data.get("password", "")
            if stored_hash == hash_password(password):
                messagebox.showinfo("Login Success", f"✅ Welcome back, {username}!")
                root.destroy()
                import Gui
                Gui.start_dashboard(username)   # <-- Username yahan bhej rahe hain
                return

            else:
                messagebox.showerror("Login Failed", "❌ Incorrect password.")
                username_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
                username_entry.focus()
                return
    except Exception as e:
        messagebox.showerror("Error", f"❌ An error occurred: {e}")

def register_user():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Required", "⚠️ Please fill in both Username and Password.")
        return

    users_ref = db.collection("users")
    try:
        existing = users_ref.where("username", "==", username).get()
        if existing:
            messagebox.showerror("Registration Failed", "❌ Username already exists.")
            return

        password_hash = hash_password(password)
        users_ref.add({
            "username": username,
            "password": password_hash
        })
        messagebox.showinfo("Registration Success", "✅ User registered successfully!")
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
    except Exception as e:
        messagebox.showerror("Error", f"❌ An error occurred: {e}")

# ----------- Improved UI ------------

frame = CTkFrame(root, corner_radius=25, fg_color="#121212", width=450, height=420)
frame.place(relx=0.5, rely=0.5, anchor="center")

welcome_label = CTkLabel(frame, text="Welcome to YTmatrix\nBest YouTube Playlist Analyzer", font=("Segoe UI", 20, "bold"), text_color="#00bfff", justify="center")
welcome_label.pack(pady=(15, 10))

CTkLabel(frame, text="🔐 Login to YTmatrix", font=("Segoe UI", 26, "bold"), text_color="#00bfff").pack(pady=(5, 20))

# Username
CTkLabel(frame, text="Username:", font=("Segoe UI", 14), text_color="#bbbbbb").pack(anchor="w", padx=40)
username_entry = CTkEntry(frame, width=320, height=40, fg_color="#1e1e1e", border_color="#333", text_color="white", font=("Segoe UI", 14))
username_entry.pack(pady=(5, 20), padx=40)

# Password
CTkLabel(frame, text="Password:", font=("Segoe UI", 14), text_color="#bbbbbb").pack(anchor="w", padx=40)
password_entry = CTkEntry(frame, show="*", width=320, height=40, fg_color="#1e1e1e", border_color="#333", text_color="white", font=("Segoe UI", 14))
password_entry.pack(pady=(5, 15), padx=40)

def toggle_password():
    if password_entry.cget("show") == "*":
        password_entry.configure(show="")
        toggle_btn.configure(text="🙈 Hide")
    else:
        password_entry.configure(show="*")
        toggle_btn.configure(text="👁 Show")

toggle_btn = CTkButton(frame, text="👁 Show", command=toggle_password, width=70, height=30, fg_color="#222222", text_color="#bbb", hover_color="#333")
toggle_btn.pack(pady=(0, 25))

def on_hover(event): login_button.configure(fg_color="#007acc")
def on_leave(event): login_button.configure(fg_color="#333333")

login_button = CTkButton(frame, text="Login", command=authenticate_login, width=320, height=45, fg_color="#333333", text_color="white", hover_color="#007acc", font=("Segoe UI", 16, "bold"))
login_button.pack()
login_button.bind("<Enter>", on_hover)
login_button.bind("<Leave>", on_leave)

register_button = CTkButton(frame, text="Register", command=register_user, width=320, height=40, fg_color="#222222", text_color="#bbb", hover_color="#007acc", font=("Segoe UI", 14))
register_button.pack(pady=(15, 15))

def on_focus_in(event): event.widget.configure(border_color="#00bfff")
def on_focus_out(event): event.widget.configure(border_color="#333")

username_entry.bind("<FocusIn>", on_focus_in)
username_entry.bind("<FocusOut>", on_focus_out)
password_entry.bind("<FocusIn>", on_focus_in)
password_entry.bind("<FocusOut>", on_focus_out)

root.bind('<Return>', lambda event: authenticate_login())

root.mainloop()
