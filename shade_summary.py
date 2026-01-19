from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QScrollArea,
    QWidget, QGridLayout, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class ShadeSummaryDialog(QDialog):
    def __init__(self, shade_name, image_paths, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Shade {shade_name} – Summary")
        self.setMinimumSize(800, 600)

        main_layout = QVBoxLayout(self)

        title = QLabel(f"Shade {shade_name} – All Captured Images")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:16px; font-weight:bold;")
        main_layout.addWidget(title)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(12)

        # Load images
        for i, path in enumerate(image_paths):
            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            pix = QPixmap(path).scaled(
                220, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            img_label.setPixmap(pix)
            grid.addWidget(img_label, i // 3, i % 3)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn, alignment=Qt.AlignCenter)
