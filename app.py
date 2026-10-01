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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            daily_goal INTEGER NOT NULL
        )
    """)
    conn.execute("""
        INSERT OR IGNORE INTO settings (id, daily_goal) VALUES (1, 2000)
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

@app.route("/today")
def today_total():
    conn = sqlite3.connect("hydra.db")
    cursor = conn.execute("SELECT SUM(amount) FROM water_log WHERE date(timestamp) = date('now')")
    result = cursor.fetchone()
    conn.close()
    
    total = result[0] if result[0] is not None else 0
    return f"Today's total: {total}ml"
@app.route("/progress")
def progress():
    conn = sqlite3.connect("hydra.db")
    
    today_cursor = conn.execute("SELECT SUM(amount) FROM water_log WHERE date(timestamp) = date('now')")
    today_result = today_cursor.fetchone()
    today_total = today_result[0] if today_result[0] is not None else 0
    
    goal_cursor = conn.execute("SELECT daily_goal FROM settings WHERE id = 1")
    goal_result = goal_cursor.fetchone()
    daily_goal = goal_result[0]
    
    conn.close()
    
    percentage = round((today_total / daily_goal) * 100, 1)
    
    return f"Progress: {today_total}ml / {daily_goal}ml ({percentage}%)"

if __name__ == "__main__":
    app.run(debug=True)