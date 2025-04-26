# login_utils.py

users = {
    "frontdesk": {"password": "fd123", "role": "frontdesk"},
    "doctor": {"password": "doc123", "role": "doctor"}
}

def validate_login(username, password):
    user = users.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None
