from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
import traceback
from datetime import datetime


class _Signals(QObject):
    finished = Signal(object)
    failed = Signal(str)


def _log_error(text: str) -> None:
    """Deja rastro del error en kiosko.log (junto al ejecutable) para depurar en la Pi."""
    try:
        import config
        log = config.BASE_DIR / "kiosko.log"
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}]\n{text}\n")
    except Exception:
        pass


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
            tb = traceback.format_exc()
            traceback.print_exc()
            _log_error(tb)
            self.signals.failed.emit(tb)
        else:
            self.signals.finished.emit(result)



def run_async(fn, on_success, on_error=None, *args):
    """Ejecuta fn(*args) en otro hilo y llama a on_success(resultado) en la UI."""
    task = _Task(fn, *args)
    task.signals.finished.connect(on_success)
    if on_error:
        task.signals.failed.connect(on_error)
    QThreadPool.globalInstance().start(task)