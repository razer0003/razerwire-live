def validate_username(username):
    if not username or len(username) < 3 or len(username) > 20:
        return False
    return True

def validate_password(password):
    if not password or len(password) < 6:
        return False
    return True

def validate_file_upload(file):
    if not file:
        return False
    return True

def validate_chat_message(message):
    if not message or len(message) > 500:
        return False
    return True