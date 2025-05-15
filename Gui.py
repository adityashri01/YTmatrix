import customtkinter as ctk
from tkinter import messagebox
from main import fetch_playlist_videos, fetch_video_details
import time
from firebase import db
from google.cloud import firestore  # required for SERVER_TIMESTAMP
from datetime import datetime

logged_in_user = None  # Global variable for current logged-in user


logged_in = True

def save_search_history(url, max_duration=None, max_videos=None, sort_option=None):
    if not logged_in_user:
        messagebox.showerror("Error", "User not logged in.")
        return

    search_record = {
        "url": url,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "filters": {
            "max_duration": max_duration,
            "max_videos": max_videos,
            "sort_by": sort_option
        }
    }
    
    try:
        db.collection("users").document(logged_in_user).collection("search_history").add(search_record)
        messagebox.showinfo("Success", "Search history saved.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save search history: {e}")



def start_dashboard(username):
    global logged_in_user
    logged_in_user = username

def logout():
    global logged_in
    logged_in = False
    messagebox.showinfo("Logout", "You have successfully logged out.")
    app.destroy()

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("YTmatrix Dashboard")
app.geometry("1200x800")
app.state("zoomed")
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

main_frame = ctk.CTkFrame(app, corner_radius=20, fg_color=("white", "#f1f1f1"))
main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
main_frame.grid_rowconfigure(4, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# === Top Buttons Row with Center Label ===
top_buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
top_buttons_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
top_buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

theme_button = ctk.CTkButton(top_buttons_frame, text="Toggle Theme", command=lambda: toggle_theme(), height=40, corner_radius=12)
theme_button.grid(row=0, column=0, sticky="w", padx=10)

center_label = ctk.CTkLabel(top_buttons_frame, text="📊 YT Dashboard", font=("Arial Black", 20))
center_label.grid(row=0, column=1)

logout_button = ctk.CTkButton(top_buttons_frame, text="Logout", command=logout, height=40, corner_radius=12, width=100, fg_color="red", hover_color="darkred")
logout_button.grid(row=0, column=2, sticky="e", padx=10)

# === URL Input Section ===
url_section = ctk.CTkFrame(main_frame, corner_radius=15, fg_color=("lightblue", "lightcyan"))
url_section.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 5))

url_label = ctk.CTkLabel(url_section, text="🎮 Playlist or Video URL:", font=("Arial", 16, "bold"))
url_label.pack(anchor="w", padx=10, pady=5)

url_entry = ctk.CTkEntry(url_section, font=("Arial", 14), corner_radius=8, border_width=2, border_color="gray")
url_entry.pack(fill="x", padx=10, pady=5)

# === Filters Section ===
filters_label = ctk.CTkLabel(main_frame, text="🎛 Filter Options", font=("Arial Bold", 18, "underline"))
filters_label.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))

filters_frame = ctk.CTkFrame(main_frame, corner_radius=10, fg_color=("lightgray", "white"))
filters_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 5))

label_duration = ctk.CTkLabel(filters_frame, text="Max Duration (hr):", font=("Arial", 14, "bold"))
label_duration.grid(row=1, column=0, padx=10, pady=5, sticky="e")
max_duration_entry = ctk.CTkEntry(filters_frame, width=80, corner_radius=8, border_width=2, border_color="gray")
max_duration_entry.grid(row=1, column=1, pady=5)

label_max_videos = ctk.CTkLabel(filters_frame, text="Max Videos:", font=("Arial", 14, "bold"))
label_max_videos.grid(row=1, column=2, padx=10, pady=5, sticky="e")
video_count_entry = ctk.CTkOptionMenu(filters_frame, values=["None", "5", "10", "15", "20"], width=100, corner_radius=8)
video_count_entry.set("None")
video_count_entry.grid(row=1, column=3, pady=5)

label_sort_by = ctk.CTkLabel(filters_frame, text="Sort By:", font=("Arial", 14, "bold"))
label_sort_by.grid(row=1, column=4, padx=10, pady=5, sticky="e")
sort_option = ctk.CTkOptionMenu(filters_frame, values=["None", "Duration", "Published Date", "Views"], width=160, corner_radius=8)
sort_option.grid(row=1, column=5, pady=5, padx=5)

# === Output Section ===
output_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color=("lightyellow", "whitesmoke"))
output_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
output_text = ctk.CTkTextbox(output_frame, font=("Arial", 14), wrap="word", height=300, corner_radius=8, border_width=2, border_color="gray")
output_text.pack(expand=True, fill="both", padx=10, pady=10)

# === Fetch Button at Bottom Center ===
fetch_button = ctk.CTkButton(app, text="🔍 Fetch Data", command=lambda: fetch_data(), height=45, corner_radius=12)
fetch_button.grid(row=1, column=0, pady=10)

# Spinner and label
loading_spinner = ctk.CTkProgressBar(main_frame, width=400, corner_radius=8)
loading_spinner.grid(row=5, column=0, pady=10, padx=10)
loading_spinner.set(0)

loading_label = ctk.CTkLabel(main_frame, text="", font=("Arial", 14))
loading_label.grid(row=6, column=0)

def fetch_data():
    loading_spinner.set(0.1)
    loading_label.configure(text="⏳ Fetching data...")
    app.update_idletasks()

    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a playlist or video URL.")
        loading_spinner.set(0)
        loading_label.configure(text="")
        return

    max_videos = None
    max_duration = None

    try:
        if video_count_entry.get() != "None":
            max_videos = int(video_count_entry.get())

        if max_duration_entry.get().strip():
            max_duration = float(max_duration_entry.get())
            if max_duration <= 0:
                raise ValueError
    except:
        messagebox.showerror("Error", "Please enter valid numeric filter values.")
        loading_spinner.set(0)
        loading_label.configure(text="")
        return

    output_text.delete("1.0", "end")

    # Save search history to Firestore
    search_record = {
        "url": url,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "filters": {
            "max_duration": max_duration,
            "max_videos": max_videos,
            "sort_by": sort_option.get()
        }
    }
    db.collection("search_history").add(search_record)

    try:
        if "list=" in url:
            videos = fetch_playlist_videos(url, sort_by=sort_option.get(), max_videos=max_videos, max_duration=max_duration)
        else:
            videos = fetch_video_details(url)

        time.sleep(2)

        if not videos:
            messagebox.showinfo("Not Found", "❌ No video(s) found.")
        else:
            if sort_option.get() == "Views":
                videos.sort(key=lambda x: int(x["view_count"]), reverse=True)

            for video in videos:
                output_text.insert("end", f"🎬 {video['title']}\n📅 Published: {video['published']}\n⏳ Duration: {video['duration']}\n👁️ Views: {video['view_count']}\n\n")

        loading_spinner.set(0)
        loading_label.configure(text="✅ Done")

    except Exception as e:
        messagebox.showerror("Error", f"❌ Failed to fetch data.\n{str(e)}")
        loading_spinner.set(0)
        loading_label.configure(text="")

# === Theme Toggle Function ===
is_dark_mode = False
def toggle_theme():
    global is_dark_mode
    if not is_dark_mode:
        app.configure(bg="black")
        main_frame.configure(fg_color="black")
        url_section.configure(fg_color="black")
        filters_frame.configure(fg_color="black")
        output_frame.configure(fg_color="black")

        for widget in [filters_label, loading_label, url_label, label_duration, label_max_videos, label_sort_by, center_label]:
            widget.configure(text_color="white")

        fetch_button.configure(fg_color="gray20", text_color="white", hover_color="gray30")
        logout_button.configure(fg_color="red", text_color="white", hover_color="darkred")
        theme_button.configure(fg_color="gray20", text_color="white", hover_color="gray30")
        output_text.configure(fg_color="black", text_color="white")
        sort_option.configure(button_color="gray20", text_color="white")
        video_count_entry.configure(button_color="gray20", text_color="white")
        is_dark_mode = True
    else:
        app.configure(bg="white")
        main_frame.configure(fg_color="#f1f1f1")
        url_section.configure(fg_color="lightcyan")
        filters_frame.configure(fg_color="white")
        output_frame.configure(fg_color="whitesmoke")

        for widget in [filters_label, loading_label, url_label, label_duration, label_max_videos, label_sort_by, center_label]:
            widget.configure(text_color="black")

        fetch_button.configure(fg_color="blue", text_color="white", hover_color="skyblue")
        logout_button.configure(fg_color="red", text_color="white", hover_color="darkred")
        theme_button.configure(fg_color="blue", text_color="white", hover_color="skyblue")
        output_text.configure(fg_color="white", text_color="black")
        sort_option.configure(button_color="white", text_color="black")
        video_count_entry.configure(button_color="white", text_color="black")
        is_dark_mode = False

search_button = ctk.CTkButton(app, text="Save Search History", command=lambda: save_search_history("https://example.com"))
search_button.pack(pady=20)

# === Run App ===
app.mainloop()
