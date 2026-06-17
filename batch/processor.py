from PySide6.QtCore import QThread, Signal
from engine.pipeline import remove_background

class ProcessingWorker(QThread):

    progress = Signal(int)
    progress_range = Signal(int, int)
    status = Signal(str)
    result_ready = Signal(str)
    error = Signal(str)

    def __init__(self, image_path):
        super().__init__()
        self.image_path = image_path
        self._running = True

    def run(self):

        try:
            self.progress_range.emit(0, 100)
            self.progress.emit(0)

            result = remove_background(self.image_path, self.report_progress)

            self.progress_range.emit(0, 100)
            self.progress.emit(100)
            self.result_ready.emit(result)

        except Exception as e:
            self.error.emit(str(e))

    def report_progress(self, update):
        self.status.emit(update.label)
        if update.busy:
            self.progress_range.emit(0, 0)
            return

        self.progress_range.emit(0, 100)
        self.progress.emit(update.percent)

    def stop(self):
        self._running = False
