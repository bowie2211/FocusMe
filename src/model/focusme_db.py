import sqlite3
from model.focusme_model import Task, Project, FocusMeData

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


def generate_focusme_data_obj(conn):
    """
    Lädt die Projekte und Tasks aus der SQLite-Datenbank in ein FocusMeData-Objekt.
    This function is required when th App is started and all data stored in the db
    has to be loaded into the RAM
    Args:
        conn: SQLite-Verbindung.

    Returns:
        Ein FocusMeData-Objekt, das alle Projekte und Tasks aus der Datenbank enthält.
    """
    focusme_data = FocusMeData()
    cursor = conn.cursor()

    # Lade alle Projekte aus der Datenbank
    cursor.execute("SELECT id, name FROM Projects;")
    projects = cursor.fetchall()

    for project_id, project_name in projects:
        # get alls tasks of the project
        tasks_table = load_project_tasks_from_db(cursor, project_name)
        # reconstruct Project-Object
        project = generate_project_obj(project_name,tasks_table)
        # Füge das Projekt zu FocusMeData hinzu
        focusme_data.add_project(project)

    return focusme_data


def load_project_tasks_from_db(cursor, project_name):
    cursor.execute("""
        SELECT taskname, description, estimated_pomodoros, performed_pomodoros, 
               date_to_perform, repeat, tag, assigned_kanban_swimlane, assigned_project
        FROM Tasks
        WHERE assigned_project = ?;
    """, (project_name ,))
    return cursor.fetchall()

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
    
    # get alls tasks of the project
    tasks_table = load_project_tasks_from_db(cursor, project_name)
    # reconstruct Project-Object 
    project = generate_project_obj(project_name,tasks_table)
    return project


def generate_project_obj(project_name, tasks_table):
    """_generates a Project object from a Project name and a SQLite Tasks Table_

    Args:
        project_name (_string_): _project name_
        tasks_table (_type_): _result from a Tasks table query_

    Returns:
        _Project_: _Project opbject with filled kanban tasks_
    """
    project = Project(project_name)
    for task_row in tasks_table:
        task = generate_task_obj(task_row)
        project.add_task(task)
    
    return project

def generate_task_obj(task_row):
    """_generates a Task object from a SQLite Tasks Table_

    Args:
        task_row (_type_): _result from a Tasks table query_

    Returns:
        _type_: _description_
    """    
    return Task(
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

def get_table_schema(conn, table_name):
    schema = []
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    for row in cursor.fetchall():
        schema.append(row)
    return schema