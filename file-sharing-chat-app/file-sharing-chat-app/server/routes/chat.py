from flask import Blueprint, request, jsonify
from server.models.user import User
from server.utils.validation import validate_message
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# In-memory storage for chat messages (for demonstration purposes)
chat_logs = []

@chat_bp.route('/chat/send', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('username')
    message = data.get('message')

    if not username or not message:
        return jsonify({"error": "Username and message are required."}), 400

    if not validate_message(message):
        return jsonify({"error": "Invalid message."}), 400

    timestamp = datetime.now().isoformat()
    chat_logs.append({"username": username, "message": message, "timestamp": timestamp})

    return jsonify({"success": True, "message": "Message sent."}), 200

@chat_bp.route('/chat/retrieve', methods=['GET'])
def retrieve_messages():
    return jsonify(chat_logs), 200

@chat_bp.route('/chat/clear', methods=['DELETE'])
def clear_chat():
    global chat_logs
    chat_logs = []
    return jsonify({"success": True, "message": "Chat cleared."}), 200