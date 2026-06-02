from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel,
    QPushButton, QFileDialog,
    QHBoxLayout, QVBoxLayout, QProgressBar
)

from batch.processor import ProcessingWorker

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenBG")

        self.worker = None
        self.image_path = None

        self.init_ui()

    def init_ui(self):

        # LEFT PANEL
        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)

        self.batch_list = QLabel("Batch Queue: 0 images")

        left = QVBoxLayout()
        left.addWidget(self.load_btn)
        left.addWidget(self.batch_list)

        left_widget = QWidget()
        left_widget.setLayout(left)

        # PREVIEW AREA
        self.before_label = QLabel("Before")
        self.after_label = QLabel("After")

        preview = QHBoxLayout()
        preview.addWidget(self.before_label)
        preview.addWidget(self.after_label)

        preview_widget = QWidget()
        preview_widget.setLayout(preview)

        # ACTION BUTTONS
        self.process_btn = QPushButton("Remove Background")
        self.process_btn.clicked.connect(self.process_image)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_processing)

        self.progress = QProgressBar()

        actions = QHBoxLayout()
        actions.addWidget(self.process_btn)
        actions.addWidget(self.cancel_btn)

        # MAIN LAYOUT
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(preview_widget)

        root = QVBoxLayout()
        root.addLayout(main_layout)
        root.addLayout(actions)
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
            self.before_label.setText(file_path)

    # -------------------------
    # PROCESSING
    # -------------------------
    def process_image(self):

        if not self.image_path:
            return

        self.worker = ProcessingWorker(self.image_path)

        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.show_result)
        self.worker.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def show_result(self, path):
        self.after_label.setText(path)
        self.progress.setValue(100)

    def cancel_processing(self):
        if self.worker:
            self.worker.stop()