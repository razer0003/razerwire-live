def validate_username(username):
    if len(username) < 3 or len(username) > 20:
        return False
    if not username.isalnum():
        return False
    return True

def validate_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True

def validate_file_upload(file):
    if not file:
        return False
    if file.content_type not in ['image/jpeg', 'image/png', 'application/pdf', 'application/zip']:
        return False
    return True

def validate_chat_message(message):
    if len(message) == 0 or len(message) > 500:
        return False
    return True