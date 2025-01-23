Sequence Diagrams
=================

Kanban Item Clicked 
###################


.. plantuml::

   @startuml
   participant User
   participant main
   participant CustomListWidget
   participant MainWindow
   participant FocusMeControl
   participant Project

   User -> main: itemClicked()
   main -> CustomListWidget: handle_item_clicked()
   CustomListWidget -> MainWindow: show_task_details()
   MainWindow -> FocusMeControl: get_current_project()
   MainWindow -> Project: get_task()
   Project --> MainWindow : Task
   @enduml


Initialize GUI
##############


.. plantuml::

   @startuml
   participant User
   participant main
   participant CustomListWidget
   participant MainWindow
   participant FocusMeControl
   participant Project
   User -> main: main()
   main -> focusme_db : initialize_database()
   focusme_db --> main:db_conn
   main -> focusme_db : generate_focusme_data_obj(db_conn)
   focusme_db --> main : FocusMeModel
   main -> FocusMeControl: __init__()
   FocusMeControl --> main: FocusMeControl 
   main -> main: set_current_project
   main -> main: set_current_task
   main -> QApplication
   QApplication --> main:app
   main -> MainWindow: __init__(focusme_data)
   MainWindow -> MainWindow: init_ui
   MainWindow --> main: window
   @enduml



get_project_by_name
###################  

.. plantuml::

   @startuml

title Sequenzdiagramm für get_project_by_name

actor User
participant focusme_db.py
participant SqliteDB as DB
participant "load_project_tasks_from_db" as LoadTasks
participant "generate_project_obj" as GenerateProject
participant "generate_task_obj" as GenerateTask

User -> focusme_db.py: get_project_by_name(project_name)
activate focusme_db.py

focusme_db.py -> DB: SELECT project_name
DB --> focusme_db.py: project_name

focusme_db.py -> LoadTasks: load_project_tasks_from_db(project_name, db_ref)
activate LoadTasks

LoadTasks -> DB: SELECT tasks WHERE project_name=project_name
DB --> LoadTasks: tasks_list
LoadTasks --> focusme_db.py: tasks_list

deactivate LoadTasks

focusme_db.py -> GenerateProject: generate_project_obj(project_name, tasks_list)
activate GenerateProject

GenerateProject -> GenerateTask: generate_task_obj(task)
activate GenerateTask

GenerateTask -> DB: SELECT subtasks WHERE task_id=task_id
DB --> GenerateTask: subtasks_list
GenerateTask --> GenerateProject: Task object with Subtask objects

deactivate GenerateTask

loop For each task in tasks_list
GenerateProject -> GenerateTask: generate_task_obj(task)
end

GenerateProject --> focusme_db.py: Project object

deactivate GenerateProject

focusme_db.py --> User: Project object

deactivate focusme_db.py

@enduml