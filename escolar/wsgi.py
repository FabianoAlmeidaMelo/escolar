"""
WSGI config for escolar project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
from dj_static import Cling
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escolar.settings")

application = Cling(get_wsgi_application())

# ## para rodar com os static em outro servidor:
# application = get_wsgi_application()
#/projetos/escolar/escolar/staticfiles$ python -m http.server 8001


