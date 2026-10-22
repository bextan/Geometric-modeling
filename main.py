from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
from mesh_struct.mesh_converter import main

import sys


def startWindow():
    app = QApplication(sys.argv)


    app.setStyleSheet("""
        /* Menu bar */
        QMenuBar {
            background-color: #282828;
            color: #E6E6E6;
            font-family: "Segoe UI";
            font-size: 12px;
            font-weight: 400;
            padding: 0px;
            margin: 0px;
            border: none;
            spacing: 0px;
        }
    

        QMenuBar::item {
            background-color: transparent;
            color: #E6E6E6;
            padding: 5px 10px;
            margin: 0px;
            border: 0px;
            border-bottom: 0px;
        }

        QMenuBar::item:first {
            padding-left: 2px;
        }

        /* Hover and selected menu */
        QMenuBar::item:selected {
            background-color: #484848;
            color: #FFFFFF;
        }

        QMenuBar::item:pressed {
            background-color: #555555;
        }

        /* Dropdown menu */
        QMenu {
            background-color: #303030;
            color: #E6E6E6;
            font-family: "Segoe UI";
            font-size: 12px;
            border: 1px solid #202020;
            padding: 4px 0px;
        }

        QMenu::item {
            background-color: transparent;
            color: #E6E6E6;
            padding: 5px 28px;
            margin: 0px;
            border: none;
            border-radius: 0px;
        }

        QMenu::item:selected {
            background-color: #4772B3;
            color: #FFFFFF;
        }

        QMenu::item:disabled {
            color: #777777;
        }

        QMenu::separator {
            height: 1px;
            background-color: #484848;
            margin: 4px 8px;
        }
    """)

    mainWindow = MainWindow()
    mainWindow.show()

    app.exec()


if __name__ == "__main__":
    startWindow()
    # main()