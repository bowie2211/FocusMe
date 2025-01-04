import unittest
import sqlite3
from model.focusme_model import Project, FocusMeData, Task, KanbanBoardColumns
from model.focusme_db import initialize_database, add_task_to_db, update_task_in_db

class TestFocusMeModel(unittest.TestCase):
    def test_create_focusme_data(self):
        focusme = FocusMeData()
        self.assertEqual(focusme.projects,[])

    def test_add_get_project(self):
        project_name_1 = "First Project"
        project_name_2 = "Second Project"
        false_name = "bla blub"
        focusme = FocusMeData()
        focusme.add_project( Project(project_name_1))
        focusme.add_project( Project(project_name_2))
        project_1 = focusme.get_project(project_name_1)
        self.assertEqual(project_1.name, project_name_1)
        project_2 = focusme.get_project(project_name_2)
        self.assertEqual(project_2.name, project_name_2)
        project_3 = focusme.get_project(false_name)
        self.assertEqual(project_3, None)
        
class TestProject(unittest.TestCase):
    def test_create_project(self):
        project_name = "Testproject"
        project = Project(project_name)
        self.assertEqual(project.name,project_name)
    
    def test_add_task(self):
        project_name = "Testproject"
        task1 = Task()
        task2 = Task() 
        project = Project(project_name)
        project.add_task(task1)
        project.add_task(task2)
        self.assertEqual(project.name,project_name)
        
        
class TestTask(unittest.TestCase):
    def test_create_task(self):
        task = Task()
        self.assertEqual(task.assigned_kanban_swimlane,KanbanBoardColumns.BACKLOG.value)

    def test_update_task_in_db(self):
        conn = initialize_database()
        task = Task(
            taskname="Initial Task",
            description="Initial Description",
            estimated_pomodoros=5,
            performed_pomodoros=2,
            date_to_perform="2023-10-10",
            repeat="weekly",
            assigned_project=1,
            assigned_kanban_swimlane=KanbanBoardColumns.BACKLOG.value,
            tag="initial"
        )
        add_task_to_db(conn, task)
        
        # Retrieve the task ID from the database
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Tasks WHERE taskname = ?;", (task.taskname,))
        task.id = cursor.fetchone()[0]
        
        # Update task details
        task.taskname = "Updated Task"
        task.description = "Updated Description"
        task.estimated_pomodoros = 10
        task.performed_pomodoros = 5
        task.date_to_perform = "2023-11-11"
        task.repeat = "daily"
        task.tag = "updated"
        
        update_task_in_db(conn, task)
        
        cursor.execute("SELECT taskname, description, estimated_pomodoros, performed_pomodoros, date_to_perform, repeat, tag FROM Tasks WHERE id = ?;", (task.id,))
        updated_task = cursor.fetchone()
        
        self.assertEqual(updated_task[0], "Updated Task")
        self.assertEqual(updated_task[1], "Updated Description")
        self.assertEqual(updated_task[2], 10)
        self.assertEqual(updated_task[3], 5)
        self.assertEqual(updated_task[4], "2023-11-11")
        self.assertEqual(updated_task[5], "daily")
        self.assertEqual(updated_task[6], "updated")
        
        conn.close()
