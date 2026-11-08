from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
import traceback


class _Signals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class _Task(QRunnable):
    def __init__(self, fn, *args):
        super().__init__()
        self.fn = fn
        self.args = args
        self.signals = _Signals()

    @Slot()
    def run(self):
        try:
            result = self.fn(*self.args)
        except Exception:
            traceback.print_exc()
            self.signals.failed.emit(traceback.format_exc())
        else:
            self.signals.finished.emit(result)



def run_async(fn, on_success, on_error=None, *args):
    """Ejecuta fn(*args) en otro hilo y llama a on_success(resultado) en la UI."""
    task = _Task(fn, *args)
    task.signals.finished.connect(on_success)
    if on_error:
        task.signals.failed.connect(on_error)
    QThreadPool.globalInstance().start(task)