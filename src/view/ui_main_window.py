from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QListWidgetItem, 
    QInputDialog, QLabel,
    QLineEdit, QComboBox, QDateEdit, QFormLayout, QMenuBar, QMenu, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt, QMimeData, Signal, QDate
from PySide6.QtGui import QDrag
from model.focusme_model import Project, Task, KanbanBoardColumns, RepeatEnum
from model.focusme_db import add_project_to_db, add_task_to_db, update_task_in_db

class KanbanBoard(QWidget):
    """
    Class dealing with kanbanboard features like adding task to
    different columns and drag and drop btw.
    the columns
    """    
    def __init__(self, add_task_callback):
        """
        Constructor of KanbanBoard
        
        Args:
            add_task_callback (function reference): a callback function in MainWindow to update data

        Returns:
            nothing
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

    def create_column(self, title):
        """
        Creates a kanbanboard column

        Args:
            title (string): title of kanbanboard column

        Returns:
            Complete kanbanboard column with ListWidget and pushbuttons
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
        #save list widget for later access (e.g. delete entries)
        column_widget.list_widget = list_widget 
        return column_widget

    def add_task(self, list_widget, column_name):
        """
        Adds a new task to the specified list widget and assigns it to the given kanban swimlane.
        Args:
            list_widget (QListWidget): The list widget to which the new task will be added.
            column_name (str): The name of the kanban swimlane to which the task will be assigned.
        Creates:
            Task: A new task with default values and assigns it to the specified kanban swimlane.
        Side Effects:
            Adds the new task to the provided list widget and calls the add_task_callback function
            to handle additional logic for adding the task to the correct project and kanban lane.
        """
        

        task = Task(
                id=None,
                taskname="Enter Taskname",
                description="Enter Description",
                estimated_pomodoros=0,
                date_to_perform="dd.MM.yyyy",
                repeat=RepeatEnum.NEVER.value,
                assigned_project="NA",
                assigned_kanban_swimlane=column_name,
                tag="",
                subtasks=[]
                )
        item = QListWidgetItem(task.taskname)
        item.setData(Qt.UserRole, task)
        list_widget.addItem(item)
        #this is a callback function call that adds the new task
        #the the correct project and kanban_lane.
        self.add_task_callback(task)
        

    def updated_boards(self, project):
        """
        Method is called during a drag and drop action.
        Clears all kanbanboard list widgets
        and populates with new (post drag and drop)
        setting
        
        Args:
            project (string): project name
        """
        
         # Step 1: delete old entries and add new entries 
        for column_widget in self.columns.values():
            column_widget.list_widget.clear()  # clear elements in the list widgets
            for task in project.tasks[column_widget.list_widget.column_name]:
                item = QListWidgetItem(task.taskname)
                item.setData(Qt.UserRole, task)
                column_widget.list_widget.addItem(item)


class CustomListWidget(QListWidget):
    """
    Class for a kanbanboard task list with drag and dropfeature
    """
    #definition of a signal which provides string for clicked item
    #the string is a name of a task
    itemClickedSignal = Signal(str, str)
    def __init__(self, column_name, board):
        super().__init__()
        self.column_name = column_name
        self.board = board
        self.itemClicked.connect(self.handle_item_clicked)

    def handle_item_clicked(self, item):
        """
        Method is connected to itemClicked signal from list widget
        and emits item clicked signal with task name and kanbanboard
        column information.
        This specific signal is used in MainWindow to update detailed
        task information, when task selection has changed.

        Args:
            item (QListItem): Clicked item in list
        """        
        self.itemClickedSignal.emit(item.text(),self.column_name)

    def startDrag(self, supportedActions):
        """
        Part of Drag&Drop feature

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
            self.move_task_to_column(task_name, source_column)
            event.acceptProposedAction()

    def move_task_to_column(self, task_name, source_column):
        # Add the task to the destination column
        item = QListWidgetItem(task_name)
        self.addItem(item) #self is end point (target List Widget) of the drag&drop action
        # Remove the task from the source column's internal data
        parent_lane__list_widget = self.board.columns[source_column].list_widget
        for index in range(parent_lane__list_widget.count()):
            item = parent_lane__list_widget.item(index)
            if item.text() == task_name:
                parent_lane__list_widget.takeItem(index)
                del item
                break

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
        self.init_ui()

    def init_ui(self):
        """
        Set the FocusMe UI elements (without populating data) 
        """
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Menu
        menu_bar = QMenuBar()
        file_menu = QMenu("Datei", self)
        menu_bar.addMenu(file_menu)
        edit_menu = QMenu("Bearbeiten", self)
        menu_bar.addMenu(edit_menu)
        layout.addWidget(menu_bar)

        # Main area with project list, kanban and task ui
        main_area = QHBoxLayout()
        layout.addLayout(main_area)

        project_layout = QVBoxLayout()

        self.project_list_q_widget = QListWidget()
        self.project_list_q_widget.itemClicked.connect(self.switch_project)
        project_layout.addWidget(self.project_list_q_widget)

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
        for col in KanbanBoardColumns:
            self.kanban_board.columns[col.value].list_widget.itemClickedSignal.connect(self.show_task_details)
        
        # right side if GUI with task details
        self.details_panel = QWidget()
        details_layout = QFormLayout()
        self.details_panel.setLayout(details_layout)

        self.detail_fields = {
            "Taskname": QLineEdit(),
            "Description":QTextEdit(),
            "Estimated_Pomos": QLineEdit(),
            "Date_to_Perform": QDateEdit(),
            "Repeat": QComboBox(),
            "Assigned_to_project": QLineEdit(),
            "Tag": QLineEdit(),
            "Subtasks":QListWidget()

            #"Subtasks": QLineEdit(),
        }

        self.detail_fields["Repeat"].addItems(
            ["never", "day", "week", "month"])

        for key, widget in self.detail_fields.items():
            details_layout.addRow(QLabel(key), widget)

        # Subtasks Section
        add_subtask_btn = QPushButton("Add Subtask")
        add_subtask_btn.clicked.connect(self.add_subtask)
        
        # Füge die Subtasks-Liste und den Button in das Layout ein
        details_layout.addRow(QLabel("Subtasks"), self.detail_fields["Subtasks"])
        details_layout.addRow("", add_subtask_btn)  # Leerzeichen als Label
        
        #self.subtasks_container = QWidget()
        #self.subtasks_container_layout = QVBoxLayout()
        #self.subtasks_container.setLayout(self.subtasks_container_layout)
        #self.subtasks_layout.addWidget(self.subtasks_container)

        #details_layout.addRow(QLabel("Subtasks"), self.subtasks_layout)
        
        self.detail_fields["Taskname"].textChanged.connect(self.check_for_changes)
        self.detail_fields["Description"].textChanged.connect(self.check_for_changes)
        self.detail_fields["Estimated_Pomos"].textChanged.connect(self.check_for_changes)
        self.detail_fields["Date_to_Perform"].dateChanged.connect(self.check_for_changes)
        self.detail_fields["Repeat"].currentIndexChanged.connect(self.check_for_changes) 
        self.detail_fields["Assigned_to_project"].textChanged.connect(self.check_for_changes)
        self.detail_fields["Tag"].textChanged.connect(self.check_for_changes)
        self.detail_fields["Subtasks"].itemChanged.connect(self.check_for_changes)
        
        """ self.save_task_btn = QPushButton("Änderungen speichern")
        self.save_task_btn.clicked.connect(self.save_task_details)
        self.save_task_btn.setDisabled(True)
        details_layout.addRow(self.save_task_btn) """

        main_area.addWidget(self.details_panel, 2)
        if self.focusme_control.get_current_project():
            self.populate_ui()

    def check_for_changes(self):
        """
        Checks if one of the edit field of task details has been changed.
        This method is the slot for the "Changed" signals of the ui elements for the 
        detailed task ui.
        It is checked if the current content of each the task dtetails edit ui is different to
        what is currently stored in focusme data model.
        The check is done by using the sender information.
        If a difference btw. content of ui element and focusme data model 
        is detected in any of the editable elements, the informetion from the ui element is
        pushed to the focusme data model and directly to the database.
        """
        sender = self.sender()
        has_changes = False
        if sender == self.detail_fields["Taskname"]:
            has_changes = self.detail_fields["Taskname"].text() != self.focusme_control.get_current_task().taskname
            if has_changes is True:
                self.focusme_control.get_current_task().taskname = self.detail_fields["Taskname"].text()
                self.kanban_board.updated_boards(self.focusme_control.get_current_project())
 
        if sender == self.detail_fields["Description"]:
            has_changes = self.detail_fields["Description"].toPlainText() != self.focusme_control.get_current_task().description
            if has_changes is True:
                self.focusme_control.get_current_task().description = self.detail_fields["Description"].toPlainText()
 
        if sender == self.detail_fields["Estimated_Pomos"]:
            has_changes = self.detail_fields["Estimated_Pomos"].text() != str(self.focusme_control.get_current_task().estimated_pomodoros)
            if has_changes is True:
                self.focusme_control.get_current_task().estimated_pomodoros = int(self.detail_fields["Estimated_Pomos"].text())
                
        if sender == self.detail_fields["Date_to_Perform"]:
            has_changes = self.detail_fields["Date_to_Perform"].date().toString("dd.MM.yyyy") != self.focusme_control.get_current_task().date_to_perform
            if has_changes is True:
                self.focusme_control.get_current_task().date_to_perform = self.detail_fields["Date_to_Perform"].date().toString("dd.MM.yyyy")
        
        if sender == self.detail_fields["Repeat"]:     
            has_changes = self.detail_fields["Repeat"].currentText() != self.focusme_control.get_current_task().repeat
            if has_changes is True:
                self.focusme_control.get_current_task().repeat = has_changes = self.detail_fields["Repeat"].currentText()
 
        if sender == self.detail_fields["Assigned_to_project"]:
            has_changes = self.detail_fields["Assigned_to_project"].text() != self.focusme_control.get_current_task().assigned_project
            if has_changes is True:
                self.focusme_control.get_current_task().assigned_project = self.detail_fields["Assigned_to_project"].text()
        
        if sender == self.detail_fields["Tag"]:
            has_changes = self.detail_fields["Tag"].text() != self.focusme_control.get_current_task().tag
            if has_changes is True:
                self.focusme_control.get_current_task().tag = self.detail_fields["Tag"].text()
        
        if sender == self.detail_fields["Subtasks"]:
            print("Subtask changed")
        
        if has_changes is True:
            update_task_in_db(self.db_conn, self.focusme_control.get_current_task())

    def populate_ui(self):
        """
        Populates the UI with the list of projects and sets the focus on the current project.
        This method performs the following actions:
        1. Iterates through the projects in the focusme_data_model and adds each project's name to the project_list_q_widget.
        2. Sets the focus on the current project in the project_list_q_widget.
        3. Updates the kanban board with the current project's data.
        Returns:
            None
        """
        
        for project in self.focusme_data_model.projects:

            self.project_list_q_widget.addItem(project.name)
        #set focus on current project
        for index in range(self.project_list_q_widget.count()):
            item = self.project_list_q_widget.item(index)
            if item.text() == self.focusme_control.get_current_project().name:
                self.project_list_q_widget.setCurrentItem(item)
                self.project_list_q_widget.setFocus()
        self.kanban_board.updated_boards(self.focusme_control.get_current_project())
    
    def add_project(self):
        project_name, ok = QInputDialog.getText(
            self, "Projekt hinzufügen", "Projektname:")
        if ok and project_name:
            self.project_list_q_widget.addItem(project_name)
            self.focusme_data_model.add_project(Project(project_name))
            self.focusme_control.set_current_project(self.focusme_data_model.get_project(project_name)) 
            add_project_to_db(self.db_conn, self.focusme_data_model.get_project(project_name))

    def delete_project(self):
        selected_item = self.project_list_q_widget.currentItem()
        if not selected_item:
            return

        project_name = selected_item.text()
        if project_name == self.current_project:
            self.kanban_board.clear_board()
            self.current_project = None

        self.project_list_q_widget.takeItem(self.project_list_q_widget.row(selected_item))
        del self.projects[project_name]

    def switch_project(self, item):
        project_name = item.text()
        self.focusme_control.set_current_project(self.focusme_data_model.get_project(item.text()))
        self.current_project = project_name
        self.kanban_board.updated_boards(self.focusme_data_model.get_project(project_name))


    def show_task_details(self, task_name,  assigned_kanban_swimlane):
        curr_proj = self.focusme_control.get_current_project()
        self.focusme_data_model.get_project(curr_proj)
        task_data=curr_proj.get_task(task_name, assigned_kanban_swimlane)
        self.focusme_control.set_current_task(task_data)
        self.detail_fields["Taskname"].setText(task_data.taskname)
        self.detail_fields["Estimated_Pomos"].setText(str(task_data.estimated_pomodoros))
        self.detail_fields["Date_to_Perform"].setDate(QDate.fromString(task_data.date_to_perform, "dd.MM.yyyy"))
        index = self.detail_fields["Repeat"].findText(task_data.repeat)
        self.detail_fields["Repeat"].setCurrentIndex(index if index >= 0 else 0)
        self.detail_fields["Assigned_to_project"].setText(task_data.assigned_project)
        self.detail_fields["Description"].setPlainText(task_data.description)
        

    def save_task_details(self):
        print("Save Data")
        # Speichere Task-Änderungen
        pass  # Implementiere Speichern-Logik hier
    
    def update_data_model(self,task):
        """
        This is function is used as a callback function in KanbanBoard in
        order to update the global data model with new tasks added to the board

        Args:
            task (Task): Task information from an added task_
        """
        proj = self.focusme_control.get_current_project()
        task.assigned_project = proj.name
        proj.add_task(task)
        add_task_to_db(self.db_conn, task)
        self.show_task_details(task.taskname, task.assigned_kanban_swimlane)


    
        
    def add_subtask(self):
        """
        Fügt einen neuen Subtask zur Liste hinzu.
        """
        # Neues benutzerdefiniertes Widget für den Subtask
        subtask_widget = QWidget()
        subtask_layout = QHBoxLayout(subtask_widget)
        subtask_layout.setContentsMargins(0, 0, 0, 0)  # Entfernt unnötige Ränder

        # Checkbox und editierbares Textfeld
        checkbox = QCheckBox()
        text_edit = QLineEdit()
        text_edit.setPlaceholderText("Enter subtask name...")

        # Füge Checkbox und Textfeld zum Layout hinzu
        subtask_layout.addWidget(checkbox)
        subtask_layout.addWidget(text_edit)

        # Überwache Änderungen
        checkbox.stateChanged.connect(self.subtask_on_checkbox_changed)
        text_edit.textChanged.connect(self.subtask_on_text_changed)

        
        # Neues Listenelement für die Subtask-Liste
        list_item = QListWidgetItem(self.detail_fields["Subtasks"])
        self.detail_fields["Subtasks"].addItem(list_item)

        # Setze das benutzerdefinierte Widget als Inhalt des Listenelements
        list_item.setSizeHint(subtask_widget.sizeHint())
        self.detail_fields["Subtasks"].setItemWidget(list_item, subtask_widget)

    def subtask_on_checkbox_changed(self, state):
        """
        Wird aufgerufen, wenn der Status der Checkbox geändert wird.
        """
        checkbox = self.sender()
        list_item = self.detail_fields["Subtasks"].itemAt(checkbox.pos())
        print(f"Checkbox changed at position {checkbox.pos()}")
    
    def subtask_on_text_changed(self, text):
        """
        Wird aufgerufen, wenn der Text des Subtasks geändert wird.
        """
        text_edit = self.sender()
        list_item = self.detail_fields["Subtasks"].itemAt(text_edit.pos())
        print(f"Text changed at position {text_edit.pos()}")