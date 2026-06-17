import sqlite3

DATABASE = "website_blocker.db"


def create_database():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    # -----------------------------
    # Blocked Websites Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_websites (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            website TEXT UNIQUE NOT NULL

        )
    """)

    # -----------------------------
    # History Table
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            website TEXT NOT NULL,

            status TEXT NOT NULL,

            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # -----------------------------
    # Users Table
    # -----------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

       id INTEGER PRIMARY KEY AUTOINCREMENT,

       username TEXT UNIQUE NOT NULL,

       password TEXT NOT NULL,

       role TEXT NOT NULL DEFAULT 'user'

    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database created successfully!")


if __name__ == "__main__":
    create_database()