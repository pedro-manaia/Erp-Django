# tools/apply_active_devices_patch.py
"""
Patch automático para habilitar Dispositivos Ativos:
- Adiciona 'core.active_devices.middleware.ActiveDevicesMiddleware' em MIDDLEWARE
- Adiciona rota '/config/dispositivos-ativos/' no urls.py principal
Execute uma vez: python tools/apply_active_devices_patch.py
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
settings = ROOT / "erp" / "settings.py"
urls = ROOT / "erp" / "urls.py"

MW_IMPORT = "core.active_devices.middleware.ActiveDevicesMiddleware"
URL_INSERT = "path('config/dispositivos-ativos/', include('core.active_devices.urls')),"

def patch_settings():
    txt = settings.read_text(encoding="utf-8")
    if MW_IMPORT in txt:
        return False
    # tenta localizar MIDDLEWARE = [ ... ]
    pat = re.compile(r"MIDDLEWARE\s*=\s*\[(.*?)\]", re.S)
    m = pat.search(txt)
    if not m:
        print("[WARN] Não encontrei bloco MIDDLEWARE no settings.py")
        return False
    block = m.group(1)
    new_block = block.rstrip() + f"\n    '{MW_IMPORT}',\n"
    new_txt = txt[:m.start(1)] + new_block + txt[m.end(1):]
    settings.write_text(new_txt, encoding="utf-8")
    print("[OK] settings.py patch aplicado (middleware).")
    return True

def patch_urls():
    txt = urls.read_text(encoding="utf-8")
    changed = False
    # garantir import include
    if "from django.urls import path, include" not in txt:
        txt = txt.replace("from django.urls import path",
                          "from django.urls import path, include")
        changed = True
    if URL_INSERT not in txt:
        # tenta localizar urlpatterns = [ ... ]
        pat = re.compile(r"urlpatterns\s*=\s*\[(.*?)\]", re.S)
        m = pat.search(txt)
        if m:
            block = m.group(1)
            if URL_INSERT not in block:
                new_block = block.rstrip() + f"\n    {URL_INSERT}\n"
                txt = txt[:m.start(1)] + new_block + txt[m.end(1):]
                changed = True
        else:
            print("[WARN] Não encontrei urlpatterns no urls.py")
    if changed:
        urls.write_text(txt, encoding="utf-8")
        print("[OK] urls.py patch aplicado (rota).")
    return changed

if __name__ == "__main__":
    any_change = False
    if settings.exists():
        any_change |= patch_settings()
    else:
        print("[WARN] settings.py não encontrado em", settings)
    if urls.exists():
        any_change |= patch_urls()
    else:
        print("[WARN] urls.py não encontrado em", urls)

    if not any_change:
        print("[INFO] Nada para alterar (parece já aplicado).")