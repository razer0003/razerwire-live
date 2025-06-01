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
#1
app = Flask(__name__)  # Initialize Flask app
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # Set max upload size to 1 GB

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

# Example structure for file_storage:
# file_storage = {
#     "file1.txt": {
#         "username": "user1",
#         "upload_time": 1683072000,
#         "size": 1024,
#         "downloads": 0
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
            print("Loaded user_data:", user_data)  # Debugging line
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
    try:
        response = requests.post(f"{SERVER_URL}/register", json={"username": username, "password": password})
        if response.status_code == 200:
            return response.json().get('message', "Error")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.JSONDecodeError:
        return "Error: Server returned an invalid response."
    except Exception as e:
        return f"Error: {e}"

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
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{SERVER_URL}/upload",
                files={'file': f},
                data={'username': username}
            )
        if response.status_code == 413:
            return "Error: File size exceeds the server's limit."
        return response.json().get('message', "Error")
    except requests.exceptions.JSONDecodeError:
        return "Error: Server returned an invalid response."
    except Exception as e:
        return f"Error: {e}"

def download_file(file_name):
    response = requests.get(f"{SERVER_URL}/download/{file_name}", stream=True)
    if response.status_code == 200:
        save_path = filedialog.asksaveasfilename(initialfile=file_name)
        if save_path:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            messagebox.showinfo("Success", f"File {file_name} downloaded successfully!")
    else:
        messagebox.showerror("Error", "Failed to download file.")

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

def fetch_file_metadata():
    try:
        response = requests.get(f"{SERVER_URL}/file_metadata")
        if response.status_code == 200:
            return response.json().get("files", {})
        else:
            print(f"Error fetching file metadata: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching file metadata: {e}")
        return {}

def populate_recent_uploads():
    global file_storage
    try:
        # Fetch the latest file metadata from the server
        response = requests.get(f"{SERVER_URL}/recent_uploads")
        if response.status_code == 200:
            file_metadata = response.json().get("files", [])
            file_list = [
                {"name": file['name'], "downloads": file.get('downloads', 0), "size": file.get('size', 0), "upload_time": file.get('upload_time', 0)}
                for file in file_metadata
            ]

            # Clear the Listbox and populate it with valid files
            recent_uploads_listbox.delete(0, tk.END)
            for file in file_list:
                recent_uploads_listbox.insert(
                    tk.END,
                    f"{file['name']} | Downloads: {file['downloads']} | Size: {file['size']} bytes | Uploaded: {time.ctime(file['upload_time'])}"
                )

            # Attach the "Sort By" menu to the Recent Uploads section
            create_sort_by_menu(file_list, recent_uploads_listbox, sort_button_recent_uploads)
        else:
            print(f"Failed to fetch recent uploads: {response.status_code}")
    except Exception as e:
        print(f"Error fetching recent uploads: {e}")

populate_recent_uploads()

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

# Function to retrieve recent chat messages
def get_chat_messages():
    try:
        response = requests.get(f"{SERVER_URL}/get_messages")
        return response.json()  # Expecting a JSON response from the server
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return []

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

#TK
#TK
#TK

# Function to send a friend request
def send_friend_request(from_user, to_user):
    response = requests.post(f"{SERVER_URL}/send_friend_request", json={"from_user": from_user, "to_user": to_user})
    return response.json().get("message", "Error")

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

def add_friend(username, friend):
    response = requests.post(f"{SERVER_URL}/add_friend", json={"username": username, "friend": friend})
    return response.json().get("message", "Error")

def remove_friend(username, friend):
    response = requests.post(f"{SERVER_URL}/remove_friend", json={"username": username, "friend": friend})
    return response.json().get("message", "Error")

def get_profile_picture(username):
    try:
        # Request the profile picture from the server
        response = requests.get(f"{SERVER_URL}/profile_picture/{username}", stream=True)
        if response.status_code == 200:
            # Save the profile picture locally
            profile_icons_path = "profile_icons"
            os.makedirs(profile_icons_path, exist_ok=True)  # Ensure the directory exists
            profile_picture_path = os.path.join(profile_icons_path, f"{username}_profile.png")
            print(f"Downloading profile picture for {username} to {profile_picture_path}")  # Debugging line
            with open(profile_picture_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return profile_picture_path
        else:
            print(f"Failed to fetch profile picture for {username}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching profile picture for {username}: {e}")
        return None

def get_user_data(username):
    response = requests.get(f"{SERVER_URL}/user_data/{username}")
    if response.status_code == 200:
        return response.json()
    return None

def update_bio(username, bio):
    response = requests.post(f"{SERVER_URL}/update_bio", json={"username": username, "bio": bio})
    return response.json().get("message", "Error")

def set_profile_picture(username, file_name):
    print(f"Setting profile picture for user: {username} with file: {file_name}")  # Debugging line

    try:
        # Send a request to the server to set the file as the profile picture
        response = requests.post(
            f"{SERVER_URL}/set_profile_picture",
            json={"username": username, "file_name": file_name}
        )
        if response.status_code == 200 and response.json().get("success"):
            messagebox.showinfo("Success", "Profile picture updated successfully!")
            update_profile_button(username)  # Refresh the profile picture instantly
        else:
            messagebox.showerror("Error", response.json().get("message", "Failed to set profile picture."))
    except Exception as e:
        print(f"Error in set_profile_picture: {e}")  # Debugging line
        messagebox.showerror("Error", f"An error occurred: {e}")

def update_profile_button(username):
    global profile_button  # Ensure profile_button is accessible globally
    try:
        print("Updating profile button for user:", username)
        # Download the profile picture from the server
        profile_picture_path = get_profile_picture(username)
        if not profile_picture_path or not os.path.exists(profile_picture_path):
            print(f"Profile picture not found for {username}. Using default icon.")
            profile_picture_path = "person_icon.png"

        # Open and resize the image to fit the button (50x50 pixels)
        image = Image.open(profile_picture_path)
        image = image.resize((50, 50), Image.Resampling.LANCZOS)
        profile_icon = ImageTk.PhotoImage(image)

        # Configure the button to use the image and set its dimensions
        profile_button.config(image=profile_icon, text="", width=50, height=50)
        profile_button.image = profile_icon  # Keep a reference to prevent garbage collection
    except Exception as e:
        print(f"Error updating profile button: {e}")
        profile_button.config(text="Profile", image="", width=10, height=2)

def update_profile_icon(username, profile_icon_label):
    icon_path = f"profile_icons/{username}_profile.png"
    if not os.path.exists(icon_path):  # Use default if the profile picture is missing
        print(f"Profile picture not found for {username}. Using default icon.")
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
    global profile_button  # Make profile_button accessible globally
    global recent_uploads_listbox  # Make recent_uploads_listbox accessible globally
    global sort_button_recent_uploads  # Make sort_button_recent_uploads accessible globally

    # Clear existing widgets
    for widget in root.winfo_children():
        widget.destroy()

    # Create the profile button
    profile_button = tk.Button(root, text="Profile", command=lambda: show_profile_settings(username), width=10, height=2)
    profile_button.place(x=10, y=10)
    update_profile_button(username)
    root.update()  # Force the GUI to refresh

    root.geometry("600x800")  # Set to a vertical half-rectangle size

    # Welcome label
    label_welcome = tk.Label(root, text=f"Welcome, {username}!", font=("Arial", 16))
    label_welcome.pack(pady=10)

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
        try:
            response = requests.get(f"{SERVER_URL}/all_users")
            print("Server response for all users:", response.json())  # Debugging line
            users = response.json().get("users", [])
            user_listbox.delete(0, tk.END)
            for user in users:
                user_listbox.insert(tk.END, user)
        except Exception as e:
            print(f"Error fetching user list: {e}")

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

    # Create the "Sort By" button
    sort_button_recent_uploads = tk.Button(root, text="Sort By")
    sort_button_recent_uploads.pack(pady=5)

    # Populate recent uploads
    populate_recent_uploads()

    def on_file_double_click(event):
        selected_file = recent_uploads_listbox.get(recent_uploads_listbox.curselection()).split(" | ")[0]
        download_file(selected_file)

    recent_uploads_listbox.bind("<Double-1>", on_file_double_click)

    def on_right_click(event):
        try:
            selected_file = recent_uploads_listbox.get(recent_uploads_listbox.curselection())
            parts = selected_file.split(" | ")
            if len(parts) < 2:
                raise ValueError("Invalid file entry format")
            file_name = parts[0]

            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Download", command=lambda: download_file(file_name))
            menu.add_command(label="View User Profile", command=lambda: show_profile(file_owner, username))
            menu.add_command(label="Set as Profile Picture", command=lambda: set_profile_picture(username, file_name))
            menu.add_command(label="Report", command=lambda: messagebox.showinfo("Report", "Feature coming soon!"))
            menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error handling right-click: {e}")

    recent_uploads_listbox.bind("<Button-3>", on_right_click)

    # Auto-refresh function
    def auto_refresh():
        if 'root' in globals() and root.winfo_exists():  # Check if the root window exists
            reload_data()  # Reload shared data from disk
            if 'recent_uploads_listbox' in globals() and recent_uploads_listbox.winfo_exists():  # Check if the recent uploads listbox exists
                populate_recent_uploads()  # Refresh recent uploads
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

    # Fetch friend requests from the server
    try:
        response = requests.get(f"{SERVER_URL}/friend_requests", params={"username": username})
        if response.status_code == 200:
            friend_requests = response.json().get("requests", [])
        else:
            messagebox.showerror("Error", f"Failed to fetch friend requests: {response.status_code}")
            friend_requests = []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to connect to the server: {e}")
        friend_requests = []

    for request in friend_requests:
        requests_listbox.insert(tk.END, request)

    def accept_request():
        try:
            selected = requests_listbox.get(requests_listbox.curselection())
            if selected:
                response = requests.post(f"{SERVER_URL}/accept_friend_request", json={"user": username, "friend": selected})
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        requests_listbox.delete(requests_listbox.curselection())
                        messagebox.showinfo("Success", f"Accepted friend request from {selected}.")
                    else:
                        messagebox.showerror("Error", result.get("message", "Failed to accept friend request."))
                else:
                    messagebox.showerror("Error", f"Server returned status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Failed to connect to the server: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def decline_request():
        selected = requests_listbox.get(requests_listbox.curselection())
        if selected:
            response = requests.post(f"{SERVER_URL}/decline_friend_request", json={"user": username, "friend": selected})
            if response.json().get("success"):
                requests_listbox.delete(requests_listbox.curselection())
                messagebox.showinfo("Success", f"Declined friend request from {selected}.")
            else:
                messagebox.showerror("Error", "Failed to decline friend request.")

    accept_button = tk.Button(notifications_window, text="Accept", command=accept_request)
    accept_button.pack(pady=5)

    decline_button = tk.Button(notifications_window, text="Decline", command=decline_request)
    decline_button.pack(pady=5)

def upload_file_ui(username):
    upload_window = tk.Toplevel(root)
    upload_window.title("File Upload")
    upload_window.geometry("400x300")

    label = tk.Label(upload_window, text="Select a file to upload (Max: 1 GB):")
    label.pack(pady=10)

    def upload_file_action():
        file_path = filedialog.askopenfilename()
        if file_path:
            result = upload_file_client(username, file_path)
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
            if isinstance(log, dict) and all(key in log for key in ("timestamp", "username", "message")):
                chat_log_display.insert(
                    tk.END,
                    f"[{log['timestamp']}] {log['username']}: {log['message']}\n"
                )
            else:
                print(f"Invalid log entry: {log}")  # Debugging line
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
    user_info = get_user_data(username)  # Fetch user data from the server
    if not user_info:
        messagebox.showerror("Error", f"User '{username}' does not exist.")
        return

    profile_window = tk.Toplevel(root)
    profile_window.title(f"{username}'s Profile")
    profile_window.geometry("400x600")

    # Create a scrollable frame
    scrollable_frame = make_scrollable_window(profile_window)

    # Profile icon
    profile_picture_path = get_profile_picture(username)
    if profile_picture_path and os.path.exists(profile_picture_path):
        try:
            profile_image = Image.open(profile_picture_path)
            profile_image = profile_image.resize((150, 150), Image.Resampling.LANCZOS)
            profile_photo = ImageTk.PhotoImage(profile_image)
            profile_label = tk.Label(scrollable_frame, image=profile_photo)
            profile_label.image = profile_photo
            profile_label.pack(pady=10, anchor="center")
        except Exception as e:
            print(f"Error loading profile picture: {e}")
            profile_label = tk.Label(scrollable_frame, text="[Profile Icon]", font=("Arial", 20), bg="gray")
            profile_label.pack(pady=10, anchor="center")
    else:
        profile_label = tk.Label(scrollable_frame, text="[Profile Icon]", font=("Arial", 20), bg="gray")
        profile_label.pack(pady=10, anchor="center")

    # Profile name
    profile_name = tk.Label(scrollable_frame, text=username, font=("Arial", 16))
    profile_name.pack(pady=10, anchor="center")

    # Bio
    bio_label = tk.Label(scrollable_frame, text="Bio:", font=("Arial", 14))
    bio_label.pack(pady=10, anchor="w")

    bio_text = tk.Label(scrollable_frame, text=user_info.get("bio", "No bio available."), wraplength=300, justify="left")
    bio_text.pack(pady=10, anchor="w")

    # Add Friend button
    if username != current_user and username not in friends.get(current_user, []):
        def send_request():
            result = send_friend_request(current_user, username)
            messagebox.showinfo("Friend Request", result)

        add_friend_button = tk.Button(scrollable_frame, text="Add Friend", command=send_request)
        add_friend_button.pack(pady=10)

    # Recent uploads
    recent_uploads_label = tk.Label(scrollable_frame, text="Recent Uploads:", font=("Arial", 14))
    recent_uploads_label.pack(pady=10, anchor="w")

    recent_uploads_listbox = tk.Listbox(scrollable_frame, height=10, width=50)
    recent_uploads_listbox.pack(pady=10, anchor="w")

    # Define the sort button before using it
    sort_button_user_uploads = tk.Button(scrollable_frame, text="Sort By")
    sort_button_user_uploads.pack(pady=5)

    # Populate recent uploads in the user profile
    try:
        response = requests.get(f"{SERVER_URL}/user_uploads", params={"username": username})
        if response.status_code == 200:
            uploads = response.json().get("uploads", [])
            file_list = [
                {"name": upload['name'], "downloads": upload.get('downloads', 0), "size": upload.get('size', 0), "upload_time": upload.get('upload_time', 0)}
                for upload in uploads
            ]
            recent_uploads_listbox.delete(0, tk.END)
            for file in file_list:
                recent_uploads_listbox.insert(
                    tk.END,
                    f"{file['name']} | Downloads: {file['downloads']} | Size: {file['size']} bytes | Uploaded: {time.ctime(file['upload_time'])}"
                )

            # Attach the "Sort By" menu to the Recent User Uploads section
            create_sort_by_menu(file_list, recent_uploads_listbox, sort_button_user_uploads)
        else:
            print(f"Failed to fetch uploads for {username}: {response.status_code}")
    except Exception as e:
        print(f"Error fetching uploads for {username}: {e}")

    # Add double-click functionality to download files
    def on_file_double_click(event):
        try:
            selected_file = recent_uploads_listbox.get(recent_uploads_listbox.curselection()).split(" | ")[0]
            download_file(selected_file)
        except Exception as e:
            print(f"Error handling double-click: {e}")

    recent_uploads_listbox.bind("<Double-1>", on_file_double_click)

    # Add right-click menu for additional options
    def on_right_click(event):
        try:
            selected_file = recent_uploads_listbox.get(recent_uploads_listbox.curselection())
            parts = selected_file.split(" | ")
            if len(parts) < 2:
                raise ValueError("Invalid file entry format")
            file_name = parts[0]

            menu = tk.Menu(profile_window, tearoff=0)
            menu.add_command(label="Download", command=lambda: download_file(file_name))
            menu.add_command(label="Set as Profile Picture", command=lambda: set_profile_picture(current_user, file_name))
            menu.add_command(label="Report", command=lambda: messagebox.showinfo("Report", "Feature coming soon!"))
            menu.post(event.x_root, event.y_root)
        except Exception as e:
            print(f"Error handling right-click: {e}")

    recent_uploads_listbox.bind("<Button-3>", on_right_click)

    # Friends
    friends_label = tk.Label(scrollable_frame, text="Friends:", font=("Arial", 14))
    friends_label.pack(pady=10, anchor="w")

    friends_listbox = tk.Listbox(scrollable_frame, height=10, width=50)
    friends_listbox.pack(pady=10, anchor="w")

    # Populate friends list
    try:
        response = requests.get(f"{SERVER_URL}/friends", params={"username": username})
        if response.status_code == 200:
            friends_list = response.json().get("friends", [])
            for friend in friends_list:
                friends_listbox.insert(tk.END, friend)
        else:
            print(f"Failed to fetch friends for {username}: {response.status_code}")
    except Exception as e:
        print(f"Error fetching friends for {username}: {e}")

def show_profile_settings(username):
    # Fetch user data from the server
    user_info = get_user_data(username)
    if not user_info:
        messagebox.showerror("Error", "User not found.")
        return

    # Create the settings window
    settings_window = tk.Toplevel(root)
    settings_window.title("User Settings")
    settings_window.geometry("400x600")

    # Create a scrollable frame
    scrollable_frame = make_scrollable_window(settings_window)

    # Profile Picture Section
    profile_icon_label = tk.Label(scrollable_frame, text="[Profile Icon]", font=("Arial", 20), bg="gray")
    profile_icon_label.pack(pady=10)

    def update_profile_picture():
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            try:
                # Upload the new profile picture to the server
                with open(file_path, 'rb') as f:
                    response = requests.post(
                        f"{SERVER_URL}/upload_profile_picture",
                        files={"file": f},
                        data={"username": username}
                    )
                if response.json().get("success"):
                    update_profile_icon(username, profile_icon_label)
                    messagebox.showinfo("Success", "Profile picture updated successfully!")
                else:
                    messagebox.showerror("Error", "Failed to update profile picture.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload profile picture: {e}")

    # Load the current profile picture
    update_profile_icon(username, profile_icon_label)

    change_icon_button = tk.Button(scrollable_frame, text="Change Profile Picture", command=update_profile_picture)
    change_icon_button.pack(pady=5)

    # Bio Section
    bio_label = tk.Label(scrollable_frame, text="Bio:", font=("Arial", 14))
    bio_label.pack(pady=10)

    bio_entry = tk.Text(scrollable_frame, height=5, width=40)
    bio_entry.insert("1.0", user_info.get("bio", ""))  # Load existing bio
    bio_entry.pack(pady=10)

    def save_bio():
        bio = bio_entry.get("1.0", tk.END).strip()
        if len(bio) > 256:
            messagebox.showerror("Error", "Bio cannot exceed 256 characters.")
        else:
            try:
                response = requests.post(f"{SERVER_URL}/update_bio", json={"username": username, "bio": bio})
                if response.json().get("success"):
                    messagebox.showinfo("Success", "Bio updated successfully!")
                else:
                    messagebox.showerror("Error", "Failed to update bio.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update bio: {e}")

    save_bio_button = tk.Button(scrollable_frame, text="Save Bio", command=save_bio)
    save_bio_button.pack(pady=5)

    # Friends List Section
    friends_label = tk.Label(scrollable_frame, text="Friends:", font=("Arial", 14))
    friends_label.pack(pady=10)

    friends_listbox = tk.Listbox(scrollable_frame, height=10, width=50)
    friends_listbox.pack(pady=10)

    # Populate the friends list
    try:
        response = requests.get(f"{SERVER_URL}/friends", params={"username": username})
        if response.status_code == 200:
            friends_list = response.json().get("friends", [])
            for friend in friends_list:
                friends_listbox.insert(tk.END, friend)
        else:
            messagebox.showerror("Error", f"Failed to fetch friends: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch friends: {e}")

    def remove_friend():
        try:
            selected_friend = friends_listbox.get(friends_listbox.curselection())
            response = requests.post(f"{SERVER_URL}/remove_friend", json={"username": username, "friend": selected_friend})
            if response.json().get("success"):
                friends_listbox.delete(friends_listbox.curselection())
                messagebox.showinfo("Success", f"{selected_friend} removed from friends.")
            else:
                messagebox.showerror("Error", "Failed to remove friend.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove friend: {e}")

    remove_friend_button = tk.Button(scrollable_frame, text="Remove Friend", command=remove_friend)
    remove_friend_button.pack(pady=5)

def make_scrollable_window(window):
    canvas = tk.Canvas(window)
    scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return scrollable_frame

def create_sort_by_menu(file_list, listbox, sort_button):
    """
    Creates a "Sort By" menu for sorting files displayed in a Listbox.

    Args:
        file_list (list): A list of dictionaries containing file metadata.
                          Example: [{"name": "file1", "downloads": 10, "size": 1024, "upload_time": 1683072000}, ...]
        listbox (tk.Listbox): The Listbox widget displaying the files.
        sort_button (tk.Button): The button that triggers the "Sort By" menu.
    """
    def sort_files(criteria, reverse=False):
        # Sort the file list based on the selected criteria
        if criteria == "downloads":
            file_list.sort(key=lambda x: x["downloads"], reverse=reverse)
        elif criteria == "size":
            file_list.sort(key=lambda x: x["size"], reverse=reverse)
        elif criteria == "upload_time":
            file_list.sort(key=lambda x: x["upload_time"], reverse=reverse)

        # Update the Listbox with the sorted files
        listbox.delete(0, tk.END)
        for file in file_list:
            listbox.insert(
                tk.END,
                f"{file['name']} | Downloads: {file['downloads']} | Size: {file['size']} bytes | Uploaded: {time.ctime(file['upload_time'])}"
            )

    # Create the "Sort By" menu
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Downloads (Most)", command=lambda: sort_files("downloads", reverse=True))
    menu.add_command(label="Downloads (Least)", command=lambda: sort_files("downloads", reverse=False))
    menu.add_command(label="Size (Biggest to Smallest)", command=lambda: sort_files("size", reverse=True))
    menu.add_command(label="Size (Smallest to Biggest)", command=lambda: sort_files("size", reverse=False))
    menu.add_command(label="Age (Oldest to Newest)", command=lambda: sort_files("upload_time", reverse=False))
    menu.add_command(label="Age (Newest to Oldest)", command=lambda: sort_files("upload_time", reverse=True))

    # Bind the menu to the "Sort By" button
    def show_menu(event):
        menu.post(event.x_root, event.y_root)

    sort_button.bind("<Button-1>", show_menu)

def display_files_with_sort(username):
    # Fetch file metadata from the server
    file_metadata = fetch_file_metadata()
    file_list = [
        {"name": name, **metadata}
        for name, metadata in file_metadata.items()
    ]

    # Create a new window to display files
    file_window = tk.Toplevel(root)
    file_window.title("Files")
    file_window.geometry("600x400")

    # Create a Listbox to display files
    file_listbox = tk.Listbox(file_window, height=15, width=80)
    file_listbox.pack(pady=10)

    # Populate the Listbox with initial file data
    for file in file_list:
        file_listbox.insert(
            tk.END,
            f"{file['name']} | Downloads: {file['downloads']} | Size: {file['size']} bytes | Uploaded: {time.ctime(file['upload_time'])}"
        )

    # Create the "Sort By" button
    sort_button = tk.Button(file_window, text="Sort By")
    sort_button.pack(pady=5)

    # Attach the "Sort By" menu to the button
    create_sort_by_menu(file_list, file_listbox, sort_button)

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

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in the request"}), 400
    file = request.files['file']
    username = request.form.get('username')
    if not file or not username:
        return jsonify({"success": False, "message": "Missing file or username"}), 400

    # Save the file in the profile_icons directory
    profile_icons_path = os.path.join(os.getcwd(), 'profile_icons')
    os.makedirs(profile_icons_path, exist_ok=True)  # Ensure the directory exists
    file_path = os.path.join(profile_icons_path, f"{username}_profile.png")
    file.save(file_path)

    return jsonify({"success": True, "message": "Profile picture uploaded successfully"})

# Load data on startup
load_data()

# Run the GUI
create_gui()
