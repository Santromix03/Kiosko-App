
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QButtonGroup, QGridLayout, QHBoxLayout, QLabel, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

import config
from core.cart import Cart
from core.models import CartItem
from core.workers import run_async
from services.catalog_service import get_addons, get_categories, get_products
from services.image_cache import download_image
from services.order_service import create_order
from services.printer_service import print_ticket
from services.ticket_renderer import render_ticket
from ui.cliente.addons_dialog import AddonsDialog
from ui.cliente.cart_panel import CartPanel
from ui.cliente.ticket_dialog import TicketDialog
from ui.cliente.tickets_dialog import TicketsDialog
from ui.common.widgets import CategoryButton, DragScroll, ProductCard

COLUMNS = 3


def _fetch_stock():
    products = get_products()
    for p in products:
        download_image(p.image_url)
    return products, get_addons()


def _fetch_menu():
    products, addons = _fetch_stock()
    return get_categories(), products, addons


class LongPressLabel(QLabel):
    """Etiqueta que avisa long_pressed si se mantiene presionada (acceso oculto)."""

    long_pressed = Signal()

    def __init__(self):
        super().__init__()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(2500)
        self._timer.timeout.connect(self.long_pressed.emit)

    def mousePressEvent(self, event):
        self._timer.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._timer.stop()
        super().mouseReleaseEvent(event)


class ClientWindow(QMainWindow):
    """Kiosco de pedidos. `exit_requested` pide volver al login de empleado."""

    exit_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.NOMBRE_LOCAL)
        self.cart = Cart()
        self.products = []
        self.addons = []
        self._modal_open = False
        self._current_category = None
        self._refreshing = False
        self._build_ui()
        run_async(_fetch_menu, self._on_loaded, self._on_error)

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._refresh_menu)
        self.refresh_timer.start(15000)  

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 8, 10, 10)
        root.setSpacing(8)

        title = LongPressLabel()
        title.setText(f"{config.NOMBRE_LOCAL.upper()} · TOMA TU PEDIDO")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignCenter)
        title.setCursor(Qt.PointingHandCursor)
        title.long_pressed.connect(self._open_printer_setup)

        # Fila superior: X de salida (vuelve al login) + título
        top = QHBoxLayout()
        top.setSpacing(8)
        self.btn_exit = QPushButton("X")
        self.btn_exit.setObjectName("ExitButton")
        self.btn_exit.setFixedSize(36, 36)
        self.btn_exit.setCursor(Qt.PointingHandCursor)
        self.btn_exit.setToolTip("Volver al login de empleado")
        self.btn_exit.clicked.connect(self.exit_requested.emit)
        top.addWidget(self.btn_exit)

        self.btn_tickets = QPushButton("Tickets")
        self.btn_tickets.setObjectName("TicketsButton")
        self.btn_tickets.setFixedHeight(36)
        self.btn_tickets.setCursor(Qt.PointingHandCursor)
        self.btn_tickets.setToolTip("Pedidos del día: imprimir o cancelar")
        self.btn_tickets.clicked.connect(self._open_tickets)
        top.addWidget(self.btn_tickets)

        top.addWidget(title, 1)
        root.addLayout(top)

        # Categorías (fila horizontal con scroll)
        category_host = QWidget()
        self.category_bar = QHBoxLayout(category_host)
        self.category_bar.setContentsMargins(0, 2, 0, 2)
        self.category_bar.setSpacing(8)
        self.category_group = QButtonGroup(self)
        self.category_group.setExclusive(True)

        self.cat_scroll = DragScroll(Qt.Horizontal)
        self.cat_scroll.setObjectName("CategoryScroll")
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setFrameShape(QScrollArea.NoFrame)
        self.cat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.cat_scroll.setFixedHeight(64)
        self.cat_scroll.setWidget(category_host)
        self.cat_scroll.watch_host(category_host)
        root.addWidget(self.cat_scroll)
        self._cat_buttons = {}

        body = QHBoxLayout()
        body.setSpacing(10)
        root.addLayout(body, 1)

        # Productos (centro)
        center = QVBoxLayout()
        body.addLayout(center, 1)

        self.status = QLabel("Cargando menú…")
        self.status.setAlignment(Qt.AlignCenter)
        center.addWidget(self.status)

        self.grid_scroll = DragScroll(Qt.Vertical)
        self.grid_scroll.setObjectName("ProductScroll")
        self.grid_scroll.setWidgetResizable(True)
        self.grid_scroll.setFrameShape(QScrollArea.NoFrame)
        self.grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid.setSpacing(10)
        self.grid_scroll.setWidget(self.grid_host)
        self.grid_scroll.watch_host(self.grid_host)
        center.addWidget(self.grid_scroll, 1)

        # Carrito (derecha)
        self.cart_panel = CartPanel(self.cart)
        self.cart_panel.confirm_requested.connect(self._confirm_order)
        body.addWidget(self.cart_panel)

    # --- carga de datos ---
    def _on_loaded(self, data):
        categories, products, addons = data
        self.products = products
        self.addons = addons
        self.status.hide()

        first_button, first_id = None, None
        for cat in categories:
            btn = CategoryButton(cat.name)
            btn.clicked.connect(lambda _=False, c=cat.id: self._select(c))
            self.category_group.addButton(btn)
            self.category_bar.addWidget(btn)
            self._cat_buttons[cat.id] = btn
            self.cat_scroll.watch(btn)
            if first_button is None:
                first_button, first_id = btn, cat.id
        self.category_bar.addStretch()

        if first_button:
            first_button.setChecked(True)
            self._show_category(first_id)

    def _on_error(self, message):
        self.status.setText(f"No se pudo cargar el menú: {message}")

    def _select(self, category_id):
        """Ignora los clicks que en realidad fueron arrastres de la fila."""
        if self.cat_scroll.dragging:
            return
        self._show_category(category_id)

    # --- productos ---
    def _clear_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _show_category(self, category_id):
        self._current_category = category_id
        btn = self._cat_buttons.get(category_id)
        if btn is not None:
            self.cat_scroll.ensureWidgetVisible(btn, 0, 0)
        self._clear_grid()
        items = [p for p in self.products if p.category_id == category_id]
        if not items:
            empty = QLabel("Próximamente")
            empty.setObjectName("EmptyLabel")
            self.grid.addWidget(empty, 0, 0)
            return
        for i, product in enumerate(items):
            card = ProductCard(product)
            card.clicked.connect(self._add_to_cart)
            self.grid_scroll.watch(card, "dragging_check")
            self.grid.addWidget(card, i // COLUMNS, i % COLUMNS)

    # --- carrito ---
      
    def _add_to_cart(self, product):
        reason = self.cart.blocked_reason(product)
        if reason:
            self.cart_panel.flash(reason)
            return

        addons = ()
        offered = [a for a in self.addons if product.category_id in a.category_ids]
        if any(self.cart.addon_left(a) >= 1 for a in offered):
            left = {a.id: self.cart.addon_left(a) for a in offered}
            dialog = AddonsDialog(product, offered, left, parent=self)
            self._modal_open = True
            try:
                accepted = dialog.exec()
            finally:
                self._modal_open = False
            if not accepted:
                return
            addons = dialog.selected_addons()

        reason = self.cart.blocked_reason(product, addons)   
        if reason:
            self.cart_panel.flash(reason)
            return
        self.cart.add(product, addons)
        self.cart_panel.refresh()

    def _confirm_order(self):
        # Copia de lo que se está pidiendo, para armar el ticket después
        self._snapshot = [CartItem(i.product, i.quantity, i.addons) for i in self.cart.items]
        self.centralWidget().setEnabled(False)   
        self.cart_panel.set_busy(True)
        run_async(create_order, self._on_order_ok, self._on_order_error, self.cart)

    def _on_order_ok(self, result):
        items = self._snapshot
        self.cart.clear()
        self.cart_panel.set_busy(False)
        self.cart_panel.refresh()
        self.centralWidget().setEnabled(True)

        image = render_ticket(result.ticket_number, items, result.total)
        self._last_ticket = result.ticket_number
        run_async(print_ticket, self._on_printed, self._on_print_error, image)

    def _on_printed(self, _):
        self._show_ticket(printed=True)

    def _on_print_error(self, message):
        # motivo corto (última línea del traceback) para mostrarlo al usuario
        lines = [ln.strip() for ln in message.splitlines() if ln.strip()]
        self._print_error = lines[-1] if lines else "Error desconocido"
        self._show_ticket(printed=False)

    def _show_ticket(self, printed, error=None):
        if printed:
            error = None
        TicketDialog(self._last_ticket, printed, error=error or getattr(self, "_print_error", None),
                     parent=self).exec()
        self._print_error = None

    # --- tickets del día (imprimir de nuevo / cancelar) ---
    def _open_tickets(self):
        if self._modal_open:
            return
        self._modal_open = True
        try:
            TicketsDialog(self).exec()
        finally:
            self._modal_open = False

    # --- panel oculto de impresora (mantener presionado el título) ---
    def _open_printer_setup(self):
        from ui.cliente.printer_setup import PrinterSetupDialog
        self._modal_open = True
        try:
            PrinterSetupDialog(self).exec()
        finally:
            self._modal_open = False

    def _on_order_error(self, message):
        self.cart_panel.set_busy(False)
        self.centralWidget().setEnabled(True)
        QMessageBox.warning(self, "Error", f"No se pudo enviar el pedido:\n{message}")

    # --- actualización periódica del stock ---
    def _refresh_menu(self):
        if self._refreshing or self._modal_open or not self.products:
            return
        self._refreshing = True
        run_async(_fetch_stock, self._on_refreshed, self._on_refresh_error)

    def _on_refreshed(self, data):
        self._refreshing = False
        if self._modal_open:
            return                      # se reintenta en el próximo ciclo
        products, addons = data
        if products == self.products and addons == self.addons:
            return
        self.products = products
        self.addons = addons
        changed = self.cart.sync(products, addons)
        self.cart_panel.refresh()
        if changed:
            self.cart_panel.flash("El stock cambió y ajustamos tu pedido")
        if self._current_category is not None:
            self._show_category(self._current_category)

    def _on_refresh_error(self, message):
        self._refreshing = False   # se reintenta en el próximo ciclo