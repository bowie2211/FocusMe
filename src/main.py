import sys
from PySide6.QtWidgets import QApplication
from ui_main_window import MainWindow
from database import init_db

def main():
    # Datenbank initialisieren
    init_db()

    # Anwendung starten
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
