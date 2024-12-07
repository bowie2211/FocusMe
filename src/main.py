import sys
from PySide6.QtWidgets import QApplication
from ui_main_window import MainWindow
from database import init_db
from model.focusme_model import FocusMeData
from control.focusme_control import FocusMeControl

def main():
    """_summary_
    """
    # Datenbank initialisieren
    init_db()
    focusme_data = FocusMeData()
    focusme_control = FocusMeControl()
    # Anwendung starten
    app = QApplication(sys.argv)
    window = MainWindow(focusme_data, focusme_control)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
