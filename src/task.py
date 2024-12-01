from enum import Enum

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QDateEdit, QComboBox, QPushButton, QListWidget, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QDate


class RepeatEnum(Enum):
    NEVER = "Never"
    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"


class Task:
    def __init__(self, taskname="", estimated_pomos=0, date_to_perform=None, repeat=RepeatEnum.NEVER, assigned_to_project="", assigned_kanban = "Backlog", tag="", subtasks=None):
        self.taskname = taskname
        self.estimated_pomos = estimated_pomos
        self.date_to_perform = date_to_perform or QDate.currentDate().toString("dd.MM.yyyy")
        self.repeat = repeat
        self.assigned_to_project = assigned_to_project
        self.assigned_kanban = assigned_kanban
        self.tag = tag
        self.subtasks = subtasks or []

    def __repr__(self):
        return f"<Task(taskname={self.taskname}, estimated_pomos={self.estimated_pomos}, date_to_perform={self.date_to_perform}, repeat={self.repeat}, assigned_to_project={self.assigned_to_project}, tag={self.tag}, subtasks={self.subtasks})>"


class TaskInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Input Dialog")
        self.setModal(True)
        self.resize(400, 300)
        
        self.layout = QVBoxLayout(self)

        # Taskname
        self.layout.addWidget(QLabel("Task Name:"))
        self.taskname_edit = QLineEdit(self)
        self.layout.addWidget(self.taskname_edit)

        # Estimated Pomos
        self.layout.addWidget(QLabel("Estimated Pomos:"))
        self.pomos_spinbox = QSpinBox(self)
        self.pomos_spinbox.setMinimum(0)
        self.layout.addWidget(self.pomos_spinbox)

        # Date to Perform
        self.layout.addWidget(QLabel("Date to Perform:"))
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.layout.addWidget(self.date_edit)

        # Repeat
        self.layout.addWidget(QLabel("Repeat:"))
        self.repeat_combo = QComboBox(self)
        self.repeat_combo.addItems([e.value for e in RepeatEnum])
        self.layout.addWidget(self.repeat_combo)

        # Assigned to Project
        self.layout.addWidget(QLabel("Assigned to Project:"))
        self.project_edit = QLineEdit(self)
        self.layout.addWidget(self.project_edit)

        # Tag
        self.layout.addWidget(QLabel("Tag:"))
        self.tag_edit = QLineEdit(self)
        self.layout.addWidget(self.tag_edit)

        # Subtasks
        self.layout.addWidget(QLabel("Subtasks:"))
        self.subtasks_list = QListWidget(self)
        self.layout.addWidget(self.subtasks_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_subtask_button = QPushButton("Add Subtask")
        self.add_subtask_button.clicked.connect(self.add_subtask)
        button_layout.addWidget(self.add_subtask_button)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

    def add_subtask(self):
        subtask_name, ok = QInputDialog.getText(self, "Add Subtask", "Enter subtask name:")
        if ok and subtask_name.strip():
            self.subtasks_list.addItem(subtask_name.strip())

    def get_task(self, kanban_bucket):
        if self.exec() == QDialog.Accepted:
            subtasks = [self.subtasks_list.item(i).text() for i in range(self.subtasks_list.count())]
            return Task(
                taskname=self.taskname_edit.text().strip(),
                estimated_pomos=self.pomos_spinbox.value(),
                date_to_perform=self.date_edit.date().toString("dd.MM.yyyy"),
                repeat=RepeatEnum(self.repeat_combo.currentText()),
                assigned_to_project=self.project_edit.text().strip(),
                assigned_kanban=kanban_bucket,
                tag=self.tag_edit.text().strip(),
                subtasks=subtasks
            )
        return None