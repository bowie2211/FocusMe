Requirements FocusMe
####################


.. req:: Editing a task
    :id: EDIT_TASK

    Ich möchte in FocusME folgendes implementieren:
    Es gibt einen Bereich rechts in dem man bestimmte Attribute einer Task, die in einem der Kanban-Spalten angelickt ist ändern kann.
    Solange die Taks information nicht geändert wurde und Bder Information 
    in der Datenbank entspricht, soll der Pushbutton "Änderungen speichern" deaktiviert sein. Ändert man Daten 
    in den verschiedenen Textboxen oder Drop-Downs soll Änderungen speichern aktivierrt werden.
    Betätigt man Änderungen speichern sollen die Informationen in die FocusME Datenstruktur und 
    anschliessen übernommen werden und die Task mit den neuen Daten in der Datenbank aktualisiert werden.



.. needs:: Kanban-Item-Click
   :id: KANBAN_ITEM_CLICKED
   :status: implemented
   :tags: UI, Event

   Beschreibung der Anforderung.

   
    .. uml::
        participant User
        participant KanbanWidget
        participant TaskEditor
        participant Database

        User -> KanbanWidget: itemClicked()
        KanbanWidget -> TaskEditor: updateUI(task)
        TaskEditor -> Database: updateTask(task)
        Database -> TaskEditor: confirmation()



.. plantuml::

   @startuml
   participant User
   participant KanbanWidget
   participant TaskEditor
   participant Database

   User -> KanbanWidget: itemClicked()
   KanbanWidget -> TaskEditor: updateUI(task)
   TaskEditor -> Database: updateTask(task)
   Database -> TaskEditor: confirmation()
   @enduml