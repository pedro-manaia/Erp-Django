import os
import sys
import pathlib

# Ensure project root is on sys.path (so 'erp' is importable no matter where this is run from)
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp.settings")

import django  # noqa
django.setup()

from django.contrib.auth import get_user_model  # noqa

User = get_user_model()

username = os.getenv("ERP_DEFAULT_USER", "pedro")
password = os.getenv("ERP_DEFAULT_PASS", "123")

u, created = User.objects.get_or_create(
    username=username,
    defaults={
        "is_staff": True,
        "is_superuser": True,
        "first_name": "Pedro",
    },
)

# Always (re)ensure access + password
changed = False
if not u.is_staff:
    u.is_staff = True
    changed = True
if not u.is_superuser:
    u.is_superuser = True
    changed = True

# Reset password to known value to guarantee login works
u.set_password(password)
changed = True

if changed:
    u.save()

print(f"Usuario {username} OK")
