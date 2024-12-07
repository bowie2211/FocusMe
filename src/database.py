import sqlite3

DB_FILE = "focusme.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tabelle für Projekte
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    );
    """)

    # Tabelle für Tasks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        project_id INTEGER,
        status TEXT,
        FOREIGN KEY (project_id) REFERENCES Projects (id)
    );
    """)

    conn.commit()
    conn.close()

def get_projects():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Projects")
    projects = cursor.fetchall()
    conn.close()
    return projects

def add_project(name, description):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Projects (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    conn.close()

def get_tasks_by_status(project_id, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Tasks WHERE project_id = ? AND status = ?", (project_id, status))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def add_task(name, project_id, status):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Tasks (name, project_id, status) VALUES (?, ?, ?)", (name, project_id, status))
    conn.commit()
    conn.close()
