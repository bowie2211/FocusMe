"""
focusme_model holds the data structures for the FocusMe application.

This module provides enumerations and classes for dealing with tasks and 
projects. 
"""

from enum import Enum
   
class RepeatEnum(Enum):
    """
    Enumeration for the different kinds of 
    task repetetions
    
    Returns:
        Nothing
    """
    NEVER = "Never"
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"


class KanbanBoardColumns(Enum):
    """
    Enumrtion for the different kind of kanban board
    columns
    
    Returns:
        Nothing
    """    
    BACKLOG = "Backlog"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class Task:
    """
    Attributes and methods for dealing with kanban tasks
    """
    def __init__(self, taskname="", description="", estimated_pomodoros=0,  \
                       performed_pomodoros=0, date_to_perform=None, \
                       repeat=RepeatEnum.NEVER.value, assigned_project="", \
                       assigned_kanban_swimlane=KanbanBoardColumns.BACKLOG.value, \
                       tag="", subtasks=None):
        self.taskname = taskname
        self.description = description
        self.estimated_pomodoros = estimated_pomodoros
        self.performed_pomodoros = performed_pomodoros
        self.date_to_perform = date_to_perform
        self.repeat = repeat
        self.assigned_project = assigned_project
        self.assigned_kanban_swimlane = assigned_kanban_swimlane
        self.tag = tag
        self.subtasks = subtasks or []

    def __repr__(self):
        return f"<Task(taskname={self.taskname}, description={self.description}, estimated_pomodoros={self.estimated_pomodoros}, \
                       date_to_perform={self.date_to_perform}, repeat={self.repeat}, assigned_project={self.assigned_project}, \
                       assigned_kanban_swimlane={self.assigned_kanban_swimlane}, tag={self.tag}, subtasks={self.subtasks})>"


class Project:
    """
    Attributes and methods for dealing with projects tasks that are organized as kanban tasks
    """
    def __init__(self, name=""):
        self.tasks = {KanbanBoardColumns.BACKLOG.value: [
        ], KanbanBoardColumns.IN_PROGRESS.value: [], KanbanBoardColumns.DONE.value: []}

        self.name = name

    def add_task(self, task):
        """
        Adds a task according to its attribute "assigned_kanban_swimlane" 
        to the tasks dictionary
        Args:
            task (Task): Task object that has to be added to a swimlane.

        Returns:
            nothing
        """
        self.tasks[task.assigned_kanban_swimlane].append(task)
    
    def get_task(self, task_name, assigned_kanban_swimlane):
        """
        provides task object depending on name and kanban swimlane

        Args:
            task_name (string): name of task
            assigned_kanban_swimlane (string) : kanban swimlane according to KanbanBoardColumns enumeration
        
        Returns:
            Task: Task object
        """
        for task in self.tasks[assigned_kanban_swimlane]:
            if task.taskname == task_name:
                return task
        return None

class FocusMeData:
    """
    Attributes and methods for dealing with serveral projects with tasks that are organized as kanban tasks
    """
    def __init__(self):
        self.projects = []

    def add_project(self, project):
        """
        Adds a project to global data structure        
        
        Args:
            project (Project): Project object that has to be added to the global data structure.

        Returns:
            nothing
        """
        self.projects.append(project)

    def get_project(self, project_name):
        """
        Returns the project named project_name from the global data structure        
        
        Args:
            project_name (string): Project name that has to be returned from the 
            global data structure.

        Returns:
            Project: Project data of the named project
            None: If Project name is not in data structure
        """
        for project in self.projects:
            if project_name == project.name:
                return project
        return None
