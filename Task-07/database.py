import sqlite3

DB_NAME = "berrybroker.db"
STARTING_BALANCE = 500

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 500,
            last_daily TEXT,
            last_rob TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_user(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (str(user_id),))
    row = cursor.fetchone()

    if row is None:
        cursor.execute(
            "INSERT INTO users (user_id, username, balance, last_daily, last_rob) "
            "VALUES (?, ?, ?, NULL, NULL)",
            (str(user_id), username, STARTING_BALANCE)
        )
        conn.commit()
        row = (str(user_id), username, STARTING_BALANCE, None, None)
    else:
        cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (username, str(user_id)))
        conn.commit()

    conn.close()
    return row


def get_balance(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (str(user_id),))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return STARTING_BALANCE
    return row[0]


def update_balance(user_id, new_balance):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, str(user_id)))
    conn.commit()
    conn.close()


def add_to_balance(user_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, str(user_id)))
    conn.commit()
    conn.close()


def set_last_daily(user_id, timestamp):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_daily = ? WHERE user_id = ?", (timestamp, str(user_id)))
    conn.commit()
    conn.close()


def set_last_rob(user_id, timestamp):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_rob = ? WHERE user_id = ?", (timestamp, str(user_id)))
    conn.commit()
    conn.close()


def get_top_users(limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows