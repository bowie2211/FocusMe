import unittest
import sqlite3
from model.focusme_model import Task, Subtask, Project, KanbanBoardColumns
from model.focusme_db import initialize_database, add_project_to_db, add_task_to_db, add_subtask_to_db, get_table_schema, select_project_table, \
                             generate_focusme_data_obj, select_project_table_target, generate_project_obj_2, select_task_table, select_subtask_table
                             

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
        project = select_project_table(conn, "P2")
        self.assertEqual(project.tasks[KanbanBoardColumns.BACKLOG.value][0].taskname,task1.taskname)
        self.assertEqual(project.tasks[KanbanBoardColumns.IN_PROGRESS.value][0].taskname,task2.taskname)
        self.assertEqual(project.tasks[KanbanBoardColumns.DONE.value][0].taskname,task3.taskname)
  
  
    def test_generate_project_obj_2(self):
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
        task1_id=add_task_to_db(conn, task=task1) #important: has to be added to db before subtasks, as task.id is needed for subtask
        subtask1 = Subtask(id=None, task_id=task1.id, description="Subtask1", status=0)
        subtask2 = Subtask(id=None, task_id=task1.id, description="Subtask2", status=0)
        subtask3 = Subtask(id=None, task_id=task1.id, description="Subtask3", status=0)
        add_subtask_to_db(conn, subtask1)
        add_subtask_to_db(conn, subtask2)
        add_subtask_to_db(conn, subtask3)
        
        project_table = select_project_table_target(conn, prj_id) 
        tasks_table = select_task_table(conn, project_table[0]) #unpacking tuple
        subtask_table   = select_subtask_table(conn, task1_id)
        project = generate_project_obj_2(project_table, tasks_table, subtask_table)
        assertEqual(project.tasks[KanbanBoardColumns.BACKLOG.value][0].subtasks[0].description, subtask1.description)
        assertEqual(project.tasks[KanbanBoardColumns.BACKLOG.value][0].subtasks[1].description, subtask2.description)
    
    
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

    def test_generate_focusme_data_obj(self):
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
        focusme_data = generate_focusme_data_obj(conn)
        self.assertEqual(focusme_data.projects[0].tasks[KanbanBoardColumns.BACKLOG.value][0].taskname,task1.taskname)
        self.assertEqual(focusme_data.projects[0].tasks[KanbanBoardColumns.IN_PROGRESS.value][0].taskname,task2.taskname)
        self.assertEqual(focusme_data.projects[0].tasks[KanbanBoardColumns.DONE.value][0].taskname,task3.taskname)
        
        
    def test_select_project(self):
        conn=initialize_database() #in memory data base 
        project = Project("P2")
        prj_id=add_project_to_db(conn, project)
        print(prj_id)
        proj_table = select_project_table_target(conn, prj_id)
        self.assertEqual(proj_table[0],project.name)

    def test_select_subtask_table(self):
        conn=initialize_database() #in memory data base 
        project = Project("P2")
        prj_id=add_project_to_db(conn, project)
        print(prj_id)
        task=Task(1, "Task1", "Description", 3, 0, "2023-12-10", "weekly", "P2", "Important")
        task_id=add_task_to_db(conn, task)  
        subtask1 = Subtask(task_id=task_id, description="test subtask1", status=0)
        subtask2 = Subtask(task_id=task_id, description="test subtask2", status=0)
        subtask1_id=add_subtask_to_db(conn, subtask1)
        subtask2_id=add_subtask_to_db(conn, subtask2)
        subtask_table = select_subtask_table(conn, task_id)
        self.assertEqual(subtask_table[0][0],subtask1_id)
        self.assertEqual(subtask_table[1][0],subtask2_id)  
    
    def test_select_task_table_1(self):
        """
        Test case for selecting tasks from the task table for a specific project.
        Testcase test handling of more than one task in the task table.
        This test initializes an in-memory database, adds a project and two tasks to the database,
        and then selects the tasks from the task table associated with the project. It verifies
        that the first task in the selected tasks table matches the ID of the first task added.
        Steps:
        1. Initialize an in-memory database.
        2. Create a project and add it to the database.
        3. Create two tasks and add them to the database.
        4. Select the tasks from the task table for the created project.
        5. Assert that the ID of the first task in the selected tasks table matches the ID of the first task added.
        Asserts:
        - The ID of the first task in the selected tasks table matches the ID of the first task added.
        """
        
        conn=initialize_database() #in memory data base
        project = Project("P2")
        prj_id=add_project_to_db(conn, project)
        print(prj_id)
        task1 = Task( taskname="Neue Backlog-Task", 
                        description="Eine neue Aufgabe", 
                        estimated_pomodoros=3, 
                        performed_pomodoros=0, 
                        assigned_kanban_swimlane=KanbanBoardColumns.BACKLOG.value,
                        date_to_perform="2023-12-10", 
                        repeat="weekly", 
                        assigned_project="P2",
                        tag="Important")    
        task2 = Task( taskname="Neue in_progress-Task",description="Eine neue Aufgabe", 
                        estimated_pomodoros=3, 
                        performed_pomodoros=0, 
                        assigned_kanban_swimlane=KanbanBoardColumns.BACKLOG.value,
                        date_to_perform="2023-12-10", 
                        repeat="weekly", 
                        assigned_project="P2",
                        tag="Important")
        task1_id=add_task_to_db(conn, task1)
        task2_id=add_task_to_db(conn, task2)
        tasks_table = select_task_table(conn, project.name)
        self.assertEqual(tasks_table[0][0],task1_id)
        
    def test_select_task_table_2(self):
        """
        Test case for selecting tasks from the task table for a specific project.
        Testcase test handling of only one task in the task table.
        This test initializes an in-memory database, adds a project and two tasks to the database,
        and then selects the tasks from the task table associated with the project. It verifies
        that the first task in the selected tasks table matches the ID of the first task added.
        Steps:
        1. Initialize an in-memory database.
        2. Create a project and add it to the database.
        3. Create two tasks and add them to the database.
        4. Select the tasks from the task table for the created project.
        5. Assert that the ID of the first task in the selected tasks table matches the ID of the first task added.
        Asserts:
        - The ID of the first task in the selected tasks table matches the ID of the first task added.
        """
        
        conn=initialize_database() #in memory data base
        project = Project("P2")
        prj_id=add_project_to_db(conn, project)
        print(prj_id)
        task1 = Task( taskname="Neue Backlog-Task", 
                        description="Eine neue Aufgabe", 
                        estimated_pomodoros=3, 
                        performed_pomodoros=0, 
                        assigned_kanban_swimlane=KanbanBoardColumns.BACKLOG.value,
                        date_to_perform="2023-12-10", 
                        repeat="weekly", 
                        assigned_project="P2",
                        tag="Important")    
        
        task1_id=add_task_to_db(conn, task1)
        tasks_table = select_task_table(conn, project.name)
        self.assertEqual(tasks_table[0][0],task1_id)