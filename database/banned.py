import json
import os

BANNED_FILE = 'banned.json'

def load_banned_users():
    if os.path.exists(BANNED_FILE):
        with open(BANNED_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_banned_users(banned_users):
    with open(BANNED_FILE, 'w') as f:
        json.dump(banned_users, f, indent=4)

def ban_user(user_id):
    banned_users = load_banned_users()
    banned_users[str(user_id)] = True
    save_banned_users(banned_users)

def unban_user(user_id):
    banned_users = load_banned_users()
    if str(user_id) in banned_users:
        del banned_users[str(user_id)]
        save_banned_users(banned_users)


def is_user_banned(user_id):
    banned_users = load_banned_users()
    return str(user_id) in banned_users
