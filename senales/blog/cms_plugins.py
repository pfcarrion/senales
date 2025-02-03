from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import BlogPluginModel

@plugin_pool.register_plugin
class BlogCMSPlugin(CMSPluginBase):
    model = BlogPluginModel
    render_template = "cms_plugins/blog_plugin.html"
    cache = False  # Opcional, si quieres que el contenido del plugin no se almacene en caché

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['posts'] = instance.blog_set.all()  # O ajusta según tu lógica
        return context

