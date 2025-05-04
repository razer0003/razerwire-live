from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from server.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required.'}), 400

    if User.find_by_username(username):
        return jsonify({'message': 'Username already exists.'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    new_user.save()

    return jsonify({'message': 'User registered successfully.'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.find_by_username(username)
    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful.'}), 200

    return jsonify({'message': 'Invalid username or password.'}), 401