import os
import cv2
from datetime import datetime
from collections import defaultdict

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QLineEdit, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTableWidget, QTableWidgetItem,
    QScrollArea, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap

from camera import Camera
from color_engine import extract_mean_rgb, rgb_to_lab
from data_store import add_roll, get_all_rolls
from grouping import assign_shade_groups
from report import generate_excel_report


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Shade Grouping – QC System")
        self.setGeometry(80, 60, 1450, 900)

        # ================= STATE =================
        self.buyer_name = ""
        self.contract_no = ""
        self.shade_boxes = {}   # shade -> QGroupBox
        self.shade_layouts = {} # shade -> QVBoxLayout

        # ================= PATHS =================
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.IMAGE_DIR = os.path.join(self.BASE_DIR, "IMAGES")
        os.makedirs(self.IMAGE_DIR, exist_ok=True)

        # ================= TOP HEADER =================
        self.buyer_input = QLineEdit()
        self.buyer_input.setPlaceholderText("Buyer Name")

        self.contract_input = QLineEdit()
        self.contract_input.setPlaceholderText("Contract No")

        self.lock_btn = QPushButton("Lock Lot")
        self.lock_btn.clicked.connect(self.lock_lot)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.buyer_input)
        header_layout.addWidget(self.contract_input)
        header_layout.addWidget(self.lock_btn)

        # ================= LIVE CAMERA =================
        self.image_label = QLabel("LIVE CAMERA")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(700, 480)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #ECEFF1;
                border: 2px solid #B0BEC5;
                font-weight: bold;
                color: #546E7A;
            }
        """)

        # ================= SHADE PREVIEW GRID =================
        self.gallery_container = QWidget()
        self.gallery_grid = QGridLayout()
        self.gallery_grid.setSpacing(12)
        self.gallery_container.setLayout(self.gallery_grid)

        self.gallery_scroll = QScrollArea()
        self.gallery_scroll.setWidgetResizable(True)
        self.gallery_scroll.setFixedWidth(380)
        self.gallery_scroll.setWidget(self.gallery_container)

        # ================= CENTER AREA =================
        center_layout = QHBoxLayout()
        center_layout.setSpacing(20)
        center_layout.addWidget(self.image_label, 3)
        center_layout.addWidget(self.gallery_scroll, 2)

        # ================= CONTROLS =================
        self.roll_input = QLineEdit()
        self.roll_input.setPlaceholderText("Roll Number")

        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.clicked.connect(self.capture_image)
        self.capture_btn.setEnabled(False)

        self.report_btn = QPushButton("Generate Report")
        self.report_btn.clicked.connect(self.generate_report)
        self.report_btn.setEnabled(False)

        button_style = """
        QPushButton {
            background-color: #1976D2;
            color: white;
            padding: 10px;
            border-radius: 4px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #1565C0;
        }
        QPushButton:disabled {
            background-color: #B0BEC5;
        }
        """
        self.capture_btn.setStyleSheet(button_style)
        self.report_btn.setStyleSheet(button_style)
        self.lock_btn.setStyleSheet(button_style)

        # Full width controls
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.roll_input)
        controls_layout.addWidget(self.capture_btn)
        controls_layout.addWidget(self.report_btn)

        # ================= TABLE =================
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Roll No", "ΔE", "Shade"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(260)

        # ================= MAIN LAYOUT =================
        main_layout = QVBoxLayout()
        main_layout.setSpacing(14)
        main_layout.addLayout(header_layout)
        main_layout.addLayout(center_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(main_layout)
        container.setStyleSheet("background-color: #F5F7FA;")
        self.setCentralWidget(container)

        # ================= CAMERA =================
        self.camera = Camera()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    # ==================================================
    def lock_lot(self):
        self.buyer_name = self.buyer_input.text().strip()
        self.contract_no = self.contract_input.text().strip()

        if not self.buyer_name or not self.contract_no:
            return

        self.buyer_input.setDisabled(True)
        self.contract_input.setDisabled(True)
        self.lock_btn.setDisabled(True)
        self.capture_btn.setEnabled(True)

    # ==================================================
    def update_frame(self):
        frame = self.camera.get_frame()
        if frame is None:
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)

        pixmap = QPixmap.fromImage(qimg).scaled(
            self.image_label.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(pixmap)

    # ==================================================
    def capture_image(self):
        roll_no = self.roll_input.text().strip()
        if not roll_no:
            return

        frame = self.camera.get_frame()
        if frame is None:
            return

        filename = f"{roll_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        path = os.path.join(self.IMAGE_DIR, filename)
        cv2.imwrite(path, frame)

        mean_rgb = extract_mean_rgb(path)
        lab = rgb_to_lab(mean_rgb)

        add_roll(roll_no, path, lab)
        rolls = get_all_rolls()
        grouped = assign_shade_groups(rolls, tolerance=1.5)
        last = grouped[-1]

        # ---- table ----
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(roll_no))
        self.table.setItem(r, 1, QTableWidgetItem(str(last["delta_e"])))
        self.table.setItem(r, 2, QTableWidgetItem(last["shade_group"]))

        # ---- gallery ----
        self.add_to_gallery(last["shade_group"], path)

        self.roll_input.clear()
        self.report_btn.setEnabled(True)

    # ==================================================
    def add_to_gallery(self, shade, image_path):
        if shade not in self.shade_boxes:
            box = QGroupBox(f"Shade {shade}")
            box.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #B0BEC5;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
            layout = QVBoxLayout()
            box.setLayout(layout)

            index = len(self.shade_boxes)
            row = index // 2
            col = index % 2
            self.gallery_grid.addWidget(box, row, col)

            self.shade_boxes[shade] = box
            self.shade_layouts[shade] = layout

        thumb = QLabel()
        thumb.setFixedSize(150, 110)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setStyleSheet("border: 1px solid #CFD8DC; background:#ECEFF1;")

        pix = QPixmap(image_path).scaled(
            140, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        thumb.setPixmap(pix)

        self.shade_layouts[shade].addWidget(thumb)

    # ==================================================
    def generate_report(self):
        report_dir = os.path.join(self.BASE_DIR, "REPORTS")
        os.makedirs(report_dir, exist_ok=True)

        path = os.path.join(report_dir, "shade_report.xlsx")
        generate_excel_report(
            path,
            buyer=self.buyer_name,
            contract=self.contract_no
        )

    def closeEvent(self, event):
        self.camera.release()
        event.accept()
