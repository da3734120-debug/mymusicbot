import os
import json
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home(): 
    return "Bot XO Online 24/7!"

def run_web_server():
    port = int(os.getenv("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive(): 
    Thread(target=run_web_server).start()

DATA_FILE = "/data/balances.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(user_balances):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(user_balances, f, indent=4)

def format_number(num):
    return "{:,}".format(num)

def draw_board(board):
    lines = []
    for i in range(0, 9, 3):
        lines.append(f"{board[i]} | {board[i+1]} | {board[i+2]}")
    return "\n---------\n".join(lines)

def check_winner(b):
    for i in range(0, 9, 3):
        if b[i] == b[i+1] == b[i+2] != "⬜": return b[i]
    for i in range(3):
        if b[i] == b[i+3] == b[i+6] != "⬜": return b[i]
    if b[0] == b[4] == b[8] != "⬜": return b[0]
    if b[2] == b[4] == b[6] != "⬜": return b[2]
    if "⬜" not in b: return "Tie"
    return None
