from requests import post, get

BASE_URL = "http://127.0.0.1:5000"  # Change this if your Flask server runs on a different address

def register_user(username, password):
    response = post(f"{BASE_URL}/register", json={"username": username, "password": password})
    return response.json()

def login_user(username, password):
    response = post(f"{BASE_URL}/login", json={"username": username, "password": password})
    return response.json()

def upload_file(username, file_path):
    with open(file_path, 'rb') as file:
        response = post(f"{BASE_URL}/upload", files={"file": file}, data={"username": username})
    return response.json()

def download_file(file_id):
    response = get(f"{BASE_URL}/download/{file_id}")
    if response.status_code == 200:
        with open(file_id, 'wb') as file:
            file.write(response.content)
        return {"success": True, "message": "File downloaded successfully."}
    return response.json()

def send_chat_message(username, message):
    response = post(f"{BASE_URL}/chat/send", json={"username": username, "message": message})
    return response.json()

def get_chat_messages():
    response = get(f"{BASE_URL}/chat/messages")
    return response.json()