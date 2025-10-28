"""
WSGI config for social_media project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')

application = get_wsgi_application()

# --- Auto-run migrations on Render safely ---
import django
from django.core.management import call_command

if os.environ.get('RENDER'):
    try:
        django.setup()
        call_command('migrate', interactive=False)
        print("✅ Database migrations applied automatically on Render.")
    except Exception as e:
        print(f"⚠️ Migration error: {e}")
