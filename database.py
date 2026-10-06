import sqlite3


# ==================================================
# DATABASE CONNECTION
# ==================================================

def connect_db():
    connection = sqlite3.connect("skillshare.db")
    return connection


# ==================================================
# USERS TABLE
# ==================================================

def create_users_table():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ==================================================
# SKILLS TABLE
# ==================================================

def create_skills_table():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            skill_type TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# ==================================================
# REQUESTS TABLE
# ==================================================

def create_requests_table():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    """)

    connection.commit()
    connection.close()


# ==================================================
# RESOURCES TABLE
# ==================================================

def create_resources_table():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            link TEXT NOT NULL,
            description TEXT
        )
    """)

    connection.commit()
    connection.close()


# ==================================================
# CREATE ALL TABLES
# ==================================================

create_users_table()
create_skills_table()
create_requests_table()
create_resources_table()
def create_reviews_table():

    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reviewer_id INTEGER NOT NULL,
            reviewed_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT,
            FOREIGN KEY (reviewer_id) REFERENCES users(id),
            FOREIGN KEY (reviewed_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()