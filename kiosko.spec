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

a = Analysis(
    ['main_cliente.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
)
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