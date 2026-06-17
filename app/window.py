from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel,
    QPushButton, QFileDialog, QMessageBox,
    QHBoxLayout, QVBoxLayout, QProgressBar,
    QFrame, QSizePolicy, QStyle
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImageReader, QPixmap
import os

from batch.processor import ProcessingWorker


class ImagePreview(QFrame):

    def __init__(self, title, placeholder):
        super().__init__()
        self.image_path = None
        self.pixmap = None

        self.setObjectName("previewCard")
        self.setFrameShape(QFrame.StyledPanel)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("previewTitle")

        self.image_label = QLabel(placeholder)
        self.image_label.setObjectName("imageCanvas")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setWordWrap(True)
        self.image_label.setMinimumSize(300, 320)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.meta_label = QLabel("No image selected")
        self.meta_label.setObjectName("previewMeta")
        self.meta_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(self.title_label)
        layout.addWidget(self.image_label, 1)
        layout.addWidget(self.meta_label)
        self.setLayout(layout)

    def set_image(self, path):
        self.image_path = path
        self.pixmap = QPixmap(path)

        if self.pixmap.isNull():
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Preview unavailable")
            self.meta_label.setText(os.path.basename(path))
            return

        self.image_label.setText("")
        self.meta_label.setText(self._metadata(path))
        self._refresh_pixmap()

    def clear(self, placeholder="Waiting for result"):
        self.image_path = None
        self.pixmap = None
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText(placeholder)
        self.meta_label.setText("No image selected")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_pixmap()

    def _refresh_pixmap(self):
        if not self.pixmap or self.pixmap.isNull():
            return

        size = self.image_label.contentsRect().size()
        if not size.isValid():
            return

        scaled = self.pixmap.scaled(
            size,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled)

    def _metadata(self, path):
        reader = QImageReader(path)
        size = reader.size()
        filename = os.path.basename(path)
        file_size = self._format_file_size(path)

        if size.isValid():
            return f"{filename} | {size.width()} x {size.height()} | {file_size}"

        return f"{filename} | {file_size}"

    def _format_file_size(self, path):
        try:
            size = os.path.getsize(path)
        except OSError:
            return "Unknown size"

        if size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"

        return f"{size / (1024 * 1024):.1f} MB"


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenBG")
        self.setGeometry(0, 0, 1100, 720) # x: int, y: int, w: int, h: int
        self.worker = None
        self.image_path = None

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #eef3f5;
            }
            QWidget {
                color: #1f2933;
                font-family: Segoe UI, Arial, sans-serif;
                font-size: 14px;
            }
            QLabel#appTitle {
                color: #111827;
                font-size: 28px;
                font-weight: 700;
            }
            QLabel#appSubtitle, QLabel#previewMeta, QLabel#statusLabel {
                color: #667085;
            }
            QLabel#previewTitle {
                color: #111827;
                font-size: 16px;
                font-weight: 700;
            }
            QWidget#sidebar {
                background: #ffffff;
                border: 1px solid #d7e0e5;
                border-radius: 8px;
            }
            QFrame#previewCard {
                background: #ffffff;
                border: 1px solid #d7e0e5;
                border-radius: 8px;
            }
            QLabel#imageCanvas {
                background: #111827;
                border: 1px solid #263241;
                border-radius: 6px;
                color: #d1d5db;
                padding: 18px;
            }
            QPushButton {
                background: #1f7a6d;
                border: none;
                border-radius: 6px;
                color: #ffffff;
                font-weight: 600;
                padding: 10px 14px;
            }
            QPushButton:hover {
                background: #17685d;
            }
            QPushButton:disabled {
                background: #b8c4ca;
                color: #ffffff;
            }
            QPushButton#secondaryButton {
                background: #ffffff;
                border: 1px solid #c7d3d9;
                color: #374151;
            }
            QPushButton#secondaryButton:hover {
                background: #f4f8f9;
            }
            QProgressBar {
                background: #dbe6ea;
                border: none;
                border-radius: 5px;
                height: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #e46f44;
                border-radius: 5px;
            }
        """)

        # LEFT PANEL
        title = QLabel("OpenBG")
        title.setObjectName("appTitle")

        self.load_btn = QPushButton("Load Image")
        self.load_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.load_btn.clicked.connect(self.load_image)

        self.batch_list = QLabel("No image loaded")
        self.batch_list.setObjectName("appSubtitle")
        self.batch_list.setWordWrap(True)

        left = QVBoxLayout()
        left.setContentsMargins(18, 18, 18, 18)
        left.setSpacing(14)
        left.addWidget(title)
        left.addWidget(self.load_btn)
        left.addWidget(self.batch_list)
        left.addStretch(1)

        left_widget = QWidget()
        left_widget.setObjectName("sidebar")
        left_widget.setFixedWidth(260)
        left_widget.setLayout(left)

        # PREVIEW AREA
        self.before_preview = ImagePreview("Source", "Load an image to preview it here")
        self.after_preview = ImagePreview("Result", "Waiting for result")

        preview = QHBoxLayout()
        preview.setSpacing(16)
        preview.addWidget(self.before_preview)
        preview.addWidget(self.after_preview)

        preview_widget = QWidget()
        preview_widget.setLayout(preview)

        # ACTION BUTTONS
        self.process_btn = QPushButton("Remove Background")
        self.process_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.process_btn.clicked.connect(self.process_image)
        self.process_btn.setEnabled(False)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.cancel_btn.clicked.connect(self.cancel_processing)
        self.cancel_btn.setEnabled(False)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)

        self.status_label = QLabel("Choose an image to begin")
        self.status_label.setObjectName("statusLabel")

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch(1)
        actions.addWidget(self.process_btn)
        actions.addWidget(self.cancel_btn)

        # MAIN LAYOUT
        main_layout = QHBoxLayout()
        main_layout.setSpacing(18)
        main_layout.addWidget(left_widget)
        main_layout.addWidget(preview_widget, 1)

        root = QVBoxLayout()
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)
        root.addLayout(main_layout)
        root.addLayout(actions)
        root.addWidget(self.status_label)
        root.addWidget(self.progress)

        container = QWidget()
        container.setLayout(root)

        self.setCentralWidget(container)

    # -------------------------
    # FILE LOADING
    # -------------------------
    def load_image(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if file_path:
            self.image_path = file_path
            self.before_preview.set_image(file_path)
            self.after_preview.clear()
            self.batch_list.setText(os.path.basename(file_path))
            self.status_label.setText("Ready to remove background")
            self.progress.setRange(0, 100)
            self.progress.setValue(0)
            self.process_btn.setEnabled(True)

    # -------------------------
    # PROCESSING
    # -------------------------
    def process_image(self):

        if not self.image_path:
            return

        self.worker = ProcessingWorker(self.image_path)

        self.worker.progress.connect(self.update_progress)
        self.worker.progress_range.connect(self.update_progress_range)
        self.worker.status.connect(self.update_status)
        self.worker.result_ready.connect(self.show_result)
        self.worker.error.connect(self.show_error)
        self.worker.start()

        self.after_preview.clear("Processing result")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_label.setText("Preparing image")
        self.process_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)

    def update_progress(self, value):
        self.progress.setValue(value)

    def update_progress_range(self, minimum, maximum):
        self.progress.setRange(minimum, maximum)

    def update_status(self, message):
        self.status_label.setText(message)

    def show_result(self, path):
        self.after_preview.set_image(path)
        self.status_label.setText("Background removed")
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.process_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.worker = None

    def show_error(self, message):
        print(f"processing error: {message}")
        QMessageBox.critical(self, "Processing Error", message)
        self.status_label.setText("Processing failed")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.process_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.worker = None

    def cancel_processing(self):
        if self.worker:
            self.worker.stop()
            self.status_label.setText("Cancel requested")
            self.cancel_btn.setEnabled(False)
            self.process_btn.setEnabled(True)
