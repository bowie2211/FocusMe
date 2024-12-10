from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QListWidgetItem, QInputDialog, QLabel,
    QLineEdit, QComboBox, QDateEdit, QFormLayout, QMenuBar, QMenu, QFrame
)
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from view.ui_task_input_dlg import TaskInputDialog
from model.focusme_model import FocusMeData, Project, KanbanBoardColumns
from control.focusme_control import FocusMeControl
from model.focusme_db import add_project_to_db, add_task_to_db

class KanbanBoard(QWidget):
    def __init__(self, add_task_callback):
        """_summary_
        """
        super().__init__()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.add_task_callback = add_task_callback
        # Spalten für das Board
        self.columns = {}
        for col in KanbanBoardColumns:
            self.columns[col.value] = self.create_column(col.value)
            self.layout.addWidget(self.columns[col.value])
            
        # for title in ["Backlog", "In Progress", "Done"]:
        #     self.columns[title] = self.create_column(title)
        #     self.layout.addWidget(self.columns[title])

        # Fixme this is a model that is tightyl coupled to a view
        #self.tasks = {"Backlog": [], "In Progress": [], "Done": []}

    def create_column(self, title):
        """_summary_

        Args:
            title (_type_): _description_

        Returns:
            _type_: _description_
        """
        column_widget = QWidget()
        column_layout = QVBoxLayout()
        column_widget.setLayout(column_layout)

        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        column_layout.addWidget(label)

        list_widget = CustomListWidget(title, self)
        list_widget.setAcceptDrops(True)
        list_widget.setDragEnabled(True)
        column_layout.addWidget(list_widget)

        add_btn = QPushButton(f"{title} hinzufügen")
        add_btn.clicked.connect(lambda: self.add_task(list_widget, title))
        column_layout.addWidget(add_btn)
        column_widget.list_widget = list_widget #save list widget for later access (e.g. delete entries)
        return column_widget

    def add_task(self, list_widget, column_name):
        """_summary_

        Args:
            list_widget (_type_): _list with current widgets_
            column_name (_type_): _name of kanban column_
        """
        # task_name, ok = QInputDialog.getText(self, "Task hinzufügen", "Taskname:")
        dialog = TaskInputDialog()
        task = dialog.get_task(column_name)
        item = QListWidgetItem(task.taskname)
        item.setData(Qt.UserRole, task)
        list_widget.addItem(item)
        #this is a callback function call that adds the new task
        #the the correct project and kanban_lane.
        self.add_task_callback(task)
        

    def updated_boards(self, project):
        """_summary_

        Args:
            project (_type_): _description_
        """
        
         # Step 1: delete old entries
        for column_widget in self.columns.values():
            column_widget.list_widget.clear()  # clear elements in the list widgets
       
       
        # Step 2: Pupulate with new task from new project
        for column, tasks in project.items():
            if column in self.columns:
                for task in tasks:
                    self.columns[column].addItem(task)  # GUI-Element mit neuen Tasks befüllen  
        
        print("todo")


class CustomListWidget(QListWidget):
    """_summary_

    Args:
        QListWidget (_type_): _description_
    """

    def __init__(self, column_name, board):
        super().__init__()
        self.column_name = column_name
        self.board = board

    def startDrag(self, supportedActions):
        """_summary_

        Args:
            supportedActions (_type_): _description_
        """
        item = self.currentItem()
        if item:
            mime_data = QMimeData()
            mime_data.setText(item.text())
            mime_data.setData("application/x-kanban-task",
                              self.column_name.encode())

            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-kanban-task"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-kanban-task"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-kanban-task"):
            task_name = event.mimeData().text()
            source_column = event.mimeData().data(
                "application/x-kanban-task").data().decode()
            self.add_task_to_column(task_name, source_column)
            event.acceptProposedAction()

    def add_task_to_column(self, task_name, source_column):
        item = QListWidgetItem(task_name)
        self.addItem(item)

        # Remove the task from the source column's internal data
        parent_board = self.board
        task_data = None
        for task in parent_board.tasks[source_column]:
            if task.taskname == task_name:
                task_data = task
                break

        if task_data:
            parent_board.tasks[source_column].remove(task_data)
            parent_board.tasks[self.column_name].append(task_data)

        # Zeige Task-Details im Detail-Panel
        self.board.parent().parent().show_task_details(task_data)


class MainWindow(QMainWindow):
    """_summary_

    Args:
        QMainWindow (_type_): _description_
    """
    def __init__(self, focusme_data_model, focusme_control, db_conn):
        """_summary_

        Args:
            focusme_data_model (_type_): _description_
        """
        super().__init__()
        self.setWindowTitle("FocusMe")
        self.setGeometry(100, 100, 1200, 800)
        self.focusme_data_model = focusme_data_model
        self.focusme_control = focusme_control
        self.db_conn = db_conn
        self.projects = {}
        self.current_project = None

        self.init_ui()

    def init_ui(self):
        """_summary_
        """
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Menüleiste
        menu_bar = QMenuBar()
        file_menu = QMenu("Datei", self)
        menu_bar.addMenu(file_menu)
        edit_menu = QMenu("Bearbeiten", self)
        menu_bar.addMenu(edit_menu)
        layout.addWidget(menu_bar)

        # Hauptbereich mit Projekten, Kanban und Task-Details
        main_area = QHBoxLayout()
        layout.addLayout(main_area)

        # Linke Seite mit Projektliste
        project_layout = QVBoxLayout()

        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.switch_project)
        project_layout.addWidget(self.project_list)

        add_project_btn = QPushButton("Projekt hinzufügen")
        add_project_btn.clicked.connect(self.add_project)
        project_layout.addWidget(add_project_btn)

        delete_project_btn = QPushButton("Projekt löschen")
        delete_project_btn.clicked.connect(self.delete_project)
        project_layout.addWidget(delete_project_btn)

        main_area.addLayout(project_layout, 1)

        # Kanban-Board
        self.kanban_board = KanbanBoard(self.update_data_model)
        main_area.addWidget(self.kanban_board, 4)

        # Rechte Seite mit Task-Details
        self.details_panel = QWidget()
        details_layout = QFormLayout()
        self.details_panel.setLayout(details_layout)

        self.detail_fields = {
            "Taskname": QLineEdit(),
            "Estimated_Pomos": QLineEdit(),
            "Date_to_Perform": QDateEdit(),
            "Repeat": QComboBox(),
            "Assigned_to_project": QLineEdit(),
            "Tag": QLineEdit(),
            "Subtasks": QLineEdit(),
        }

        self.detail_fields["Repeat"].addItems(
            ["never", "day", "week", "month"])

        for key, widget in self.detail_fields.items():
            details_layout.addRow(QLabel(key), widget)

        self.save_task_btn = QPushButton("Änderungen speichern")
        self.save_task_btn.clicked.connect(self.save_task_details)
        details_layout.addRow(self.save_task_btn)

        main_area.addWidget(self.details_panel, 2)

    def add_project(self):
        project_name, ok = QInputDialog.getText(
            self, "Projekt hinzufügen", "Projektname:")
        if ok and project_name:
            self.project_list.addItem(project_name)
            self.focusme_data_model.add_project(Project(project_name))
            self.focusme_control.set_current_project(self.focusme_data_model.get_project(project_name)) 
            add_project_to_db(self.db_conn, self.focusme_data_model.get_project(project_name))

    def delete_project(self):
        selected_item = self.project_list.currentItem()
        if not selected_item:
            return

        project_name = selected_item.text()
        if project_name == self.current_project:
            self.kanban_board.clear_board()
            self.current_project = None

        self.project_list.takeItem(self.project_list.row(selected_item))
        del self.projects[project_name]

    def switch_project(self, item):
        #if self.current_project:
        #    self.save_current_project()

        project_name = item.text()
        self.focusme_control.set_current_project(self.focusme_data_model.get_project(item.text()))
        self.current_project = project_name
        # self.kanban_board.load_tasks(self.projects[project_name])
        self.kanban_board.updated_boards(self.focusme_data_model.get_project(project_name))


    def show_task_details(self, task_data):
        for key, widget in self.detail_fields.items():

            # value = task_data.get(key, "") FIXME
            value = task_data.taskname
            if isinstance(widget, QLineEdit):
                widget.setText(value)
            elif isinstance(widget, QDateEdit):
                widget.setDate(value)
            elif isinstance(widget, QComboBox):
                index = widget.findText(value)
                widget.setCurrentIndex(index if index >= 0 else 0)

    def save_task_details(self):
        # Speichere Task-Änderungen
        pass  # Implementiere Speichern-Logik hier
    
    def update_data_model(self,task):
        """_This is function is used as a callback function in KanbanBoard in
        order to update the global data model with new tasks added to the board_

        Args:
            task (_Task_): _Task information from an added task_
        """       
        proj = self.focusme_control.get_current_project()
        task.assigned_project = proj.name
        proj.add_task(task)
        add_task_to_db(self.db_conn, task)