"""
    This module provides functions to interact with a SQLite database for managing projects, tasks, 
    and subtasks in the FocusMe application.
    Functions:
        initialize_database(conn=None, db_name=None):
        
        save_focusme_model_to_db(conn, focusme_model):
        
        generate_focusme_data_obj(conn):
        
        load_project_tasks_from_db(cursor, project_name):
            Loads tasks associated with a specific project from the database.
        
        add_project_to_db(conn, project) -> int:
            Adds a project to the database and returns the ID of the newly inserted project.
        
        get_project_by_name(conn, project_name):
            Retrieves a project by its name from the database.
        
        generate_project_obj(project_name, tasks_table):
        
        generate_task_obj(task_row):
        
        get_table_schema(conn, table_name):
            Retrieves the schema of a specified `table` in the database.
        
        update_task_in_db(conn, task):
        
        add_task_to_db(conn, task):
"""
import sqlite3
from model.focusme_model import Task, Subtask, Project, FocusMeData

def initialize_database(conn=None, db_name=None):
    """
    Initializes the database with the required tables: Projects, Tasks, and Subtasks.
    If a connection object is not provided, it will create a new SQLite connection.
    If a database name is provided, it will connect to that database; otherwise, 
    it will use an in-memory database.
    Args:
        conn (sqlite3.Connection, optional): An existing SQLite connection object. Defaults to None.
        db_name (str, optional): The name of the SQLite database file. Defaults to None.
    Returns:
        sqlite3.Connection: The SQLite connection object with the initialized database.
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
            description TEXT NOT NULL,
            status INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES Tasks (id)
        );
    """)
    
    conn.commit()
    return conn


def save_focusme_model_to_db(conn, focusme_model):
    """
    Saves the FocusMe model data to the database.
    Args:
        conn (sqlite3.Connection): The SQLite database connection object.
        focusme_model (FocusMeModel): The FocusMe model object containing projects, tasks, and subtasks.
    The function performs the following operations:
        1. Iterates over the projects in the focusme_model.
        2. Inserts each project into the Projects `table`.
        3. For each project, iterates over the kanban swimlanes and their associated tasks.
        4. Inserts each task into the Tasks `table`, associating it with the corresponding project and kanban swimlane.
        5. For each task, iterates over its subtasks and inserts them into the Subtasks `table`, associating them with the corresponding task.
    The function commits the transaction to the database after all operations are completed.
    """
    
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
                    task.taskname, task.description, task.estimated_pomodoros,
                    task.performed_pomodoros,
                    task.date_to_perform, task.repeat, project_id, kanban_swimlane,
                    task.tag
                ))
                task_id = cursor.lastrowid
                # Subtasks speichern
                for subtask in task.subtasks:
                    cursor.execute("INSERT INTO Subtasks (task_id, subtaskname) VALUES (?, ?);",
                                   (task_id, subtask))
    conn.commit()


def generate_focusme_data_obj(conn):
    """
    Generates a FocusMeData object by loading projects and their tasks from the database.
    Args:
        conn (sqlite3.Connection): The database connection object.
    Returns:
        FocusMeData: An object containing all projects and their associated tasks.
    The function performs the following steps:
    1. Initializes a FocusMeData object.
    2. Creates a cursor from the database connection.
    3. Executes a SQL query to load all projects from the 'Projects' `table`.
    4. Iterates over each project, loading its tasks and reconstructing the Project object.
    5. Adds each reconstructed Project object to the FocusMeData object.
    """
    focusme_data = FocusMeData()
    cursor = conn.cursor()

    # Load all projects from the database
    cursor.execute("SELECT id, name FROM Projects;")
    projects = cursor.fetchall()

    for project_id, project_name in projects:
        # get alls tasks of the project
        tasks_table = select_task_table(conn, project_name)
        # reconstruct Project-Object
        project = generate_project_obj(conn,project_name,tasks_table)
        # Füge das Projekt zu FocusMeData hinzu
        focusme_data.add_project(project)

    return focusme_data

def select_project_table(conn, project_name):
    """
    Retrieve a project by its name from the database.
    Args:
        conn (sqlite3.Connection): The database connection object.
        project_name (str): The name of the project to retrieve.
    Returns:
        Project: The reconstructed Project object containing the project's details and tasks.
    Raises:
        ValueError: If no project with the given name is found.
    """
    
    cursor = conn.cursor()
    # Projekt-ID anhand des Namens abrufen
    cursor.execute("SELECT id FROM Projects WHERE name = ?;", (project_name,))
    result = cursor.fetchone()
    
    if not result:
        raise ValueError(f"Kein Projekt mit dem Namen '{project_name}' gefunden.")
    
    # get alls tasks of the project
    tasks_table = select_task_table(conn, project_name) #FIXME Project_name is not unique, use project id
    # reconstruct Project-Object 
    project = generate_project_obj(conn, project_name, tasks_table)
    return project


def select_task_table(conn, project_name):
    """
    Load `tasks` associated with a specific project from the database.
    Args:
        conn (sqlite3.Connection): The database connection object.
        project_name (str): The name of the project whose tasks are to be loaded.
    Returns:
        list of tuple: A list of tuples where each tuple represents a task with the following fields:
            - id (int): The unique identifier of the task.
            - taskname (str): The name of the task.
            - description (str): A description of the task.
            - estimated_pomodoros (int): The estimated number of pomodoros to complete the task.
            - performed_pomodoros (int): The number of pomodoros performed on the task.
            - date_to_perform (str): The date the task is scheduled to be performed.
            - repeat (str): The repeat schedule of the task.
            - tag (str): The tag associated with the task.
            - assigned_kanban_swimlane (str): The kanban swimlane the task is assigned to.
            - assigned_project (str): The project the task is assigned to.
    """
    cursor = conn.cursor()

    
    try:
        cursor.execute("""
            SELECT id, taskname, description, estimated_pomodoros, performed_pomodoros, 
                   date_to_perform, repeat, tag, assigned_kanban_swimlane, assigned_project
            FROM Tasks
            WHERE assigned_project = ?;
        """, (project_name,))
    except sqlite3.Error as e:
        print(f"Fehler beim Laden der Aufgaben für das Projekt '{project_name}': {e}")
        return []
    task_table = cursor.fetchall()
    return task_table




def select_subtask_table(conn, task_id):
    """
    Loads subtasks for a given task from the database.
    Args:
        conn (sqlite3.Connection): The database connection object.
        task_id (int): The ID of the task whose subtasks are to be loaded.
    Returns:
        list: A list of subtasks associated with the given task.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, status FROM Subtasks WHERE task_id = ?;", (task_id,))
    return cursor.fetchall()




def add_project_to_db(conn, project) -> int:
    """
    Adds a project to the database.
    
    Args:
        conn (sqlite3.Connection): The database connection object.
        project (Project): The project to insert, with its `name` attribute set.
        
    Returns:
        int: The ID of the newly inserted project.
    Raises:
        sqlite3.Error: If an error occurs during the database operation.
    """
    cursor = conn.cursor()
    try:
        # Transaktion starten
        cursor.execute("BEGIN TRANSACTION;")

        # Projekt einfügen
        cursor.execute("INSERT INTO Projects (name) VALUES (?);", (project.name,))
        project.id = cursor.lastrowid
        conn.commit()
        return project.id
    
    except sqlite3.Error as e:
        # Bei Fehler: Rollback und Fehler ausgeben
        conn.rollback()
        print(f"Fehler beim Speichern des Projekts: {e}")
        raise

def select_project_table_target(conn, project_id):
    """
    Retrieve a project by its name from the database.
    Args:
        conn (sqlite3.Connection): The database connection object.
        project_name (str): The name of the project to retrieve.
    Returns:
        Project: The reconstructed Project object containing the project's details and tasks.
    Raises:
        ValueError: If no project with the given name is found.
    """
    
    cursor = conn.cursor()
    # Projekt-ID anhand des Namens abrufen
    
    cursor.execute(""" SELECT name, id FROM Projects WHERE id = ?;""", (project_id ,))
    
    result = cursor.fetchone()
    
    if not result:
        raise ValueError(f"Kein Projekt mit dem Namen '{project_id}' gefunden.")
    
    return result

def generate_project_obj(conn, project_name, tasks_table):
    """
    Generates a Project object with tasks.
    Args:
        project_name (str): The name of the project.
        tasks_table (list): A list of task data, where each element represents a task.
    Returns:
        Project: An instance of the Project class with tasks added.
    """
    
    project = Project(project_name)
    for task_row in tasks_table:
        task = generate_task_obj(conn, task_row)
        project.add_task(task)
    
    return project

def generate_project_obj_2(project_table, tasks_table, subtask_table):
    project = Project(project_table[0], project_table[1])
    for task_row in tasks_table:
        task = generate_task_obj_2(task_row, subtask_table)
        project.add_task(task)
    return project

def generate_task_obj_2(task_row, subtask_table):
    """
    Generates a Task object from a database row.
    Args:
        task_row (tuple): A tuple containing task data in the following order:
            - id (int): The unique identifier of the task.
            - taskname (str): The name of the task.
            - description (str): A brief description of the task.
            - estimated_pomodoros (int): The estimated number of pomodoros to complete the task.
            - performed_pomodoros (int): The number of pomodoros already performed.
            - date_to_perform (str): The date on which the task is to be performed.
            - repeat (bool): Indicates if the task is a repeating task.
            - tag (str): A tag associated with the task.
            - assigned_kanban_swimlane (str): The kanban swimlane to which the task is assigned.
            - assigned_project (str): The project to which the task is assigned.
    Returns:
        Task: An instance of the Task class populated with the provided data.
    """
    task = Task(
            id=task_row[0],
            taskname=task_row[1],
            description=task_row[2],
            estimated_pomodoros=task_row[3],
            performed_pomodoros=task_row[4],
            date_to_perform=task_row[5],
            repeat=task_row[6],
            tag=task_row[7],
            assigned_kanban_swimlane=task_row[8],
            assigned_project=task_row[9],
            )
    for subtask_row in subtask_table:
        subtask = Subtask(
            id=subtask_row[0],
            task_id=task.id,
            description=subtask_row[1],
            status=subtask_row[2]
        )
        task.add_subtask(subtask)
    
    return task

def generate_task_obj(conn, task_row):
    """
    Generates a Task object from a database row.
    Args:
        task_row (tuple): A tuple containing task data in the following order:
            - id (int): The unique identifier of the task.
            - taskname (str): The name of the task.
            - description (str): A brief description of the task.
            - estimated_pomodoros (int): The estimated number of pomodoros to complete the task.
            - performed_pomodoros (int): The number of pomodoros already performed.
            - date_to_perform (str): The date on which the task is to be performed.
            - repeat (bool): Indicates if the task is a repeating task.
            - tag (str): A tag associated with the task.
            - assigned_kanban_swimlane (str): The kanban swimlane to which the task is assigned.
            - assigned_project (str): The project to which the task is assigned.
    Returns:
        Task: An instance of the Task class populated with the provided data.
    """
    subtask_rows = select_subtask_table(conn, task_row[0])
    task = Task(
            id=task_row[0],
            taskname=task_row[1],
            description=task_row[2],
            estimated_pomodoros=task_row[3],
            performed_pomodoros=task_row[4],
            date_to_perform=task_row[5],
            repeat=task_row[6],
            tag=task_row[7],
            assigned_kanban_swimlane=task_row[8],
            assigned_project=task_row[9],
            )
    for subtask_row in subtask_rows:
        subtask = Subtask(
            id=subtask_row[0],
            task_id=task.id,
            description=subtask_row[1],
            status=subtask_row[2]
        )
        task.add_subtask(subtask)
    
    return task

def get_table_schema(conn, table_name):
    """
    Retrieve the schema of a specified `table` in the database.
    Args:
        conn (sqlite3.Connection): The connection object to the SQLite database.
        table_name (str): The name of the `table` whose schema is to be retrieved.
    Returns:
        list: A list of tuples, where each tuple contains information about a column in the `table`.
              The information typically includes the column id, name, type, not null flag, default value, and primary key flag.
    """
    
    schema = []
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    for row in cursor.fetchall():
        schema.append(row)
    return schema


def update_task_in_db(conn, task):
    """
    Updates an existing task in the database with new values.
    Args:
        conn (sqlite3.Connection): The database connection object.
        task (Task): An object containing the updated task information. 
                     It should have the following attributes:
                     - taskname (str): The name of the task.
                     - description (str): The description of the task.
                     - estimated_pomodoros (int): The estimated number of Pomodoros.
                     - performed_pomodoros (int): The number of Pomodoros performed.
                     - date_to_perform (str): The date to perform the task.
                     - repeat (str): The repeat value.
                     - assigned_project (int): The ID of the assigned project.
                     - assigned_kanban_swimlane (int): The ID of the assigned Kanban swimlane.
                     - tag (str): The tag associated with the task.
                     - id (int): The ID of the task to be updated.
    Returns:
        None
    Raises:
        sqlite3.Error: If an error occurs while updating the task in the database.
    """
    
    try:
        cursor = conn.cursor()
        # SQL UPDATE statement to modify the fields of the task in the database
        cursor.execute("""
            UPDATE Tasks
            SET
                taskname = ?, 
                description = ?, 
                estimated_pomodoros = ?, 
                performed_pomodoros = ?, 
                date_to_perform = ?, 
                repeat = ?, 
                assigned_project = ?, 
                assigned_kanban_swimlane = ?, 
                tag = ? 
            WHERE id = ?;
        """, (
            task.taskname,               # Task name
            task.description,            # Task description
            task.estimated_pomodoros,    # Estimated Pomodoros
            task.performed_pomodoros,    # Performed Pomodoros
            task.date_to_perform,        # Date to perform
            task.repeat,                 # Repeat value
            task.assigned_project,       # Assigned project ID
            task.assigned_kanban_swimlane, # Assigned Kanban swimlane
            task.tag,                    # Tag
            task.id                      # ID of the task to locate the correct row
        ))
        
        # Commit the changes to the database
        conn.commit()
        print(f"Task mit ID {task.id} erfolgreich aktualisiert.")
    except sqlite3.Error as e:
        print(f"Fehler beim Aktualisieren der Task: {e}")

def add_task_to_db(conn, task):
    """
    Adds a task to the database.
    Parameters:
    conn (sqlite3.Connection): The connection object to the SQLite database.
    task (Task): An object containing the task details to be added to the database. 
                 The Task object should have the following attributes:
                 - id (int): The unique identifier of the task is filled after db insertion
                 - taskname (str): The name of the task.
                 - description (str): A description of the task.
                 - estimated_pomodoros (int): The estimated number of pomodoros to complete the task.
                 - performed_pomodoros (int): The number of pomodoros performed so far.
                 - date_to_perform (str): The date when the task is scheduled to be performed.
                 - repeat (str): The repeat frequency of the task.
                 - assigned_project (str): The project to which the task is assigned.
                 - assigned_kanban_swimlane (str): The kanban swimlane to which the task is assigned.
                 - tag (str): A tag associated with the task.
    Returns:
    int: The ID of the newly inserted task.
    """
    
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
    
    for subtask in task.subtasks:
        add_subtask_to_db(conn, subtask)
    
    conn.commit()
    task.id = cursor.lastrowid
    return task.id



def add_subtask_to_db(conn, subtask):
    """
    Adds a subtask to the database.
    Args:
        conn (sqlite3.Connection): The database connection object.
        subtask (Subtask): The subtask object to be added, which should have 
                           the attributes 'task_id', 'description', and 'status'.
        id (int): The unique identifier of the task is filled after db insertion
    Returns:
        int: The ID of the newly inserted subtask.
    """

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Subtasks (task_id, description, status) 
        VALUES (?, ?, ?);
    """, (subtask.task_id, subtask.description, subtask.status))
    conn.commit()
    subtask.id = cursor.lastrowid
    return subtask.id
    
def update_subtask_in_db(conn, subtask):
    """
    Updates a subtask in the database.
    """
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Subtasks
        SET description = ?, status = ?
        WHERE id = ?;
    """, (subtask.description, subtask.status, subtask.id))
    conn.commit()