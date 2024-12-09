import unittest
import sqlite3
from model.focusme_model import Task, Project, KanbanBoardColumns
from model.focusme_db import initialize_database, add_project_to_db, add_task_to_db, get_table_schema, get_project_by_name

class TestFocusMeDB(unittest.TestCase):
    def test_initialize_db(self):
        db = initialize_database(db_name="test.db")
        db.total_changes
        self.assertEqual(db.total_changes,0)

    def test_add_task_to_db(self):
        conn=initialize_database() #in memory data base 
        new_task = Task(
        taskname="Neue Backlog-Task", 
        description="Eine neue Aufgabe", 
        estimated_pomodoros=3, 
        performed_pomodoros=0, 
        date_to_perform="2023-12-10", 
        repeat="weekly", 
        assigned_project="P1",
        tag="Important")
        

        # Neue Task in den Backlog des Projekts mit ID 1 einfügen
        add_task_to_db(conn, task=new_task)
        # Verbindung schließen
        conn.close()
        
    def test_add_project_to_db(self):
        conn=initialize_database() #in memory data base 
        project = Project("P1")
        add_project_to_db(conn, project)
        print("yepp")
    
    def test_get_project_by_name(self):
        conn=initialize_database() #in memory data base 
        project = Project("P2")
        prj_id=add_project_to_db(conn, project)
        print(prj_id)
        task1 = Task(
        taskname="Neue Backlog-Task", 
        description="Eine neue Aufgabe", 
        estimated_pomodoros=3, 
        performed_pomodoros=0, 
        assigned_kanban_swimlane=KanbanBoardColumns.BACKLOG.value,
        date_to_perform="2023-12-10", 
        repeat="weekly", 
        assigned_project="P2",
        tag="Important")
        add_task_to_db(conn, task=task1)
        task2 = Task(
        taskname="Neue in_progress-Task", 
        description="Eine neue Aufgabe", 
        estimated_pomodoros=3, 
        performed_pomodoros=0, 
        assigned_kanban_swimlane=KanbanBoardColumns.IN_PROGRESS.value,
        date_to_perform="2023-12-10", 
        repeat="weekly", 
        assigned_project="P2",
        tag="Important")
        add_task_to_db(conn, task=task2)
        task3 = Task(
        taskname="Neue done-Task", 
        description="Eine neue Aufgabe", 
        estimated_pomodoros=3, 
        performed_pomodoros=0, 
        assigned_kanban_swimlane=KanbanBoardColumns.DONE.value,
        date_to_perform="2023-12-10", 
        repeat="weekly", 
        assigned_project="P2",
        tag="Important")
        add_task_to_db(conn, task=task3)
        project = get_project_by_name(conn, "P2")
        self.assertEqual(project.tasks[KanbanBoardColumns.BACKLOG.value][0].taskname,task1.taskname)
        self.assertEqual(project.tasks[KanbanBoardColumns.IN_PROGRESS.value][0].taskname,task2.taskname)
        self.assertEqual(project.tasks[KanbanBoardColumns.DONE.value][0].taskname,task3.taskname)
  
    
    def test_tasks_table_schema(self):
        conn=initialize_database() #in memory data base 
        schema=get_table_schema(conn, "Tasks")
        self.assertEqual(schema[1][1],"taskname")
        self.assertEqual(schema[2][1],"description")
        self.assertEqual(schema[3][1],"estimated_pomodoros")
        self.assertEqual(schema[4][1],"performed_pomodoros")
        self.assertEqual(schema[5][1],"date_to_perform")
        self.assertEqual(schema[6][1],"repeat")
        self.assertEqual(schema[7][1],"assigned_project")
        self.assertEqual(schema[8][1],"assigned_kanban_swimlane")
        self.assertEqual(schema[9][1],"tag")
