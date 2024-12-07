class FocusMeControl():

    def __init__(self, current_project=None):
        """_summary_
        """
        self.current_project = current_project
        pass

    def set_current_project(self, project):
        self.current_project = project

    def get_current_project(self):
        return self.current_project
