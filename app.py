from datetime import datetime
from flask import Flask, render_template
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
def calculate_streak():
    conn = sqlite3.connect("hydra.db")
    goal = conn.execute("SELECT daily_goal FROM settings WHERE id = 1").fetchone()[0]
    
    streak = 0
    day_offset = 0
    
    while True:
        cursor = conn.execute(
            "SELECT SUM(amount) FROM water_log WHERE date(timestamp) = date('now', ?)",
            (f'-{day_offset} days',)
        )
        total = cursor.fetchone()[0]
        total = total if total is not None else 0
        
        if total >= goal:
            streak += 1
            day_offset += 1
        else:
            break
    
    conn.close()
    return streak   

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

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("hydra.db")
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    today_date = datetime.now().strftime("%a, %d %b")
    
    today_cursor = conn.execute("SELECT SUM(amount) FROM water_log WHERE date(timestamp) = date('now')")
    today_result = today_cursor.fetchone()
    today_total = today_result[0] if today_result[0] is not None else 0
    
    goal_cursor = conn.execute("SELECT daily_goal FROM settings WHERE id = 1")
    daily_goal = goal_cursor.fetchone()[0]
    
    week_cursor = conn.execute("""
        SELECT date(timestamp) as day, SUM(amount) as total
        FROM water_log
        WHERE date(timestamp) >= date('now', '-6 days')
        GROUP BY date(timestamp)
        ORDER BY day
    """)
    week_data = {row[0]: row[1] for row in week_cursor.fetchall()}
    from datetime import timedelta
    last_7_days = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        day_label = (datetime.now() - timedelta(days=i)).strftime("%a")
        amount = week_data.get(day, 0)
        last_7_days.append({"label": day_label, "amount": amount})
    streak = calculate_streak()
    conn.close()
    
    percentage = round((today_total / daily_goal) * 100, 1)
    
    return render_template("dashboard.html", today_total=today_total, daily_goal=daily_goal, percentage=percentage, week_data=week_data, greeting=greeting, today_date=today_date, streak=streak, last_7_days=last_7_days)
if __name__ == "__main__":
    app.run(debug=True)