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
    DONE = "DONE"

class Task:
    """
    Attributes and methods for dealing with kanban tasks
    """
    def __init__(self, id=None, taskname="", description="", estimated_pomodoros=0,  \
                       performed_pomodoros=0, date_to_perform=None, \
                       repeat=RepeatEnum.NEVER.value, tag="",\
                       assigned_kanban_swimlane=KanbanBoardColumns.BACKLOG.value, \
                       assigned_project="", subtasks=None):
        
        self.id = id
        self.taskname = taskname
        self.description = description
        self.estimated_pomodoros = estimated_pomodoros
        self.performed_pomodoros = performed_pomodoros
        self.date_to_perform = date_to_perform
        self.repeat = repeat
        self.tag = tag
        self.assigned_kanban_swimlane = assigned_kanban_swimlane
        self.assigned_project = assigned_project
        self.subtasks = subtasks or []
        

    def __repr__(self):
        return f"<Task(id={self.id}, taskname={self.taskname}, description={self.description}, estimated_pomodoros={self.estimated_pomodoros}, \
                       date_to_perform={self.date_to_perform}, repeat={self.repeat}, assigned_kanban_swimlane={self.assigned_kanban_swimlane}, \
                       tag={self.tag}, assigned_project={self.assigned_project},  subtasks={self.subtasks})>"

    def add_subtask(self, subtask):
        """
        Adds a subtask to the task object
        
        Args:
            subtask (Subtask): Subtask object that has to be added to the task object.

        Returns:
            nothing
        """
        self.subtasks.append(subtask)
    
    def update_subtask(self, subtask):
        """
        Updates a subtask in the task object
        
        Args:
            subtask (Subtask): Subtask object that has to be updated in the task object.

        Returns:
            nothing
        """
        for i, st in enumerate(self.subtasks):
            if st.id == subtask.id:
                self.subtasks[i] = subtask
                break

class Subtask:
    def __init__(self, id=None, task_id=None, project_id = None, description="", status=0):
        self.id = id
        self.task_id = task_id
        self.project_id = project_id
        self.description = description
        self.status = status


class Project:
    """
    Attributes and methods for dealing with projects tasks that are organized as kanban tasks
    """
    def __init__(self,  name="", db_id=None):
        self.tasks = {KanbanBoardColumns.BACKLOG.value: [
        ], KanbanBoardColumns.IN_PROGRESS.value: [], KanbanBoardColumns.DONE.value: []}
        self.id = db_id
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
