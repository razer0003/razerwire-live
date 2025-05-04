from flask import Blueprint, request, jsonify
from server.models.user import User
from server.utils.validation import validate_message
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# In-memory chat log for demonstration purposes
chat_log = []

@chat_bp.route('/chat/send', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('username')
    message = data.get('message')

    if not validate_message(message):
        return jsonify({'error': 'Invalid message'}), 400

    timestamp = datetime.now().isoformat()
    chat_entry = {'username': username, 'message': message, 'timestamp': timestamp}
    chat_log.append(chat_entry)

    return jsonify({'success': True, 'message': 'Message sent successfully'}), 200

@chat_bp.route('/chat/messages', methods=['GET'])
def get_messages():
    return jsonify(chat_log), 200