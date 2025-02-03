from django.urls import path
from .views import secure_data_view
from . import views

#urlpatterns = [
#    path('secure-data/', views.secure_data_view, name='secure_data'),  # Ruta correcta
#]


#from django.urls import path
#from .views import secure_data_view

urlpatterns = [
    path('secure-data/', secure_data_view, name='secure_data'),
]
