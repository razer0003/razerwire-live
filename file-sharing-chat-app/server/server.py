from flask import Flask, request, jsonify, send_file
import os
import pickle
import time
import requests
from PIL import Image  # Import the Image module from PIL

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Paths for data storage
USER_DATA_PATH = 'user_data.pkl'
FILE_STORAGE_PATH = 'file_storage.pkl'
CHAT_LOG_PATH = 'chat_log.pkl'
FRIEND_REQUESTS_PATH = 'friend_requests.pkl'
FRIENDS_PATH = 'friends.pkl'  # Add this near the other file paths
SERVER_URL = "http://192.168.1.59:5000"

app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1 GB limit

user_data = {}  # Ensure this is defined globally in the server
friends = {}  # Initialize an empty dictionary for friends

def save_data():
    try:
        with open(USER_DATA_PATH, 'wb') as f:
            pickle.dump(user_data, f)
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    global user_data
    if os.path.exists(USER_DATA_PATH):
        try:
            with open(USER_DATA_PATH, 'rb') as f:
                user_data = pickle.load(f)
        except Exception as e:
            print(f"Error loading user data: {e}")
            user_data = {}

def cleanup_file_storage():
    global file_storage
    upload_dir = 'uploads'
    valid_files = set(os.listdir(upload_dir))

    # Remove metadata for files that no longer exist
    invalid_files = [file_name for file_name in file_storage if file_name not in valid_files]
    for file_name in invalid_files:
        print(f"Removing metadata for missing file: {file_name}")  # Debugging line
        del file_storage[file_name]

    # Save the updated file_storage back to disk
    with open(FILE_STORAGE_PATH, 'wb') as f:
        pickle.dump(file_storage, f)

# Load or initialize data
load_data()

# Initialize file_storage before cleanup
if os.path.exists(FILE_STORAGE_PATH):
    with open(FILE_STORAGE_PATH, 'rb') as f:
        file_storage = pickle.load(f)
else:
    file_storage = {}

# Perform cleanup after initializing file_storage
cleanup_file_storage()

if os.path.exists(CHAT_LOG_PATH):
    with open(CHAT_LOG_PATH, 'rb') as f:
        chat_log = pickle.load(f)
else:
    chat_log = []

if os.path.exists(FRIEND_REQUESTS_PATH):
    with open(FRIEND_REQUESTS_PATH, 'rb') as f:
        friend_requests = pickle.load(f)
else:
    friend_requests = {}

# Load friends data
if os.path.exists(FRIENDS_PATH):
    with open(FRIENDS_PATH, 'rb') as f:
        friends = pickle.load(f)
else:
    friends = {}  # Initialize as an empty dictionary if the file doesn't exist

# User authentication

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in user_data and user_data[username]['password'] == password:
        return jsonify({"success": True, "message": "Login successful"})
    return jsonify({"success": False, "message": "Invalid credentials"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    if username in user_data:
        return jsonify({"message": "User already exists"}), 400
    user_data[username] = {
        "password": password,  # Hash the password in production
        "profile_icon": "person_icon.png",
        "bio": "",
        "friends": []
    }
    save_data()  # Save the updated user data
    return jsonify({"message": "User registered successfully"}), 200

# File upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in the request"}), 400
    file = request.files['file']
    username = request.form.get('username')
    if not file or not username:
        return jsonify({"success": False, "message": "Missing file or username"}), 400
    
    # Ensure the uploads directory exists
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    upload_path = os.path.join(upload_dir, file.filename)
    try:
        file.save(upload_path)
        file_storage[file.filename] = {
            'username': username,
            'upload_time': time.time(),
            'size': os.path.getsize(upload_path),
            'downloads': 0  # Initialize download count
        }
        with open(FILE_STORAGE_PATH, 'wb') as f:
            pickle.dump(file_storage, f)
        return jsonify({"success": True, "message": "File uploaded successfully"})
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({"success": False, "message": "Failed to save file"}), 500

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part in the request"}), 400
    file = request.files['file']
    username = request.form.get('username')
    if not file or not username:
        return jsonify({"success": False, "message": "Missing file or username"}), 400

    # Save the file temporarily
    temp_path = os.path.join('profile_icons', f"temp_{username}.png")
    os.makedirs('profile_icons', exist_ok=True)
    file.save(temp_path)

    try:
        # Open the image and crop it to a 1:1 aspect ratio
        image = Image.open(temp_path)
        width, height = image.size
        if width != height:
            min_dim = min(width, height)
            image = image.crop((
                (width - min_dim) // 2,
                (height - min_dim) // 2,
                (width + min_dim) // 2,
                (height + min_dim) // 2
            ))

        # Resize to 512x512
        image = image.resize((512, 512), Image.Resampling.LANCZOS)

        # Save the processed image
        file_path = os.path.join('profile_icons', f"{username}_profile.png")
        image.save(file_path)

        # Clean up the temporary file
        os.remove(temp_path)

        return jsonify({"success": True, "message": "Profile picture uploaded and processed successfully"})
    except Exception as e:
        print(f"Error processing profile picture: {e}")
        return jsonify({"success": False, "message": "Failed to process profile picture"}), 500

@app.route('/profile_picture/<username>', methods=['GET'])
def get_profile_picture(username):
    profile_icons_path = os.path.join(os.getcwd(), 'profile_icons')
    file_path = os.path.join(profile_icons_path, f"{username}_profile.png")
    
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/png')
    else:
        return jsonify({"success": False, "message": "Profile picture not found"}), 404

@app.route('/set_profile_picture', methods=['POST'])
def set_profile_picture():
    data = request.json
    username = data.get('username')
    file_name = data.get('file_name')

    if not username or not file_name:
        return jsonify({"success": False, "message": "Missing username or file name"}), 400

    # Path to the uploaded file
    upload_path = os.path.join('uploads', file_name)
    if not os.path.exists(upload_path):
        return jsonify({"success": False, "message": "File not found on the server"}), 404

    try:
        # Open the image and crop it to a 1:1 aspect ratio
        image = Image.open(upload_path)
        width, height = image.size
        if width != height:
            min_dim = min(width, height)
            image = image.crop((
                (width - min_dim) // 2,
                (height - min_dim) // 2,
                (width + min_dim) // 2,
                (height + min_dim) // 2
            ))

        # Resize to 512x512
        image = image.resize((512, 512), Image.Resampling.LANCZOS)

        # Save the processed image as the user's profile picture
        profile_icons_path = os.path.join(os.getcwd(), 'profile_icons')
        os.makedirs(profile_icons_path, exist_ok=True)  # Ensure the directory exists
        profile_picture_path = os.path.join(profile_icons_path, f"{username}_profile.png")
        image.save(profile_picture_path)

        return jsonify({"success": True, "message": "Profile picture updated successfully"})
    except Exception as e:
        print(f"Error processing profile picture: {e}")
        return jsonify({"success": False, "message": "Failed to process profile picture"}), 500

@app.route('/recent_uploads', methods=['GET'])
def recent_uploads():
    # Ensure file metadata is up-to-date
    upload_dir = 'uploads'
    valid_files = set(os.listdir(upload_dir))

    # Remove metadata for files that no longer exist
    invalid_files = [file_name for file_name in file_storage if file_name not in valid_files]
    for file_name in invalid_files:
        print(f"Removing metadata for missing file: {file_name}")
        del file_storage[file_name]

    # Add metadata for new files in the uploads directory
    for file_name in valid_files:
        if file_name not in file_storage:
            file_path = os.path.join(upload_dir, file_name)
            file_storage[file_name] = {
                'username': 'unknown',  # Default username if not provided
                'upload_time': os.path.getmtime(file_path),
                'size': os.path.getsize(file_path),
                'downloads': 0
            }

    # Save the updated file_storage back to disk
    with open(FILE_STORAGE_PATH, 'wb') as f:
        pickle.dump(file_storage, f)

    # Return the file metadata
    return jsonify({"files": [
        {"name": name, **metadata}
        for name, metadata in file_storage.items()
    ]})

@app.route('/download/<file_name>', methods=['GET'])
def download_file(file_name):
    file_path = os.path.join('uploads', file_name)
    if os.path.exists(file_path):
        return app.send_static_file(file_path)
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/download/nofile.png')
def serve_nofile():
    return app.send_static_file('nofile.png')  # Ensure 'nofile.png' is in the static directory

@app.route('/uploads/<file_name>', methods=['GET'])
def serve_uploaded_file(file_name):
    """
    Serve files from the 'uploads' directory.
    """
    file_path = os.path.join('uploads', file_name)
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/user_uploads', methods=['GET'])
def user_uploads():
    username = request.args.get('username')
    if not username:
        return jsonify({"success": False, "message": "Missing username"}), 400

    user_files = [
        {"name": name, **metadata}
        for name, metadata in file_storage.items()
        if metadata['username'] == username
    ]
    return jsonify({"success": True, "uploads": user_files})

@app.route('/file_metadata', methods=['GET'])
def get_file_metadata():
    return jsonify({"success": True, "files": file_storage})

# Chat messages
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        message = data.get('message')
        chat_log.append((username, message, time.time()))
        with open(CHAT_LOG_PATH, 'wb') as f:
            pickle.dump(chat_log, f)
        return jsonify({"success": True, "message": "Message sent"})
    elif request.method == 'GET':
        return jsonify(chat_log[-10:])  # Return the last 10 messages

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('username')
    message = data.get('message')
    chat_log.append((username, message, time.time()))  # Append as a tuple
    with open(CHAT_LOG_PATH, 'wb') as f:
        pickle.dump(chat_log, f)
    return jsonify({"success": True, "message": "Message sent"})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    formatted_chat_log = []
    for entry in chat_log:
        if isinstance(entry, (list, tuple)) and len(entry) == 3:
            formatted_chat_log.append({
                "username": entry[0],
                "message": entry[1],
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry[2]))
            })
        else:
            print(f"Invalid chat log entry: {entry}")  # Debugging line
    return jsonify(formatted_chat_log)

@app.route('/friends', methods=['GET'])
def get_friends():
    username = request.args.get('username')
    if username in user_data:
        return jsonify({"friends": user_data[username].get("friends", [])})
    return jsonify({"friends": []})

@app.route('/add_friend', methods=['POST'])
def add_friend():
    data = request.json
    username = data.get('username')
    friend = data.get('friend')
    if username in user_data and friend in user_data:
        if friend not in user_data[username]["friends"]:
            user_data[username]["friends"].append(friend)
            user_data[friend]["friends"].append(username)
            save_data()
            return jsonify({"success": True, "message": f"{friend} added as a friend"})
    return jsonify({"success": False, "message": "Failed to add friend"})

@app.route('/remove_friend', methods=['POST'])
def remove_friend():
    data = request.json
    username = data.get('username')
    friend = data.get('friend')
    if username in user_data and friend in user_data:
        if friend in user_data[username]["friends"]:
            user_data[username]["friends"].remove(friend)
            user_data[friend]["friends"].remove(username)
            save_data()
            return jsonify({"success": True, "message": f"{friend} removed from friends"})
    return jsonify({"success": False, "message": "Failed to remove friend"})

@app.route('/update_bio', methods=['POST'])
def update_bio():
    data = request.json
    username = data.get('username')
    bio = data.get('bio')
    if username in user_data:
        user_data[username]['bio'] = bio
        save_data()  # Save the updated user data
        return jsonify({"success": True, "message": "Bio updated successfully"})
    return jsonify({"success": False, "message": "User not found"}), 404

@app.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    data = request.json
    from_user = data.get('from_user')
    to_user = data.get('to_user')
    if to_user in user_data:
        friend_requests.setdefault(to_user, []).append(from_user)
        with open(FRIEND_REQUESTS_PATH, 'wb') as f:
            pickle.dump(friend_requests, f)
        return jsonify({"success": True, "message": "Friend request sent"})
    return jsonify({"success": False, "message": "User not found"}), 404

@app.route('/friend_requests', methods=['GET'])
def get_friend_requests():
    username = request.args.get('username')
    if username in friend_requests:
        return jsonify({"requests": friend_requests[username]})
    return jsonify({"requests": []})  # Return an empty list if no requests exist

@app.route('/accept_friend_request', methods=['POST'])
def accept_friend_request():
    data = request.json
    user = data.get('user')  # The user accepting the request
    friend = data.get('friend')  # The user who sent the request

    if user in friend_requests and friend in friend_requests[user]:
        # Add each other as friends
        user_data[user]["friends"].append(friend)
        user_data[friend]["friends"].append(user)

        # Remove the friend request
        friend_requests[user].remove(friend)
        if not friend_requests[user]:  # Clean up empty lists
            del friend_requests[user]

        # Save the updated data
        save_data()
        with open(FRIEND_REQUESTS_PATH, 'wb') as f:
            pickle.dump(friend_requests, f)

        return jsonify({"success": True, "message": f"Friend request from {friend} accepted"})
    return jsonify({"success": False, "message": "Friend request not found"}), 404

@app.route('/all_users', methods=['GET'])
def all_users():
    return jsonify({"users": list(user_data.keys())})

@app.route('/user_data/<username>', methods=['GET'])
def get_user_data(username):
    user = user_data.get(username)
    if user:
        return jsonify(user)
    return jsonify({"success": False, "message": "User not found"}), 404

@app.route('/user_friends', methods=['GET'])
def user_friends():
    username = request.args.get('username')
    if not username:
        return jsonify({"success": False, "message": "Missing username"}), 400

    user_friends = friends.get(username, [])
    return jsonify({"success": True, "friends": user_friends})

def upload_file_client(username, file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(
            f"{SERVER_URL}/upload",
            files={'file': f},
            data={'username': username}
        )
    print("Raw response:", response.text)  # Debugging: Print the raw response
    try:
        return response.json().get('message', "Error")
    except requests.exceptions.JSONDecodeError:
        return f"Server returned invalid response: {response.text}"

def upload_file_action():
    file_path = filedialog.askopenfilename()  # Use filedialog here
    if file_path:
        result = upload_file_client(username, file_path)  # Call the renamed function
        messagebox.showinfo("Upload Result", result)

def get_friends(username):
    response = requests.get(f"{SERVER_URL}/friends", params={"username": username})
    return response.json().get("friends", [])

def update_bio(username, bio):
    response = requests.post(f"{SERVER_URL}/update_bio", json={"username": username, "bio": bio})
    return response.json().get("message", "Error")

if __name__ == "__main__":
    load_data()
    app.run(host="0.0.0.0", port=5000)