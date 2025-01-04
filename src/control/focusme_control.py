class FocusMeControl():
    """
        Information about the current selected project and task 
        can be set and get. 
    """

    def __init__(self, current_project=None, current_task=None):
        """
        Sets the current_project and current_task attribute
        """
        self.current_project = current_project
        self.current_task = current_task
        pass

    def set_current_project(self, project):
        """
            Sets the current_project attribute
            
            Args:
            current_project (Project): Project object
        
            Returns:
            Nothing
        """
        self.current_project = project

    def get_current_project(self):
        """
            Returns the current_project attribute
            
            Args:
            None
        
            Returns:
            Task Project
        """
        return self.current_project

    def set_current_task(self, task):
        """
            Sets the current_task attribute
            
            Args:
            current_project (Task): Task object
        
            Returns:
            Nothing
        """
        self.current_task = task

    def get_current_task(self):
        """
            Returns the current_task attribute
            
            Args:
            None
        
            Returns:
            Task Object
        """
        return self.current_task

