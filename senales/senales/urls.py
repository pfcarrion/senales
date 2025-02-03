from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog
from blog import views as blog_views
from core import views as core_views
#from core.views import payment_test
from core.views import senales_trading

urlpatterns = [
    path('accounts/', include('allauth.urls')),  # Autenticación
    path('filer/', include('filer.urls')),  # Media
    path('blogs/<int:blog_id>/', blog_views.detalle_blog, name='detalle_blog'),
    path('suscripciones/nueva/', core_views.crear_suscripcion, name='crear_suscripcion'),
    path('suscribirse/', core_views.subscribe, name='subscribe'),
    path('subscribe/', core_views.subscribe, name='subscribe'),  # Ruta de la suscripción
    path('payment/<int:subscription_id>/', core_views.payment, name='payment'),
    path('crear-usuario/', core_views.crear_usuario, name='crear_usuario'),
    path('payment/success/<int:subscription_id>/', core_views.payment_success, name='payment_success'),
    path('payment/cancel/', core_views.payment_cancel, name='payment_cancel'),
    path('seleccionar-metodo-pago/<int:subscription_id>/', core_views.seleccionar_metodo_pago, name='seleccionar_metodo_pago'),
    path('binance-payment/<int:subscription_id>/', core_views.binance_payment, name='binance_payment'),
    path('senales/', senales_trading, name='senales'),
]

# Aquí, solo incluyes las rutas relacionadas con el idioma
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('secure-data/', core_views.secure_data_view, name='secure_data'),  # Esta ruta ahora estará disponible en /es/secure-data/
    path('', include('cms.urls')),  # Django CMS al final
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
