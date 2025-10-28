"""
WSGI config for social_media project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')

from django.core.wsgi import get_wsgi_application

# --- Auto-run migrations on Render ---
import django
from django.core.management import call_command

if os.environ.get('RENDER'):  # Run only in Render environment
    django.setup()
    try:
        call_command('migrate', interactive=False)
        print("✅ Database migrations applied automatically on Render.")
    except Exception as e:
        print(f"⚠️ Migration error: {e}")

# Create the WSGI application
application = get_wsgi_application()
