import unittest
from model.focusme_model import Project
from control.focusme_control import FocusMeControl

class TestFocusMeControl(unittest.TestCase):
    def test_create_focusme_control(self):
        focusme = FocusMeControl()
        self.assertEqual(focusme.current_project,None)
            
    def test_create_focusme_control_2(self):
        project = Project("Test")    
        focusme = FocusMeControl(project)
        self.assertEqual(focusme.current_project.name,"Test")

