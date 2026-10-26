from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QProgressBar
from PySide6.QtCore import Qt

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Cover the viewport with a transparent dark overlay
        self.setStyleSheet("""
            LoadingOverlay {
                background-color: rgba(0, 0, 0, 130);
            }
        """)

        # Center the loading window
        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Modal-like panel
        self.panel = QWidget()
        self.panel.setFixedWidth(360)
        self.panel.setStyleSheet("""
            QWidget {
                background-color: #20252B;
                border: 1px solid #3A424C;
                border-radius: 12px;
            }
        """)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(24, 24, 24, 24)
        panel_layout.setSpacing(18)

        # Loading label
        self.label = QLabel("Loading mesh...")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #E6EAF0;
                background: transparent;
                border: none;
                font-size: 16px;
                font-weight: 500;
            }
        """)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #343B45;
                border: none;
                border-radius: 6px;
                text-align: center;
                color: white;
            }

            QProgressBar::chunk {
                background-color: #3984F5;
                border-radius: 6px;
            }
        """)

        panel_layout.addWidget(self.label)
        panel_layout.addWidget(self.progress_bar)

        outer_layout.addWidget(self.panel)

        self.hide()

    def set_progress(self, value):
        self.progress_bar.setValue(value)

    def set_message(self, message):
        self.label.setText(message)