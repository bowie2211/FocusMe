from enum import Enum

class RepeatEnum(Enum):
    NEVER = "Never"
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"

class KanbanBoardColumns(Enum):
    BACKLOG = "Backlog"
    IN_PROGRESS = "In Progress"
    DONE = "DONE"


class Task:
    def __init__(self, taskname="",description="", estimated_pomos=0, date_to_perform=None, repeat=RepeatEnum.NEVER.value, assigned_to_project="", assigned_kanban = KanbanBoardColumns.BACKLOG.value, tag="", subtasks=None):
        self.taskname = taskname
        self.description = description
        self.estimated_pomodoros = estimated_pomos
        self.performed_pomodoros = 0
        self.date_to_perform = date_to_perform 
        self.repeat = repeat
        self.assigned_project = assigned_to_project
        self.assigned_kanban_swimlane = assigned_kanban
        self.tag = tag
        self.subtasks = subtasks or []

    def __repr__(self):
        return f"<Task(taskname={self.taskname}, estimated_pomos={self.estimated_pomos}, date_to_perform={self.date_to_perform}, repeat={self.repeat}, assigned_to_project={self.assigned_to_project}, tag={self.tag}, subtasks={self.subtasks})>"




class Project:
    def __init__(self, name=""):
        self.tasks = {KanbanBoardColumns.BACKLOG.value: [], KanbanBoardColumns.IN_PROGRESS.value: [], KanbanBoardColumns.DONE.value: []}

        self.name = name
    
    def add_task(self, task):
        """
        Adds a task according to its attribute "assigned_kanban_swimlane" 
        to the tasks dictionary
        """
        self.tasks[task.assigned_kanban_swimlane].append(task)
        
class FocusMeData:
    def __init__(self):
        self.projects = []
        
    def add_project(self,project):
        self.projects.append(project) 

    def get_project(self, project_name):
        for project in self.projects:
            if (project_name == project.name):
                return project
        return None
