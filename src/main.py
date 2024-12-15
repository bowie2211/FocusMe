import sys
from PySide6.QtWidgets import QApplication
from view.ui_main_window import MainWindow
from model.focusme_db import initialize_database, generate_focusme_data_obj
from control.focusme_control import FocusMeControl

def main():
    """_summary_
    """
    # initialize database
    db_conn=initialize_database(db_name="focusme2.db")
    
    focusme_data = generate_focusme_data_obj(db_conn)
    focusme_control = FocusMeControl()
    focusme_control.set_current_project(focusme_data.projects[0])
    # start application
    app = QApplication(sys.argv)
    window = MainWindow(focusme_data, focusme_control, db_conn)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
