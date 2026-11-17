# Construir con:  pyinstaller kiosko.spec --clean --noconfirm
import importlib.util

from PyInstaller.utils.hooks import collect_all

# Ponlo en False cuando compruebes que todo funciona (oculta la ventana negra en Windows).
CONSOLE = True

datas = [('assets', 'assets'), ('ui/common/styles.qss', 'ui/common')]
binaries = []
hiddenimports = []

# El cliente de Supabase carga varios paquetes de forma dinámica: se incluyen completos.
for pkg in ('supabase', 'postgrest', 'gotrue', 'supabase_auth', 'realtime',
            'storage3', 'supafunc', 'supabase_functions'):
    if importlib.util.find_spec(pkg):
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h

# NOTA: NO se incluye el teclado virtual de Qt (qtvirtualkeyboard). La app trae
# su propio teclado táctil (ui/common/touch_keyboard.py); si el plugin viajara
# en el build, el teclado de Qt podría asomar en cualquier diálogo de la Pi.

a = Analysis(
    ['main_cliente.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'PySide6.QtVirtualKeyboard'],
    noarchive=False,
)
# Por si algún hook de PyInstaller arrastrara piezas del teclado virtual de Qt
# (plugin IME, DLL y layouts QML), se descartan explícitamente del build.
a.binaries = [b for b in a.binaries if 'virtualkeyboard' not in b[0].lower()]
a.datas = [d for d in a.datas if 'virtualkeyboard' not in d[0].lower()]
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Kiosko',
    debug=False,
    strip=False,
    upx=False,
    console=CONSOLE,
    icon='assets/icono.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='Kiosko',
)