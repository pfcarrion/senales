from django.urls import path
from . import views

app_name = "blog"  # Importante para namespacing

urlpatterns = [
    path('', views.blog_list, name='lista_blog'),  # Lista de entradas
    path('<int:post_id>/', views.detalle_blog, name='detalle_blog'),  # Detalle de entrada
]

