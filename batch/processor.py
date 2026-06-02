from PySide6.QtCore import QThread, Signal
from engine.pipeline import remove_background

class ProcessingWorker(QThread):

    progress = Signal(int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self._running = True

    def run(self):

        try:
            self.progress.emit(10)

            result = remove_background(self.image_path)

            self.progress.emit(100)

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._running = False