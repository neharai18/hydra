from datetime import datetime
from flask import Flask
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("hydra.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS water_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount INTEGER NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return "HYDRA is running!"

@app.route("/log/<int:amount>")
def log_water(amount):
    conn = sqlite3.connect("hydra.db")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO water_log (amount, timestamp) VALUES (?, ?)", (amount, timestamp))
    conn.commit()
    conn.close()
    return f"Logged {amount}ml at {timestamp}"

if __name__ == "__main__":
    app.run(debug=True)