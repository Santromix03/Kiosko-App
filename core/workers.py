from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot
import traceback
from datetime import datetime


class _Signals(QObject):
    finished = Signal(object)
    failed = Signal(str)


class _Relay(QObject):
    """Reenvía el resultado de la tarea al hilo principal.

    El receptor de la señal de la tarea es un QObject del hilo principal,
    así que Qt entrega en COLA ahí: los callbacks de la UI nunca corren
    dentro del hilo del worker.
    """

    done = Signal(object)
    fail = Signal(str)

    def __init__(self, task):
        super().__init__()
        self._task = task          # mantiene viva la tarea hasta la entrega

    @Slot(object)
    def _on_done(self, result):
        try:
            self.done.emit(result)
        finally:
            _ACTIVE.discard(self)

    @Slot(str)
    def _on_fail(self, message):
        try:
            self.fail.emit(message)
        finally:
            _ACTIVE.discard(self)


# Referencias vivas: si la tarea queda solo como variable local de run_async,
# Python la recolecta y el resultado se pierde (aunque el hilo termine el trabajo).
_ACTIVE: set = set()


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
    """Ejecuta fn(*args) en otro hilo y llama a on_success(resultado) en el hilo principal.

    Si algo falla, llama a on_error(traza) y deja el error en kiosko.log.
    """
    task = _Task(fn, *args)
    relay = _Relay(task)
    task.signals.finished.connect(relay._on_done)
    task.signals.failed.connect(relay._on_fail)
    relay.done.connect(on_success)          # ya llega en el hilo principal
    if on_error is not None:
        relay.fail.connect(on_error)
    _ACTIVE.add(relay)
    QThreadPool.globalInstance().start(task)
