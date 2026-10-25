from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication

import sys



def startWindow():
    app = QApplication(sys.argv)


    app.setStyleSheet("""
        /* Menu bar */
        QMenuBar {
            background-color: #151515;
            color: #DADADA;
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
            color: #DADADA;
            padding: 5px 10px;
            margin: 0px;
            border: none;
        }

        QMenuBar::item:selected {
            background-color: #303030;
            color: #FFFFFF;
        }

        QMenuBar::item:pressed {
            background-color: #383838;
        }

        /* Dropdown menu */
        QMenu {
            background-color: #1A1A1A;
            color: #DADADA;
            font-family: "Segoe UI";
            font-size: 12px;
            border: 1px solid #101010;
            padding: 4px 0px;
        }

        QMenu::item {
            background-color: transparent;
            color: #DADADA;
            padding: 5px 28px;
            margin: 0px;
            border: none;
            border-radius: 0px;
        }

        QMenu::item:selected {
            background-color: #365783;
            color: #FFFFFF;
        }

        QMenu::item:disabled {
            color: #666666;
        }

        QMenu::separator {
            height: 1px;
            background-color: #353535;
            margin: 4px 8px;
        }
    """)

    mainWindow = MainWindow()
    mainWindow.show()

    app.exec()


if __name__ == "__main__":
    startWindow()