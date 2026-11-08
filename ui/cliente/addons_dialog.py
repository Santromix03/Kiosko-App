from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ui.common.widgets import format_price


class AddonsDialog(QDialog):
    """Pregunta qué adiciones quiere el cliente para un producto."""

    def __init__(self, product, addons, left_by_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adiciones")
        self.setModal(True)
        self.setMinimumWidth(480)
        self.product = product
        self._rows = []

        title = QLabel(product.name)
        title.setObjectName("AddonTitle")
        title.setWordWrap(True)
        subtitle = QLabel("¿Quieres agregarle algo?")
        subtitle.setObjectName("AddonSub")

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        for addon in addons:
            sold_out = left_by_id.get(addon.id, 0) < 1
            text = (f"{addon.name}  ·  Agotado" if sold_out
                    else f"{addon.name}  ·  +{format_price(addon.price)}")
            check = QCheckBox(text)
            check.setObjectName("AddonCheck")
            check.setEnabled(not sold_out)
            check.toggled.connect(self._update_total)
            layout.addWidget(check)
            self._rows.append((check, addon))

        self.total_label = QLabel()
        self.total_label.setObjectName("AddonTotal")
        self.total_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.total_label)

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancelar")
        cancel.setObjectName("ClearButton")
        cancel.setMinimumHeight(56)
        cancel.clicked.connect(self.reject)
        ok = QPushButton("Agregar al pedido")
        ok.setObjectName("ConfirmButton")
        ok.setMinimumHeight(56)
        ok.clicked.connect(self.accept)
        buttons.addWidget(cancel)
        buttons.addWidget(ok, 1)
        layout.addLayout(buttons)

        self._update_total()

    def selected_addons(self) -> tuple:
        return tuple(a for check, a in self._rows if check.isChecked())

    def _update_total(self):
        total = self.product.price + sum(a.price for a in self.selected_addons())
        self.total_label.setText(f"Total: {format_price(total)}")