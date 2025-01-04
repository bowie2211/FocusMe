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
