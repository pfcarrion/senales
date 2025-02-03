from cms.models.pluginmodel import CMSPlugin
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Modelo de Blog
class Blog(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

# Modelo de Comentario
#class Comentario(models.Model):
 #   blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comentarios")
  #  autor = models.CharField(max_length=100)
   # contenido = models.TextField()
    #fecha = models.DateTimeField(auto_now_add=True)

    #def __str__(self):
     #   return f"Comentario de {self.usuario} en {self.blog.titulo}"


class Comentario(models.Model):
    blog = models.ForeignKey(Blog, related_name='comentarios', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.autor} en {self.blog.titulo}"


# Modelo de Plugin para integrar blogs en DjangoCMS
class BlogPlugin(CMSPlugin):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def __str__(self):
        return self.blog.titulo

# Para la carga de plugin
class BlogPluginModel(CMSPlugin):
    title = models.CharField(max_length=255, help_text="Título del blog plugin")
    description = models.TextField(blank=True, help_text="Descripción opcional del blog plugin")

    def __str__(self):
        return self.title

# Para la publicacion del Blogpost
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

#    def get_absolute_url(self):
#        return reverse('blog:detalle_blog', args=[self.id])  # Ajusta según la URL de detalle
