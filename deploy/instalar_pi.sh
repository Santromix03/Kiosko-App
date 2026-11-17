#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║  CAFEMAFE KIOSKO — instalador para Raspberry Pi              ║
# ║                                                              ║
# ║  Uso:                                                        ║
# ║    ./instalar_pi.sh [carpeta_del_release]                    ║
# ║    ./instalar_pi.sh --desinstalar                            ║
# ║                                                              ║
# ║  Qué hace:                                                   ║
# ║   1. Copia la app del release a ~/Kiosko                     ║
# ║   2. Prepara el .env (y activa pantalla completa)            ║
# ║   3. Crea el lanzador que mantiene la pantalla encendida     ║
# ║   4. Registra la app para abrir sola al encender la Pi       ║
# ║   5. Verifica el grupo bluetooth para la impresora           ║
# ╚══════════════════════════════════════════════════════════════╝
set -euo pipefail

ROJO='\033[1;31m'; VERDE='\033[1;32m'; AMAR='\033[1;33m'; AZUL='\033[1;34m'; NORM='\033[0m'
info()  { echo -e "  ${AZUL}»${NORM} $1"; }
ok()    { echo -e "  ${VERDE}✔${NORM} $1"; }
warn()  { echo -e "  ${AMAR}!${NORM} $1"; }
die()   { echo -e "  ${ROJO}✖ $1${NORM}"; exit 1; }

banner() {
echo -e "${ROJO}"
cat <<'BANNER'
   ____  ___  ____   __  __ ___ _   _
  / ___|/ _ \|  _ \ |  \/  |_ _| \ | |
 | |   | | | | |_) || |\/| || |  \| |
 | |___| |_| |  _ < | |  | || | |\  |
  \____|\___/|_| \_\|_|  |_|___|_| \_|
         kiosco de pedidos · installer
BANNER
echo -e "${NORM}"
}

# ---- desinstalar -------------------------------------------------------------
if [[ "${1:-}" == "--desinstalar" ]]; then
    banner
    if [ -f "$HOME/Kiosko/.env" ]; then
        cp "$HOME/Kiosko/.env" "$HOME/kiosko.env.bak"
        ok "Guardé una copia de tu .env en $HOME/kiosko.env.bak"
    fi
    rm -rf "$HOME/Kiosko" "$HOME/.config/autostart/kiosko.desktop"
    ok "Kiosco desinstalado"
    exit 0
fi

# ---- Validaciones ------------------------------------------------------------
[[ $EUID -eq 0 ]] && die "No lo corras como root/sudo: se instala en tu carpeta personal."

SRC="${1:-$PWD/Kiosko}"
[ -d "$SRC" ] || die "No encuentro el release. Descomprime Kiosko-vX.Y.Z-linux-arm64.tar.gz y ejecuta:
       ./instalar_pi.sh /ruta/carpeta/descomprimida"

APP_DIR="$HOME/Kiosko"
banner
info "Origen del release: $SRC"
echo

# ---- 1) Copiar la app --------------------------------------------------------
info "Copiando la aplicación a $APP_DIR…"
mkdir -p "$APP_DIR"
cp -a "$SRC"/. "$APP_DIR"/
chmod +x "$APP_DIR/Kiosko" 2>/dev/null || true
ok "Aplicación instalada en $APP_DIR"

# ---- 2) .env -----------------------------------------------------------------
if [ ! -f "$APP_DIR/.env" ]; then
    cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    warn "Se creó $APP_DIR/.env desde la plantilla: ábrelo y pon tus claves de Supabase."
    warn "Las credenciales de la impresora las pones luego en el panel oculto de la app."
else
    ok ".env ya existe, se respeta tal cual"
fi
grep -q '^KIOSK_FULLSCREEN=' "$APP_DIR/.env" 2>/dev/null || \
    echo "KIOSK_FULLSCREEN=1" >> "$APP_DIR/.env"

# ---- 3) Lanzador (pantalla completa + pantalla siempre encendida) -------------
info "Creando lanzador…"
cat > "$APP_DIR/iniciar_kiosko.sh" <<EOF
#!/usr/bin/env bash
# Lanzador del kiosco (generado por instalar_pi.sh)
cd "$APP_DIR"
export KIOSK_FULLSCREEN=1

# pantalla encendida siempre: sin salvapantallas, sin atenuar, sin apagado
xset s off        2>/dev/null || true
xset s noblank    2>/dev/null || true
xset -dpms        2>/dev/null || true

# registro de salida para depurar si algo raro pasa
exec ./Kiosko >> "$HOME/kiosko_salida.log" 2>&1
EOF
chmod +x "$APP_DIR/iniciar_kiosko.sh"
ok "Lanzador en $APP_DIR/iniciar_kiosko.sh"

# ---- 4) Arranque automático al encender ---------------------------------------
info "Configurando arranque automático al encender la Pi…"
mkdir -p "$HOME/.config/autostart"
cat > "$HOME/.config/autostart/kiosko.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Kiosko Cafemafe
Comment=Kiosco de pedidos (arranque automático)
Exec=$APP_DIR/iniciar_kiosko.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
ok "La app abrirá sola al encender (pantalla completa)"

# ---- 5) Bluetooth -------------------------------------------------------------
if id -nG "$USER" 2>/dev/null | grep -qw bluetooth; then
    ok "Tu usuario pertenece al grupo 'bluetooth'"
else
    warn "Tu usuario NO está en el grupo 'bluetooth'. Ejecuta:"
    echo   -e "       ${AMAR}sudo usermod -aG bluetooth $USER${NORM}"
    warn   "…y reinicia. Sin eso la impresora Bluetooth puede no conectar."
fi

# ---- Cierre -------------------------------------------------------------------
echo
echo -e "${VERDE}  ════════════════════════════════════════════════${NORM}"
ok "Instalación completa"
echo
echo    "   1) Edita $APP_DIR/.env con tus claves de Supabase"
echo    "      (SUPABASE_URL y SUPABASE_ANON_KEY)"
echo    "   2) Reinicia la Pi: la app abre sola, en pantalla"
echo    "      completa y pidiendo el login del empleado"
echo    "   3) Panel oculto (impresora / salir del kiosco):"
echo    "      mantén presionado el título 2,5 segundos"
echo
echo    "   Desinstalar: ./instalar_pi.sh --desinstalar"
echo -e "${VERDE}  ════════════════════════════════════════════════${NORM}"
