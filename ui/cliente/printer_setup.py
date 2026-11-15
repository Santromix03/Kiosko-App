import subprocess
import time
from datetime import datetime

from PIL import Image, ImageDraw
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QPushButton, QSpinBox, QVBoxLayout,
)

import config
from core.workers import run_async
from services.printer_service import image_to_raster


def _write_env(values: dict) -> None:
    """Reescribe las claves dadas en el .env junto al ejecutable, conservando el resto."""
    path = config.BASE_DIR / ".env"
    lines = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            key = line.split("=", 1)[0].strip()
            if key not in values:
                lines.append(line)
    lines += [f"{k}={v}" for k, v in values.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _scan_bluetooth():
    """Descubre dispositivos cercanos con bluetoothctl. Devuelve [(mac, nombre)]."""
    try:
        subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, timeout=15)
        time.sleep(8)                        # deja que la antena encuentre vecinos
        r = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True, timeout=10)
        subprocess.run(["bluetoothctl", "scan", "off"], capture_output=True, timeout=10)
    except FileNotFoundError:
        raise RuntimeError("bluetoothctl no está disponible en este sistema")
    devices = []
    for line in r.stdout.splitlines():
        if line.startswith("Device "):
            parts = line.split(" ", 2)
            if len(parts) >= 3:
                devices.append((parts[1], parts[2]))
    if not devices:
        raise RuntimeError("No se encontraron dispositivos Bluetooth cerca")
    return devices


def _pair_printer(mac: str):
    """Empareja y confía la impresora para que el kiosco pueda abrirle conexión."""
    out = []
    for cmd in (["bluetoothctl", "pair", mac], ["bluetoothctl", "trust", mac]):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            out.append((r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "")
        except FileNotFoundError:
            raise RuntimeError("bluetoothctl no está disponible en este sistema")
        except subprocess.TimeoutExpired:
            out.append("sin respuesta (¿ya está emparejada? pide confirmación en la impresora)")
    return "\n".join(x for x in out if x)


def _test_image() -> Image.Image:
    from services.ticket_renderer import _font
    w = config.PAPER_PX
    img = Image.new("L", (w, 190), 255)
    d = ImageDraw.Draw(img)
    d.text((14, 14), "PRUEBA DE IMPRESION", font=_font(True, 30), fill=0)
    d.text((14, 64), datetime.now().strftime("%Y-%m-%d %H:%M"), font=_font(False, 22), fill=0)
    d.text((14, 104), "Si lees esto, la impresora", font=_font(False, 22), fill=0)
    d.text((14, 138), "esta lista para usar.", font=_font(False, 22), fill=0)
    return img


def _send_test():
    """Prueba real según el modo elegido: bluetooth o guardar PNG."""
    from services import printer_service
    if config.PRINTER_MODE == "file":
        out_dir = config.BASE_DIR / "tickets"
        out_dir.mkdir(exist_ok=True)
        path = out_dir / f"prueba_{datetime.now():%Y%m%d_%H%M%S}.png"
        _test_image().save(path)
        return f"PNG guardado en {path}"
    printer_service._send_bluetooth(image_to_raster(_test_image()))
    return "Impreso correctamente"


class PrinterSetupDialog(QDialog):
    """Panel oculto del kiosco para configurar y probar la impresora."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de impresora")
        self.setModal(True)
        self.setMinimumSize(740, 460)

        title = QLabel("Impresora")
        title.setObjectName("AddonTitle")

        # --- modo y canal ---
        row1 = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.setObjectName("SetupCombo")
        self.mode.addItems(["bluetooth", "file"])
        self.mode.setCurrentText(config.PRINTER_MODE)
        self.channel = QSpinBox()
        self.channel.setObjectName("SetupCombo")
        self.channel.setRange(0, 30)
        self.channel.setValue(config.PRINTER_CHANNEL)
        self.channel.setSpecialValueText("auto (1-10)")
        row1.addWidget(QLabel("Modo:"))
        row1.addWidget(self.mode, 1)
        row1.addWidget(QLabel("Canal:"))
        row1.addWidget(self.channel)

        # --- MAC ---
        row2 = QHBoxLayout()
        self.mac = QLineEdit(config.PRINTER_MAC)
        self.mac.setObjectName("SetupInput")
        self.mac.setPlaceholderText("AA:BB:CC:DD:EE:FF")
        scan_btn = QPushButton("Escanear")
        scan_btn.setObjectName("ClearButton")
        scan_btn.setMinimumHeight(44)
        scan_btn.clicked.connect(self._scan)
        row2.addWidget(QLabel("MAC:"))
        row2.addWidget(self.mac, 1)
        row2.addWidget(scan_btn)

        self.devices = QListWidget()
        self.devices.setObjectName("SetupList")
        self.devices.itemClicked.connect(
            lambda item: self.mac.setText(item.text().split(" · ")[-1]))

        self.note = QLabel()
        self.note.setObjectName("SetupNote")
        self.note.setWordWrap(True)

        # --- acciones ---
        row3 = QHBoxLayout()
        pair_btn = QPushButton("Emparejar")
        pair_btn.setObjectName("ClearButton")
        pair_btn.setMinimumHeight(48)
        pair_btn.clicked.connect(self._pair)
        test_btn = QPushButton("Imprimir prueba")
        test_btn.setObjectName("ConfirmButton")
        test_btn.setMinimumHeight(48)
        test_btn.clicked.connect(self._test)
        row3.addWidget(pair_btn)
        row3.addWidget(test_btn, 1)

        row4 = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.setObjectName("ConfirmButton")
        save_btn.setMinimumHeight(48)
        save_btn.clicked.connect(self._save)
        close_btn = QPushButton("Cerrar")
        close_btn.setObjectName("ClearButton")
        close_btn.setMinimumHeight(48)
        close_btn.clicked.connect(self.reject)
        row4.addWidget(close_btn)
        row4.addWidget(save_btn, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addLayout(row1)
        layout.addLayout(row2)
        layout.addWidget(self.devices, 1)
        layout.addWidget(self.note)
        layout.addLayout(row3)
        layout.addLayout(row4)

    # --- helpers de UI ---
    def _busy(self, note: str):
        self.note.setText(note)
        self.setEnabled(False)

    def _done(self, note: str):
        self.setEnabled(True)
        self.note.setText(note)

    def _fail(self, message: str):
        lines = [ln.strip() for ln in message.splitlines() if ln.strip()]
        self.setEnabled(True)
        self.note.setText("⚠ " + (lines[-1] if lines else message))

    # --- acciones ---
    def _scan(self):
        self._busy("Escaneando Bluetooth… (unos 10 segundos)")
        run_async(_scan_bluetooth, self._on_scanned, self._fail)

    def _on_scanned(self, devices):
        if not self.isEnabled():
            return
        self.devices.clear()
        for mac, name in devices:
            self.devices.addItem(f"{name} · {mac}")
        self._done(f"{len(devices)} dispositivos. Toca uno para usar su MAC.")

    def _pair(self):
        mac = self.mac.text().strip()
        if not mac:
            self.note.setText("⚠ Escribe o elige una MAC primero")
            return
        self._busy(f"Emparejando {mac}… confirma si la impresora lo pide")
        run_async(_pair_printer, lambda out: self._done(out or "Listo"), self._fail, mac)

    def _test(self):
        self._busy("Enviando prueba…")
        run_async(_send_test, self._done, self._fail)

    def _save(self):
        mode = self.mode.currentText()
        mac = self.mac.text().strip().upper()
        channel = self.channel.value()
        _write_env({"PRINTER_MODE": mode, "PRINTER_MAC": mac, "PRINTER_CHANNEL": channel})

        # aplicar en vivo, sin reiniciar la app
        config.PRINTER_MODE = mode
        config.PRINTER_MAC = mac
        config.PRINTER_CHANNEL = channel
        import services.printer_service as ps
        ps._channel_cache = None

        self._done("Guardado en .env y aplicado. La release usará esta misma configuración.")
