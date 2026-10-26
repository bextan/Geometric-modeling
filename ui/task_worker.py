from PySide6.QtCore import QObject, Signal, Slot


class TaskWorker(QObject):
    progress = Signal(int, str)
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, task, *args, **kwargs):
        super().__init__()
        self.task = task
        self.args = args
        self.kwargs = kwargs

    @Slot()
    def run(self):
        try:
            result = self.task(
                *self.args,
                progress_callback=self.progress.emit,
                **self.kwargs
            )
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))