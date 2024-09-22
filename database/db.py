import json

DB_FILE = 'bot_data.json'

def save_data(data):
    with open(DB_FILE, 'w') as file:
        json.dump(data, file)


def load_data():
    try:
        with open(DB_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"users": [], "history": []}



def load_data_mail():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}}

def save_data_mail(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)


def load_template_texts():
    with open('texts.json', 'r') as f:
        return json.load(f)