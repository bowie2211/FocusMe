import unittest
from model.focusme_model import Project, FocusMeData, Task, KanbanBoardColumns

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
