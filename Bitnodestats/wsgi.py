import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Bitnodestats.settings.production")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
