import sys
from PySide6.QtWidgets import QApplication
from view.ui_main_window import MainWindow
from model.focusme_db import initialize_database
from model.focusme_model import FocusMeData
from control.focusme_control import FocusMeControl

def main():
    """_summary_
    """
    # Datenbank initialisieren
    db_conn=initialize_database(db_name="focusme2.db")
    focusme_data = FocusMeData()
    focusme_control = FocusMeControl()
    # Anwendung starten
    app = QApplication(sys.argv)
    window = MainWindow(focusme_data, focusme_control, db_conn)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
