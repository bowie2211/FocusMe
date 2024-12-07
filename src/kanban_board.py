from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt

class TaskDialog(QDialog):
    def __init__(self, task):
        super().__init__()
        self.setWindowTitle("Task Eigenschaften")
        self.setLayout(QFormLayout())

        # Anzeigen und Bearbeiten der Task-Eigenschaften
        self.fields = {}
        for field, value in task.items():
            if field == "Repeat":
                widget = QComboBox()
                widget.addItems(["never", "day", "week", "month"])
                widget.setCurrentText(value)
            elif field == "Date_to_Perform":
                widget = QDateEdit()
                widget.setDisplayFormat("dd.MM.yyyy")
                widget.setDate(value)
            else:
                widget = QLineEdit(value)
            self.fields[field] = widget
            self.layout().addRow(f"{field}:", widget)

        # Buttons für Speichern und Abbrechen
        save_btn = QPushButton("Speichern")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        self.layout().addWidget(save_btn)
        self.layout().addWidget(cancel_btn)

    def get_task_data(self):
        return {field: widget.text() if isinstance(widget, QLineEdit) else widget.currentText() for field, widget in self.fields.items()}


class KanbanBoard(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Spalten für Backlog, In Progress und Done
        self.columns = {
            "Backlog": self.create_column("Backlog"),
            "In Progress": self.create_column("In Progress"),
            "Done": self.create_column("Done"),
        }

        # Hinzufügen der Spalten
        for column in self.columns.values():
            self.layout.addWidget(column)

        # Task-Daten (als Beispiel)
        self.tasks = {}

    def create_column(self, title):
        column_widget = QWidget()
        column_layout = QVBoxLayout()
        column_widget.setLayout(column_layout)

        # Titel
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        column_layout.addWidget(title_label)

        # Liste für Tasks
        task_list = QListWidget()
        task_list.setAcceptDrops(True)
        task_list.setDragEnabled(True)
        task_list.dragEnterEvent = self.drag_enter_event
        task_list.dropEvent = self.drop_event
        column_layout.addWidget(task_list)

        # Button: Task hinzufügen
        add_task_btn = QPushButton(f"Task zu {title} hinzufügen")
        add_task_btn.clicked.connect(lambda: self.add_task(task_list, title))
        column_layout.addWidget(add_task_btn)

        return column_widget

    def add_task(self, list_widget, column_name):
        # Task hinzufügen
        task_name, ok = QLineEdit.getText(self, "Help", "Taskname:")
        if not ok or not task_name:
            return
        
        task_data = {
            "Taskname": task_name,
            "Estimated_Pomos": "0",
            "Date_to_Perform": "01.01.2024",
            "Repeat": "never",
            "Assigned_to_project": "",
            "Tag": "",
            "Subtasks": "",
        }

        item = QListWidgetItem(task_name)
        item.setData(Qt.UserRole, task_data)
        list_widget.addItem(item)
        self.tasks[task_name] = task_data

    def drag_enter_event(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def drop_event(self, event):
        # Task zwischen Spalten verschieben
        source_item = event.source().currentItem()
        task_data = source_item.data(Qt.UserRole)

        if not task_data:
            return

        # Task aus der Quellspalte entfernen
        source_widget = event.source()
        source_widget.takeItem(source_widget.currentRow())

        # Task in die Zielspalte einfügen
        target_widget = self.sender()
        item = QListWidgetItem(task_data["Taskname"])
        item.setData(Qt.UserRole, task_data)
        target_widget.addItem(item)

    def open_task_properties(self, item):
        task_data = item.data(Qt.UserRole)
        dialog = TaskDialog(task_data)
        if dialog.exec():
            updated_data = dialog.get_task_data()
            item.setData(Qt.UserRole, updated_data)
