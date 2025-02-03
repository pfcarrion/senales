from django.urls import path, include  
from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _

class CoreApphook(CMSApp):
    app_name = "core"  # Nombre de tu aplicación (usado para namespacing de URLs)
    name = _("Core Application")  # Nombre que aparecerá en el panel de administración

    def get_urls(self, page=None, language=None, **kwargs):
#        return ["core.urls"]  # Ruta al archivo de URLs de tu app
        return [path('', include('senales.urls'))]  # Ruta completa a tu archivo de URLs
#         return [path('', include('senales.urls'))]
# Registra el AppHook en el pool
apphook_pool.register(CoreApphook)

