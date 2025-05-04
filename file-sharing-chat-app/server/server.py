from flask import Flask, request, jsonify
import os
import pickle
import time
import requests
from tkinter import filedialog, messagebox

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit

# Paths for data storage
USER_DATA_PATH = 'user_data.pkl'
FILE_STORAGE_PATH = 'file_storage.pkl'
CHAT_LOG_PATH = 'chat_log.pkl'

# Load or initialize data
if os.path.exists(USER_DATA_PATH):
    with open(USER_DATA_PATH, 'rb') as f:
        user_data = pickle.load(f)
else:
    user_data = {}

if os.path.exists(FILE_STORAGE_PATH):
    with open(FILE_STORAGE_PATH, 'rb') as f:
        file_storage = pickle.load(f)
else:
    file_storage = {}

if os.path.exists(CHAT_LOG_PATH):
    with open(CHAT_LOG_PATH, 'rb') as f:
        chat_log = pickle.load(f)
else:
    chat_log = []

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
    if username in user_data:
        return jsonify({"success": False, "message": "Username already exists"})
    user_data[username] = {"password": password, "profile_icon": None, "bio": "", "friends": []}
    with open(USER_DATA_PATH, 'wb') as f:
        pickle.dump(user_data, f)
    return jsonify({"success": True, "message": "User registered successfully"})

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
            'size': os.path.getsize(upload_path)
        }
        with open(FILE_STORAGE_PATH, 'wb') as f:
            pickle.dump(file_storage, f)
        return jsonify({"success": True, "message": "File uploaded successfully"})
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({"success": False, "message": "Failed to save file"}), 500

@app.route('/recent_uploads', methods=['GET'])
def recent_uploads():
    recent_files = sorted(file_storage.items(), key=lambda x: x[1]['upload_time'], reverse=True)[:10]
    return jsonify([
        {
            "name": file_name,
            "username": metadata['username'],
            "upload_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(metadata['upload_time'])),
            "size": metadata['size']
        }
        for file_name, metadata in recent_files
    ])

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
    if not username or not message:
        return jsonify({"success": False, "message": "Missing username or message"}), 400
    chat_log.append((username, message, time.time()))
    with open(CHAT_LOG_PATH, 'wb') as f:
        pickle.dump(chat_log, f)
    return jsonify({"success": True, "message": "Message sent"})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify([
        {
            "username": log[0],
            "message": log[1],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log[2]))
        }
        for log in chat_log[-10:]  # Return the last 10 messages
    ])

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)