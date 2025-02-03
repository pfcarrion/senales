from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _

class BlogApphook(CMSApp):
    app_name = "blog"  # Nombre de tu aplicación (usado para namespacing de URLs)
    name = _("Blog Application")  # Nombre que aparecerá en el panel de administración

    def get_urls(self, page=None, language=None, **kwargs):
        return ["blog.urls"]  # Ruta al archivo de URLs de tu app

# Registra el AppHook en el pool
apphook_pool.register(BlogApphook)

