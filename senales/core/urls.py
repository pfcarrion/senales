from django.urls import path
from .views import secure_data_view
from . import views


urlpatterns = [
    path('secure-data/', secure_data_view, name='secure_data'),
    path('senales/', views.senales, name='senales'),
    ]
