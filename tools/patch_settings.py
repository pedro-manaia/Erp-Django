\
import io, os, sys, re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings_path = os.path.join(BASE_DIR, 'erp', 'settings.py')

V2_MARK = "# === AUTO-PATCH v2: hard-dedupe apps ==="

BLOCK_V2 = (
    V2_MARK + "\n"
    "def __ap_base(_a):\n"
    "    return _a.split('.')[0]\n"
    "# Remove QUALQUER entrada de products/inventory por base-name\n"
    "INSTALLED_APPS = [a for a in INSTALLED_APPS if __ap_base(a) not in ('products','inventory')]\n"
    "# Garante AppConfig\n"
    "INSTALLED_APPS += ['products.apps.ProductsConfig','inventory.apps.InventoryConfig']\n"
    "# Remove duplicatas por caminho exato\n"
    "_seen=set(); _out=[]\n"
    "for a in INSTALLED_APPS:\n"
    "    if a in _seen: continue\n"
    "    _seen.add(a); _out.append(a)\n"
    "INSTALLED_APPS = _out\n"
    "# MIGRATION_MODULES\n"
    "try:\n"
    "    MIGRATION_MODULES\n"
    "except NameError:\n"
    "    MIGRATION_MODULES = {}\n"
    "for _m in ['customers','products','sales','inventory']:\n"
    "    MIGRATION_MODULES.setdefault(_m, None)\n"
)

def main():
    if not os.path.exists(settings_path):
        print(f"[patch_settings v3] ERRO: settings.py não encontrado em {settings_path}")
        sys.exit(1)

    with io.open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Sempre anexar o bloco V2 (se ainda não existe)
    if V2_MARK not in content:
        with io.open(settings_path, 'a', encoding='utf-8') as f:
            f.write("\n\n" + BLOCK_V2 + "\n")
        print("[patch_settings v3] Bloco v2 anexado.")
    else:
        print("[patch_settings v3] Bloco v2 já presente.")

    print("[patch_settings v3] OK.")
    sys.exit(0)

if __name__ == "__main__":
    main()
