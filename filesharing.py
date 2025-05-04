import os
import tkinter as tk
from tkinter import messagebox
import socket
import threading
import pickle
import time
from tkinter import filedialog
import shutil  # Add this import at the top of your file
from PIL import Image, ImageTk  # Ensure this import is at the top of your file
from tkinter import ttk  # Add this import for the progress bar
import requests
from flask import Flask, request, jsonify  # Add Flask imports

app = Flask(__name__)  # Initialize Flask app

print("Current working directory:", os.getcwd())
print("Does person_icon.png exist?", os.path.exists("person_icon.png"))

if not os.path.exists("person_icon.png"):
    print("Default profile icon (person_icon.png) is missing. Please add it to the working directory.")

if not os.path.exists('uploads'):
    os.makedirs('uploads')

#Setting Up User Authentication and File Storage
#Setting Up User Authentication and File Storage
#Setting Up User Authentication and File Storage

# Global variables
user_data = {}  # Store username, password pairs
file_storage = {}  # Store files with metadata like upload time, size, etc.
chat_log = []  # Store chat messages
MAX_STORAGE = 10 * 1024 * 1024 * 1024  # 10GB max storage
current_storage = 0  # Keep track of current used storage
friends = {}  # Example: {'user1': ['user2', 'user3'], 'user2': ['user1']}
friend_requests = {}  # Example: {'user1': ['user3']}

# Example structure for user_data:
# user_data = {
#     "username1": {
#         "password": "hashed_password",
#         "profile_icon": "path_to_icon.png",
#         "bio": "User bio",
#         "friends": ["friend1", "friend2"]
#     }
# }

# File path for user data and logs
USER_DATA_PATH = 'user_data.pkl'
FILE_STORAGE_PATH = 'file_storage.pkl'
CHAT_LOG_PATH = 'chat_log.pkl'

SERVER_URL = "http://192.168.1.59:5000"

# Save data to files
def save_data():
    try:
        with open(USER_DATA_PATH, 'wb') as f:
            pickle.dump(user_data, f)
        with open(FILE_STORAGE_PATH, 'wb') as f:
            pickle.dump(file_storage, f)
        with open(CHAT_LOG_PATH, 'wb') as f:
            pickle.dump(chat_log, f)
        with open('friends.pkl', 'wb') as f:  # Save friends dictionary
            pickle.dump(friends, f)
        with open('friend_requests.pkl', 'wb') as f:  # Save friend requests
            pickle.dump(friend_requests, f)
    except Exception as e:
        print(f"Error saving data: {e}")

# Function to load user data and file storage from files
def load_data():
    global user_data, file_storage, chat_log, friends, friend_requests
    if os.path.exists(USER_DATA_PATH):
        try:
            with open(USER_DATA_PATH, 'rb') as f:
                user_data = pickle.load(f)
                if not isinstance(user_data, dict):  # Ensure it's a dictionary
                    raise ValueError("Corrupted user_data file")
        except Exception as e:
            print(f"Error loading user_data: {e}")
            user_data = {}  # Reset to an empty dictionary if corrupted
    else:
        user_data = {}

    if os.path.exists(FILE_STORAGE_PATH):
        try:
            with open(FILE_STORAGE_PATH, 'rb') as f:
                file_storage = pickle.load(f)
                if not isinstance(file_storage, dict):
                    raise ValueError("Corrupted file_storage file")
        except Exception as e:
            print(f"Error loading file_storage: {e}")
            file_storage = {}

    if os.path.exists(CHAT_LOG_PATH):
        try:
            with open(CHAT_LOG_PATH, 'rb') as f:
                chat_log = pickle.load(f)
                if not isinstance(chat_log, list):
                    raise ValueError("Corrupted chat_log file")
        except Exception as e:
            print(f"Error loading chat_log: {e}")
            chat_log = []

    if os.path.exists('friends.pkl'):
        try:
            with open('friends.pkl', 'rb') as f:
                friends = pickle.load(f)
        except Exception as e:
            print(f"Error loading friends: {e}")
            friends = {}

    if os.path.exists('friend_requests.pkl'):
        try:
            with open('friend_requests.pkl', 'rb') as f:
                friend_requests = pickle.load(f)
        except Exception as e:
            print(f"Error loading friend_requests: {e}")
            friend_requests = {}

def reload_data():
    global chat_log, file_storage
    if os.path.exists(CHAT_LOG_PATH):
        try:
            with open(CHAT_LOG_PATH, 'rb') as f:
                chat_log = pickle.load(f)
        except Exception as e:
            print(f"Error reloading chat_log: {e}")

    if os.path.exists(FILE_STORAGE_PATH):
        try:
            with open(FILE_STORAGE_PATH, 'rb') as f:
                file_storage = pickle.load(f)
        except Exception as e:
            print(f"Error reloading file_storage: {e}")

# Function to create a new user account
def create_user(username, password):
    response = requests.post(f"{SERVER_URL}/register", json={"username": username, "password": password})
    return response.json().get('message', "Error")

# Function to authenticate user
def authenticate_user(username, password):
    response = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
    return response.json().get('success', False)

#File Upload and Management
#File Upload and Management
#File Upload and Management

# Function to handle file uploads
def upload_file(username, file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"{SERVER_URL}/upload",  # Use SERVER_URL here
            files={'file': f},
            data={'username': username}
        )
    return response.json().get('message', "Error")

def upload_file_client(username, file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"{SERVER_URL}/upload",  # Use SERVER_URL here
            files={'file': f},
            data={'username': username}
        )
    return response.json().get('message', "Error")

# Function to check and delete old files
def cleanup_files():
    global current_storage
    current_time = time.time()

    files_to_delete = []
    for file_name, metadata in file_storage.items():
        if current_time - metadata['upload_time'] > 30 * 24 * 60 * 60:  # 1 month
            files_to_delete.append(file_name)

    for file_name in files_to_delete:
        os.remove(os.path.join('uploads', file_name))
        current_storage -= file_storage[file_name]['size']
        del file_storage[file_name]
    save_data()

# Function to list files uploaded by the user
def list_files(username):
    files = [file for file, metadata in file_storage.items() if metadata['username'] == username]
    return files

#Networking for Peer-to-Peer (P2P) File Transfer
#Networking for Peer-to-Peer (P2P) File Transfer
#Networking for Peer-to-Peer (P2P) File Transfer

# Function to establish peer-to-peer connection and send file
def p2p_send_file(username, target_username, file_path):
    target_ip = get_ip_for_user(target_username)
    if target_ip:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, 12345))
        with open(file_path, 'rb') as f:
            data = f.read()
            sock.sendall(data)
        sock.close()
        return "File sent successfully."
    return "Target user not found."

def get_ip_for_user(username):
    # Here you should maintain a mapping of users to IP addresses for P2P
    # For simplicity, this returns a dummy value.
    return '127.0.0.1'  # Example: localhost for testing

# Function to listen for incoming files on a given port
def listen_for_files():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(5)

    while True:
        client_socket, _ = server_socket.accept()
        with open('received_file', 'wb') as f:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
        client_socket.close()

#Chat System
#Chat System
#Chat System

#TK
#TK
#TK

# Function to send a chat message
def send_chat_message(username, message):
    try:
        response = requests.post(
            f"{SERVER_URL}/send_message",
            json={"username": username, "message": message}
        )
        return response.json().get('message', "Error")
    except Exception as e:
        print(f"Error sending message: {e}")
        return "Error sending message"

# Function to retrieve recent chat messages
def get_chat_messages():
    try:
        response = requests.get(f"{SERVER_URL}/get_messages")
        return response.json()  # Expecting a JSON response from the server
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

# Function to send a friend request
def send_friend_request(from_user, to_user):
    if to_user not in user_data:
        return "User does not exist."
    if to_user not in friend_requests:
        friend_requests[to_user] = []
    if from_user not in friend_requests[to_user]:
        friend_requests[to_user].append(from_user)
        save_data()
        return "Friend request sent."
    return "Friend request already sent."

# Function to accept a friend request
def accept_friend_request(user, friend):
    if user in friend_requests and friend in friend_requests[user]:
        friend_requests[user].remove(friend)
        if user not in friends:
            friends[user] = []
        if friend not in friends:
            friends[friend] = []
        if friend not in friends[user]:  # Avoid duplicates
            friends[user].append(friend)
        if user not in friends[friend]:  # Avoid duplicates
            friends[friend].append(user)
        save_data()
        return "Friend request accepted."
    return "No friend request to accept."

# Function to decline a friend request
def decline_friend_request(user, friend):
    if user in friend_requests and friend in friend_requests[user]:
        friend_requests[user].remove(friend)
        save_data()
        return "Friend request declined."
    return "No friend request to decline."

# Create GUI
def create_gui():
    global root
    root = tk.Tk()
    root.title("File Sharing System")

    def on_login():
        username = entry_username.get()
        password = entry_password.get()
        if authenticate_user(username, password):
            messagebox.showinfo("Success", "Logged in successfully.")
            # Clear the login screen and show the main application
            for widget in root.winfo_children():
                widget.destroy()
            show_main_screen(username)
        else:
            messagebox.showerror("Error", "Invalid credentials.")

    def on_create_account():
        username = entry_username.get()
        password = entry_password.get()
        result = create_user(username, password)
        messagebox.showinfo("Result", result)
        if "successfully" in result:
            # Automatically log in the user after account creation
            for widget in root.winfo_children():
                widget.destroy()
            show_main_screen(username)

    # Create UI elements
    label_username = tk.Label(root, text="Username:")
    label_username.pack()
    entry_username = tk.Entry(root)
    entry_username.pack()

    label_password = tk.Label(root, text="Password:")
    label_password.pack()
    entry_password = tk.Entry(root, show='*')
    entry_password.pack()

    button_login = tk.Button(root, text="Login", command=on_login)
    button_login.pack()

    button_create_account = tk.Button(root, text="Create Account", command=on_create_account)
    button_create_account.pack()

    root.mainloop()

# Function to display the main application screen
def show_main_screen(username):
    global root
    root.geometry("600x800")  # Set to a vertical half-rectangle size

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Welcome label
    label_welcome = tk.Label(root, text=f"Welcome, {username}!", font=("Arial", 16))
    label_welcome.pack(pady=10)

    # Profile button (top-left corner)
    def create_profile_button():
        try:
            # Open and resize the image to 50x50 pixels
            icon_path = user_data[username].get("profile_icon", "person_icon.png")
            image = Image.open(icon_path)
            image = image.resize((50, 50), Image.Resampling.LANCZOS)
            profile_icon = ImageTk.PhotoImage(image)

            profile_button = tk.Button(root, image=profile_icon, command=lambda: show_profile_settings(username), width=50, height=50)
            profile_button.image = profile_icon  # Keep a reference to avoid garbage collection
        except Exception as e:
            print(f"Error loading profile icon: {e}")
            # Fallback to a text-based button if the image is not found or fails to load
            profile_button = tk.Button(root, text="Profile", command=lambda: show_profile_settings(username), width=10, height=2)

        profile_button.place(x=10, y=10)

    root.after(100, create_profile_button)  # Delay the creation of the profile button

    # Notification bell
    notification_bell = tk.Button(root, text="🔔", font=("Arial", 16), command=lambda: show_notifications(username))
    notification_bell.place(x=550, y=10)

    # Search bar for users
    search_frame = tk.Frame(root)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text="Search User:")
    search_label.pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5)

    def search_user():
        query = search_entry.get().lower()
        user_listbox.delete(0, tk.END)
        for user in user_data.keys():
            if query in user.lower():
                user_listbox.insert(tk.END, user)

    search_button = tk.Button(search_frame, text="Search", command=search_user)
    search_button.pack(side=tk.LEFT, padx=5)

    # Scrollable list of users
    user_list_frame = tk.Frame(root)
    user_list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    user_listbox = tk.Listbox(user_list_frame, height=15, width=50)
    user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(user_list_frame, orient=tk.VERTICAL, command=user_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    user_listbox.config(yscrollcommand=scrollbar.set)

    # Populate the user list
    def populate_user_list():
        if 'user_listbox' in globals() and user_listbox.winfo_exists():  # Check if the widget exists
            user_listbox.delete(0, tk.END)
            for user in user_data.keys():
                user_listbox.insert(tk.END, user)

    populate_user_list()

    def view_profile(event):
        selected_user = user_listbox.get(user_listbox.curselection())
        show_profile(selected_user, username)  # Pass the logged-in username as `current_user`

    user_listbox.bind("<Double-1>", view_profile)

    # Recent uploads section
    recent_uploads_label = tk.Label(root, text="Recent Uploads:", font=("Arial", 14))
    recent_uploads_label.pack(pady=10)

    recent_uploads_frame = tk.Frame(root)
    recent_uploads_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    recent_uploads_listbox = tk.Listbox(recent_uploads_frame, height=10, width=80)
    recent_uploads_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar_uploads = tk.Scrollbar(recent_uploads_frame, orient=tk.VERTICAL, command=recent_uploads_listbox.yview)
    scrollbar_uploads.pack(side=tk.RIGHT, fill=tk.Y)

    recent_uploads_listbox.config(yscrollcommand=scrollbar_uploads.set)

    # Populate recent uploads
    def populate_recent_uploads():
        try:
            response = requests.get(f"{SERVER_URL}/recent_uploads")
            recent_files = response.json()  # Expecting a JSON response from the server
            recent_uploads_listbox.delete(0, tk.END)
            for file in recent_files:
                recent_uploads_listbox.insert(tk.END, f"{file['name']} | {file['username']} | {file['upload_time']} | {file['size']} bytes")
        except Exception as e:
            print(f"Error fetching recent uploads: {e}")

    populate_recent_uploads()

    # Auto-refresh function
    def auto_refresh():
        if 'root' in globals() and root.winfo_exists():  # Check if the root window exists
            reload_data()  # Reload shared data from disk
            if 'user_listbox' in globals() and user_listbox.winfo_exists():  # Check if the widget exists
                populate_user_list()
            if 'recent_uploads_listbox' in globals() and recent_uploads_listbox.winfo_exists():  # Check if the recent uploads listbox exists
                populate_recent_uploads()
            root.after(10000, auto_refresh)  # Schedule the function to run every 10 seconds

    auto_refresh()  # Start the auto-refresh loop

    # Buttons for functionality
    button_upload = tk.Button(root, text="Upload File", command=lambda: [upload_file_ui(username), populate_recent_uploads()])
    button_upload.pack(pady=10)

    button_chat = tk.Button(root, text="Chat", command=lambda: chat_ui(username))
    button_chat.pack(pady=10)

    button_logout = tk.Button(root, text="Logout", command=logout)
    button_logout.pack(pady=10)

def show_notifications(username):
    notifications_window = tk.Toplevel(root)
    notifications_window.title("Notifications")
    notifications_window.geometry("300x400")

    requests_label = tk.Label(notifications_window, text="Friend Requests:", font=("Arial", 14))
    requests_label.pack(pady=10)

    requests_listbox = tk.Listbox(notifications_window, height=15, width=40)
    requests_listbox.pack(pady=10)

    for request in friend_requests.get(username, []):
        requests_listbox.insert(tk.END, request)

    def accept_request():
        selected = requests_listbox.get(requests_listbox.curselection())
        if selected:
            result = accept_friend_request(username, selected)
            requests_listbox.delete(requests_listbox.curselection())
            messagebox.showinfo("Friend Request", result)

    def decline_request():
        selected = requests_listbox.get(requests_listbox.curselection())
        if selected:
            result = decline_friend_request(username, selected)
            requests_listbox.delete(requests_listbox.curselection())
            messagebox.showinfo("Friend Request", result)

    accept_button = tk.Button(notifications_window, text="Accept", command=accept_request)
    accept_button.pack(pady=5)

    decline_button = tk.Button(notifications_window, text="Decline", command=decline_request)
    decline_button.pack(pady=5)

def upload_file_ui(username):
    # Create a new window for file upload
    upload_window = tk.Toplevel(root)
    upload_window.title("File Upload")
    upload_window.geometry("400x300")

    label = tk.Label(upload_window, text="Select a file to upload:")
    label.pack(pady=10)

    def upload_file_action():
        file_path = filedialog.askopenfilename()  # Use filedialog here
        if file_path:
            result = upload_file_client(username, file_path)  # Call the renamed function
            messagebox.showinfo("Upload Result", result)

    button_select_file = tk.Button(upload_window, text="Select File", command=upload_file_action)
    button_select_file.pack(pady=10)

def chat_ui(username):
    chat_window = tk.Toplevel(root)
    chat_window.title("Chatroom")
    chat_window.geometry("500x500")

    chat_log_display = tk.Text(chat_window, state="disabled", wrap="word", height=20, width=60)
    chat_log_display.pack(pady=10)

    def refresh_chat():
        chat_log_display.config(state="normal")
        chat_log_display.delete(1.0, tk.END)
        messages = get_chat_messages()
        for log in messages:
            chat_log_display.insert(
                tk.END,
                f"[{log['timestamp']}] {log['username']}: {log['message']}\n"
            )
        chat_log_display.config(state="disabled")

    refresh_button = tk.Button(chat_window, text="Refresh", command=refresh_chat)
    refresh_button.pack(pady=5)

    entry_message = tk.Entry(chat_window, width=50)
    entry_message.pack(pady=5)

    def send_message():
        message = entry_message.get()
        if message.strip():
            result = send_chat_message(username, message)
            messagebox.showinfo("Chat", result)
            entry_message.delete(0, tk.END)
            refresh_chat()

    button_send = tk.Button(chat_window, text="Send", command=send_message)
    button_send.pack(pady=5)

    # Auto-refresh function
    def auto_refresh_chat():
        refresh_chat()
        chat_window.after(2500, auto_refresh_chat)  # Schedule the function to run every 10 seconds

    auto_refresh_chat()  # Start the auto-refresh loop

    refresh_chat()

def logout():
    # Restart the application to show the login screen
    for widget in root.winfo_children():
        widget.destroy()
    create_gui()

def show_profile(username, current_user):
    profile_window = tk.Toplevel(root)
    profile_window.title(f"{username}'s Profile")
    profile_window.geometry("400x600")

    # Create a canvas and a scrollbar
    canvas = tk.Canvas(profile_window)
    scrollbar = tk.Scrollbar(profile_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configure the canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Profile icon
    icon_path = user_data[username].get("profile_icon", "person_icon.png")
    if not icon_path or not os.path.exists(icon_path):  # Use default if None or invalid
        icon_path = "person_icon.png"

    try:
        image = Image.open(icon_path)
        image = image.resize((150, 150), Image.Resampling.LANCZOS)
        profile_icon = ImageTk.PhotoImage(image)
        profile_icon_label = tk.Label(scrollable_frame, image=profile_icon)
        profile_icon_label.image = profile_icon
    except Exception as e:
        print(f"Error loading profile icon: {e}")
        profile_icon_label = tk.Label(scrollable_frame, text="[Profile Icon]", font=("Arial", 20), width=20, height=10, bg="gray")
    profile_icon_label.pack(pady=10)

    # Profile name
    profile_name = tk.Label(scrollable_frame, text=username, font=("Arial", 16))
    profile_name.pack(pady=10)

    # Bio
    bio_label = tk.Label(scrollable_frame, text="Bio:", font=("Arial", 14))
    bio_label.pack(pady=10)

    bio_text = tk.Label(scrollable_frame, text=user_data[username].get("bio", "No bio available."), wraplength=300, justify="left")
    bio_text.pack(pady=10)

    # Recent uploads
    recent_uploads_label = tk.Label(scrollable_frame, text="Recent Uploads:", font=("Arial", 14))
    recent_uploads_label.pack(pady=10)

    recent_uploads_listbox = tk.Listbox(scrollable_frame, height=10, width=50)
    recent_uploads_listbox.pack(pady=10)

    for file_name, metadata in file_storage.items():
        if metadata['username'] == username:
            upload_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(metadata['upload_time']))
            recent_uploads_listbox.insert(tk.END, f"{file_name} | {upload_time} | {metadata['size']} bytes")

    # Friend list
    friends_label = tk.Label(scrollable_frame, text="Friends:", font=("Arial", 14))
    friends_label.pack(pady=10)

    friends_listbox = tk.Listbox(scrollable_frame, height=10, width=50)
    friends_listbox.pack(pady=10)

    for friend in friends.get(username, []):  # Use `friends` dictionary to display friends
        friends_listbox.insert(tk.END, friend)

    # Add Friend button (only if viewing someone else's profile)
    if username != current_user:
        def add_friend():
            result = send_friend_request(current_user, username)
            messagebox.showinfo("Friend Request", result)

        add_friend_button = tk.Button(scrollable_frame, text="Add Friend", command=add_friend)
        add_friend_button.pack(pady=10)

def show_profile_settings(username):
    settings_window = tk.Toplevel(root)
    settings_window.title("Profile Settings")
    settings_window.geometry("400x600")

    # Profile icon
    def upload_profile_icon():
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                # Open the image and crop it to 1:1 aspect ratio
                image = Image.open(file_path)
                width, height = image.size
                min_dim = min(width, height)
                image = image.crop(((width - min_dim) // 2, (height - min_dim) // 2, (width + min_dim) // 2))
                # Resize to 512x512
                image = image.resize((512, 512), Image.Resampling.LANCZOS)
                # Save the image to a file
                icon_path = f"profile_icons/{username}_icon.png"
                os.makedirs("profile_icons", exist_ok=True)
                image.save(icon_path)
                # Update user data
                user_data[username]["profile_icon"] = icon_path
                save_data()
                # Update the displayed profile icon
                update_profile_icon()
                messagebox.showinfo("Success", "Profile picture updated successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload profile picture: {e}")

    def update_profile_icon():
        # Use a default icon if the profile icon is not set
        icon_path = user_data[username].get("profile_icon", "person_icon.png")
        if not icon_path or not os.path.exists(icon_path):  # Use default if None or invalid
            icon_path = "person_icon.png"

        try:
            image = Image.open(icon_path)
            image = image.resize((150, 150), Image.Resampling.LANCZOS)
            profile_icon = ImageTk.PhotoImage(image)
            profile_icon_label.config(image=profile_icon, text="")
            profile_icon_label.image = profile_icon
        except Exception as e:
            print(f"Error loading profile icon: {e}")
            profile_icon_label.config(text="[Profile Icon]", image="", bg="gray")

    profile_icon_label = tk.Label(settings_window, text="[Profile Icon]", font=("Arial", 20), width=20, height=10, bg="gray")
    profile_icon_label.pack(pady=10)
    update_profile_icon()

    change_icon_button = tk.Button(settings_window, text="Change Profile Picture", command=upload_profile_icon)
    change_icon_button.pack(pady=5)

    # Bio
    bio_label = tk.Label(settings_window, text="Bio:", font=("Arial", 14))
    bio_label.pack(pady=10)

    bio_entry = tk.Text(settings_window, height=5, width=40)
    bio_entry.insert("1.0", user_data[username].get("bio", ""))  # Load existing bio
    bio_entry.pack(pady=10)

    def save_bio():
        bio = bio_entry.get("1.0", tk.END).strip()
        if len(bio) > 256:
            messagebox.showerror("Error", "Bio cannot exceed 256 characters.")
        else:
            user_data[username]["bio"] = bio
            save_data()
            messagebox.showinfo("Success", "Bio updated successfully!")

    save_bio_button = tk.Button(settings_window, text="Save Bio", command=save_bio)
    save_bio_button.pack(pady=5)

    # Friend list
    friends_label = tk.Label(settings_window, text="Friends:", font=("Arial", 14))
    friends_label.pack(pady=10)

    friends_listbox = tk.Listbox(settings_window, height=10, width=50)
    friends_listbox.pack(pady=10)

    # Populate the friends list using the `friends` dictionary
    for friend in friends.get(username, []):
        friends_listbox.insert(tk.END, friend)

    def remove_friend():
        selected = friends_listbox.get(friends_listbox.curselection())
        if selected:
            # Remove the friendship from both users
            friends[username].remove(selected)
            friends[selected].remove(username)
            friends_listbox.delete(friends_listbox.curselection())
            save_data()
            messagebox.showinfo("Success", f"{selected} removed from friends.")

    remove_friend_button = tk.Button(settings_window, text="Remove Friend", command=remove_friend)
    remove_friend_button.pack(pady=5)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in the request"}), 400
    file = request.files['file']
    username = request.form.get('username')
    if not file or not username:
        return jsonify({"success": False, "message": "Missing file or username"}), 400
    upload_path = os.path.join('uploads', file.filename)
    os.makedirs('uploads', exist_ok=True)  # Ensure the uploads directory exists
    file.save(upload_path)
    file_storage[file.filename] = {
        'username': username,
        'upload_time': time.time(),
        'size': os.path.getsize(upload_path)
    }
    with open(FILE_STORAGE_PATH, 'wb') as f:
        pickle.dump(file_storage, f)
    return jsonify({"success": True, "message": "File uploaded successfully"})

# Load data on startup
load_data()

# Run the GUI
create_gui()
