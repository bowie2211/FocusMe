import sqlite3
from model.focusme_model import Task, Project

def initialize_database(conn=None, db_name=None):
    """_summary_

    Args:
        conn (_type_, optional): _description_. Defaults to None.
        db_name (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """    
    if conn is None:
        if db_name:
            conn = sqlite3.connect(db_name)  # Persistente Datenbank
        else:
            conn = sqlite3.connect(":memory:")  # In-Memory-Datenbank
    cursor = conn.cursor()
    
    # Tabellen erstellen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            taskname TEXT NOT NULL,
            description TEXT,
            estimated_pomodoros INTEGER,
            performed_pomodoros INTEGER,
            date_to_perform DATE,
            repeat TEXT,
            assigned_project INTEGER NOT NULL,
            assigned_kanban_swimlane TEXT NOT NULL,
            tag TEXT,
            FOREIGN KEY (assigned_project) REFERENCES Projects (id)
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            subtaskname TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES Tasks (id)
        );
    """)
    
    conn.commit()
    return conn


def save_focusme_model_to_db(conn, focusme_model):
    cursor = conn.cursor()
    
    # Projekte speichern
    for project in focusme_model.projects:  # Annahme: focusme_model.projects ist eine Liste von Projekten
        cursor.execute("INSERT INTO Projects (name) VALUES (?);", (project.name,))
        project_id = cursor.lastrowid
        
        # Tasks pro Kanban-Spalte speichern
        for kanban_swimlane, tasks in project.kanban.items():
            for task in tasks:
                cursor.execute("""
                    INSERT INTO Tasks (
                        taskname, description, estimated_pomodoros, performed_pomodoros, 
                        date_to_perform, repeat, assigned_project, assigned_kanban_swimlane, tag
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    task.taskname, task.description, task.estimated_pomodoros, task.performed_pomodoros,
                    task.date_to_perform, task.repeat, project_id, kanban_swimlane, task.tag
                ))
                task_id = cursor.lastrowid
                
                # Subtasks speichern
                for subtask in task.subtasks:
                    cursor.execute("INSERT INTO Subtasks (task_id, subtaskname) VALUES (?, ?);", (task_id, subtask))
    
    conn.commit()


def add_task_to_db(conn, task):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Tasks (
            taskname, description, estimated_pomodoros, performed_pomodoros, 
            date_to_perform, repeat, assigned_project, assigned_kanban_swimlane, tag
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        task.taskname, task.description, task.estimated_pomodoros, 
        task.performed_pomodoros, task.date_to_perform, task.repeat, 
        task.assigned_project, task.assigned_kanban_swimlane, task.tag
    ))
    conn.commit()

def add_project_to_db(conn, project):
    cursor = conn.cursor()
    try:
        # Transaktion starten
        cursor.execute("BEGIN TRANSACTION;")

        # Projekt einfügen
        cursor.execute("INSERT INTO Projects (name) VALUES (?);", (project.name,))
        project_id = cursor.lastrowid
        # Transaktion abschließen
        conn.commit()
        return project_id
    
    except sqlite3.Error as e:
        # Bei Fehler: Rollback und Fehler ausgeben
        conn.rollback()
        print(f"Fehler beim Speichern des Projekts: {e}")
        raise


def get_project_by_name(conn, project_name):
    """
    Ruft ein Projekt und alle zugehörigen Tasks anhand des Projektnamens aus der Datenbank ab.
    
    :param conn: SQLite-Verbindung
    :param project_name: Name des Projekts
    :return: Ein rekonstruierter Project-Objekt
    """
    cursor = conn.cursor()
    
    # Projekt-ID anhand des Namens abrufen
    cursor.execute("SELECT id FROM Projects WHERE name = ?;", (project_name,))
    result = cursor.fetchone()
    
    if not result:
        raise ValueError(f"Kein Projekt mit dem Namen '{project_name}' gefunden.")
    
    project_id = result[0]

    # Alle Tasks des Projekts abrufen
    cursor.execute("""
        SELECT taskname, description, estimated_pomodoros, performed_pomodoros, 
               date_to_perform, repeat, tag, assigned_kanban_swimlane, assigned_project
        FROM Tasks
        WHERE assigned_project = ?;
    """, (project_name ,))
    tasks = cursor.fetchall()
    
    # Projekt-Objekt rekonstruieren
    project = Project(project_name)
    for task_row in tasks:
        task = Task(
            taskname=task_row[0],
            description=task_row[1],
            estimated_pomodoros=task_row[2],
            performed_pomodoros=task_row[3],
            date_to_perform=task_row[4],
            repeat=task_row[5],
            assigned_project=task_row[8],
            assigned_kanban_swimlane=task_row[7],
            tag=task_row[6]
            )
        #kanban_swimlane = task_row[7]
        #project.kanban[kanban_swimlane].append(task)
        project.add_task(task)
    
    return project

# def get_projects():
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, name FROM Projects")
#     projects = cursor.fetchall()
#     conn.close()
#     return projects

# def add_project(name, description):
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO Projects (name, description) VALUES (?, ?)", (name, description))
#     conn.commit()
#     conn.close()

# def get_tasks_by_status(project_id, status):
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
#     cursor.execute("SELECT id, name FROM Tasks WHERE project_id = ? AND status = ?", (project_id, status))
#     tasks = cursor.fetchall()
#     conn.close()
#     return tasks

# def add_task(name, project_id, status):
#     conn = sqlite3.connect(DB_FILE)
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO Tasks (name, project_id, status) VALUES (?, ?, ?)", (name, project_id, status))
#     conn.commit()
#     conn.close()


def get_table_schema(conn, table_name):
    schema = []
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    for row in cursor.fetchall():
        schema.append(row)
    return schema