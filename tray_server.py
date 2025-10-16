
# -*- coding: utf-8 -*-
"""
Tray controller do ERP (Windows) com:
- Auto-instalação de dependências (--install-deps)
- Instância única (mutex Local\ + fallback por socket)
- Prevenção de 2 servidores na mesma porta
- Status visual (Online/Offline/Reiniciando com piscar)
- Lê SERVER_PORT do .env (padrão 3100)

Atenção: o .BAT chama 2x (instalação e depois execução). Para evitar
2 popups, o caminho "--install-deps" roda SEM exibir alerta de instância.
"""

import os, sys, time, threading, subprocess, webbrowser, socket
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR
SERVER_SCRIPT = PROJECT_DIR / "run_waitress.py"
ENV_FILE = PROJECT_DIR / ".env"

# ---------------------- Auto-instalação de dependências ----------------------
REQUIRED_PKGS = [
    "psutil", "pystray", "Pillow", "python-dotenv", "waitress",
    "Django", "django-environ", "djangorestframework",
    "django-filter", "drf-spectacular", "whitenoise",
]

def ensure_dependencies():
    print("[INFO] Verificando dependências...")
    import importlib.util
    missing = []
    module_map = {
        "Pillow": "PIL",
        "python-dotenv": "dotenv",
        "django-environ": "environ",
        "djangorestframework": "rest_framework",
        "django-filter": "django_filters",
        "drf-spectacular": "drf_spectacular",
    }
    for pkg in REQUIRED_PKGS:
        mod = module_map.get(pkg, pkg).replace("-", "_")
        if importlib.util.find_spec(mod) is None:
            missing.append(pkg)
    if missing:
        print("[INFO] Instalando:", ", ".join(missing))
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("[INFO] Dependências instaladas.")
    else:
        print("[INFO] Todas as dependências já estão presentes.")

def read_env_port(default_port=3100):
    try:
        from dotenv import dotenv_values
        if ENV_FILE.exists():
            cfg = dotenv_values(str(ENV_FILE))
            return int(cfg.get("SERVER_PORT", str(default_port)))
    except Exception as e:
        print("[WARN] Falha ao ler .env:", e)
    return int(default_port)

SERVER_PORT = read_env_port(3100)

# --------------------------- Helpers de aviso Windows ------------------------
def _win_message(title, msg, icon_exclamation=True):
    if os.name != "nt":
        return
    try:
        import ctypes
        MB_ICON = 0x30 if icon_exclamation else 0x40
        MB_TOPMOST = 0x00040000
        ctypes.windll.user32.MessageBoxW(None, msg, title, MB_ICON | MB_TOPMOST)
    except Exception:
        pass

# --------------------------- Guard de instância única ------------------------
def _sanitize_name(s: str) -> str:
    for ch in '\\/:*?"<>|':
        s = s.replace(ch, "_")
    return s

def _already_running_by_process():
    """Defesa extra: se já houver processo com este script, retorna True (sem criar ícone)."""
    try:
        import psutil
        me = os.getpid()
        my_script = str(Path(__file__).resolve()).lower()
        for p in psutil.process_iter(attrs=["pid", "cmdline"]):
            if p.info["pid"] == me:
                continue
            try:
                cmd = " ".join(p.info.get("cmdline") or [])
                if my_script in cmd.lower():
                    return True
            except Exception:
                continue
    except Exception:
        return False
    return False

def _acquire_single_instance(name_seed: str, lock_port: int) -> bool:
    """Tenta adquirir singleton. Retorna True se conseguiu; False se já existe outro."""
    # 1) Mutex no Windows
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            CreateMutex = kernel32.CreateMutexW
            CreateMutex.argtypes = (wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR)
            CreateMutex.restype = wintypes.HANDLE
            ERROR_ALREADY_EXISTS = 183
            safe = _sanitize_name(name_seed)
            mutex_name = f"Local\\ERP_TRAY_{SERVER_PORT}_{safe}"
            handle = CreateMutex(None, False, mutex_name)
            last_error = ctypes.get_last_error()
            if handle and last_error != ERROR_ALREADY_EXISTS:
                globals()['_mutex_handle'] = handle
                return True
            if handle and last_error == ERROR_ALREADY_EXISTS:
                return False
        except Exception:
            pass
    # 2) Fallback universal via socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(("127.0.0.1", lock_port))
        s.listen(1)
        globals()['_instance_lock_socket'] = s
        return True
    except OSError:
        return False

NAME_SEED = f"{hash(str(PROJECT_DIR.resolve()).lower()) & 0xffffffff:08x}"
LOCK_PORT = 60000 + (SERVER_PORT % 1000)

# ----------------------------- Fluxo --install-deps --------------------------
# IMPORTANTE: aqui rodamos SEM alerta de instância (evita 2 popups do .BAT)
if "--install-deps" in sys.argv:
    try:
        ensure_dependencies()
        print("[INFO] Finalizado: dependências OK.")
        sys.exit(0)
    except Exception as e:
        print("[ERRO] Falha na instalação automática:", e)
        sys.exit(1)

# ---- Agora sim o guard para a execução normal (com alerta ÚNICO) ----
if _already_running_by_process() or not _acquire_single_instance(NAME_SEED, LOCK_PORT):
    _win_message("ERP Tray", "O aplicativo da bandeja já está em execução.\nNão abrirei outro.", True)
    sys.exit(2)

# Só importar pystray/PIL após confirmar singleton
import psutil
import pystray
from PIL import Image, ImageDraw

# --------------------------- Ícones e utilidades -----------------------------
def _create_round_icon(size=64, fill=(158, 158, 158, 255)):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, size-4, size-4), fill=fill)
    cx, cy = size//2, size//2
    r = size//3
    draw.arc((cx-r, cy-r, cx+r, cy+r), start=300, end=240, width=6, fill=(255, 255, 255, 255))
    draw.line((cx, cy - r + 6, cx, cy - r//2), fill=(255, 255, 255, 255), width=6)
    return img

ICONS = {
    "offline": _create_round_icon(fill=(158,158,158,255)),   # cinza
    "online": _create_round_icon(fill=(255,165,0,255)),      # laranja
}

# ------------------------------ Server Manager -------------------------------
class ServerManager:
    def __init__(self, tray_icon: pystray.Icon):
        self.proc = None
        self._stop_requested = False
        self._watcher = None
        self._blink_thread = None
        self._blink_stop = threading.Event()
        self._lock = threading.Lock()
        self.icon = tray_icon
        self._set_status("offline", "Desligado")

    def start(self):
        with self._lock:
            if not SERVER_SCRIPT.exists():
                self._notify("run_waitress.py não encontrado ao lado do tray_server.py.", error=True)
                return
            if self.is_running():
                self._set_status("online", "Online")
                self._notify("Servidor já está em execução.")
                self._win_notice("Servidor já está em execução.")
                return
            if self._is_port_in_use(SERVER_PORT):
                msg = f"Já existe um servidor na porta {SERVER_PORT}. Não iniciarei outro."
                self._notify(msg)
                self._win_notice(msg)
                self._set_status("online", "Online")
                return
            creationflags = 0
            if os.name == "nt":
                CREATE_NO_WINDOW = 0x08000000
                DETACHED_PROCESS = 0x00000008
                creationflags = CREATE_NO_WINDOW | DETACHED_PROCESS
            env = os.environ.copy()
            cmd = [sys.executable, "-u", str(SERVER_SCRIPT)]
            try:
                self.proc = subprocess.Popen(
                    cmd, cwd=str(PROJECT_DIR), env=env,
                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                    creationflags=creationflags
                )
                self._set_status("online", "Online")
                self._notify(f"Servidor iniciado (porta {SERVER_PORT}).")
                self._start_watcher()
            except Exception as e:
                self._set_status("offline", "Erro ao iniciar")
                self._notify(f"Falha ao iniciar servidor: {e}", error=True)
                self._win_notice(f"Falha ao iniciar servidor: {e}")

    def stop(self):
        with self._lock:
            self._stop_requested = True
            self._stop_blink()
            if self.proc and self.is_running():
                try:
                    self.proc.terminate()
                    try:
                        self.proc.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        self.proc.kill()
                    self._notify("Servidor parado.")
                    self._win_notice("Servidor parado.")
                except Exception as e:
                    self._notify(f"Erro ao parar servidor: {e}", error=True)
                    self._win_notice(f"Erro ao parar servidor: {e}")
            self.proc = None
            self._set_status("offline", "Desligado")

    def restart(self):
        self._set_status("offline", "Reiniciando...")
        self._start_blink()
        try:
            self.stop()
            time.sleep(0.8)
            self._stop_requested = False
            self.start()
        finally:
            self._stop_blink()

    def open_in_browser(self):
        webbrowser.open(f"http://127.0.0.1:{SERVER_PORT}")

    def is_running(self):
        return self.proc is not None and self.proc.poll() is None

    def _start_watcher(self):
        if self._watcher and self._watcher.is_alive():
            return
        def watch():
            while True:
                if self.proc is None:
                    break
                ret = self.proc.poll()
                if ret is None:
                    self._set_status("online", "Online")
                    time.sleep(1.0)
                    continue
                if self._stop_requested:
                    self._set_status("offline", "Desligado")
                    break
                self._set_status("offline", "Caiu, reiniciando...")
                self._notify("Servidor caiu; reiniciando...")
                self._win_notice("Servidor caiu; reiniciando...")
                time.sleep(1.0)
                self.start()
                break
        self._watcher = threading.Thread(target=watch, daemon=True)
        self._watcher.start()

    def _set_status(self, key, label):
        try:
            self.icon.icon = ICONS.get(key, ICONS["offline"])
            self.icon.title = f"ERP (porta {SERVER_PORT}) - {label}"
            if hasattr(self.icon, "update"):
                try:
                    self.icon.update()
                except Exception:
                    pass
        except Exception:
            pass

    def _start_blink(self):
        self._blink_stop.clear()
        if self._blink_thread and self._blink_thread.is_alive():
            return
        def blinker():
            toggle = False
            while not self._blink_stop.is_set():
                toggle = not toggle
                icon_key = "online" if toggle else "offline"
                self._set_status(icon_key, "Reiniciando...")
                time.sleep(0.4)
        self._blink_thread = threading.Thread(target=blinker, daemon=True)
        self._blink_thread.start()

    def _stop_blink(self):
        self._blink_stop.set()

    def _is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            return s.connect_ex(("127.0.0.1", port)) == 0

    def _notify(self, msg, error=False):
        print(("[ERRO] " if error else "[INFO] ") + msg)

    def _win_notice(self, msg):
        _win_message("ERP Tray", msg, True)

# --------------------------------- Tray UI -----------------------------------
def main():
    icon = pystray.Icon("ERP Server", ICONS["offline"], title=f"ERP (porta {SERVER_PORT}) - Desligado")
    mgr = ServerManager(icon)

    def do_start(icon, item): mgr.start()
    def do_stop(icon, item): mgr.stop()
    def do_restart(icon, item): mgr.restart()
    def do_open(icon, item): mgr.open_in_browser()
    def do_exit(icon, item):
        mgr.stop()
        icon.stop()

    def is_running_checked(item):
        return mgr.is_running()

    icon.menu = pystray.Menu(
        pystray.MenuItem("Abrir no navegador", do_open, default=True),
        pystray.MenuItem("Iniciar servidor", do_start, enabled=lambda item: not mgr.is_running()),
        pystray.MenuItem("Reiniciar servidor", do_restart),
        pystray.MenuItem("Parar servidor", do_stop, enabled=lambda item: mgr.is_running()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Servidor online", None, checked=is_running_checked, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Sair", do_exit),
    )

    mgr.start()
    icon.run()

if __name__ == "__main__":
    main()
