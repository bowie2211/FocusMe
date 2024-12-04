import unittest
from model.focusme_model import Project, FocusMeData, Task

class TestFocusMeModel(unittest.TestCase):
    def test_create_focusme_data(self):
        focusme = FocusMeData()
        self.assertEqual(focusme.projects,[])

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
        
        
class TestTaks(unittest.TestCase):
    def test_create_task(self):
        task = Task()
        self.assertEqual(task.assigned_kanban_swimlane,"Backlog")
