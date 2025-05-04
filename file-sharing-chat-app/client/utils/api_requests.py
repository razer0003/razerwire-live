import requests

BASE_URL = "http://localhost:5000"  # Adjust the base URL as needed

def register_user(username, password):
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    return response.json()

def login_user(username, password):
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    return response.json()

def upload_file(username, file_path):
    with open(file_path, 'rb') as file:
        response = requests.post(f"{BASE_URL}/upload", files={"file": file}, data={"username": username})
    return response.json()

def download_file(file_name):
    response = requests.get(f"{BASE_URL}/download/{file_name}")
    if response.status_code == 200:
        with open(file_name, 'wb') as file:
            file.write(response.content)
        return {"message": "File downloaded successfully."}
    return response.json()

def send_chat_message(username, message):
    response = requests.post(f"{BASE_URL}/chat/send", json={"username": username, "message": message})
    return response.json()

def get_chat_messages():
    response = requests.get(f"{BASE_URL}/chat/messages")
    return response.json()