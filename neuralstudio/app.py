import sys
from PySide6.QtWidgets import QApplication
from neuralstudio.ui.main_window import MainWindow
def main():
    app=QApplication(sys.argv); app.setApplicationName("Neural Studio")
    window=MainWindow(); window.show(); return app.exec()
