from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Route d'administration standard
    path('admin/', admin.site.urls),

    # Routes d'authentification (login, logout, password reset)
    #path('accounts/', include('django.contrib.auth.urls')),

    # Inclure les routes de l'app 'boissons'
    path('', include('boissons.urls', namespace='boissons')),
    path('personnel/', include('personnel.urls', namespace='personnel')),
    path('avance/', include('avances.urls', namespace='avances')),
    path('depense/', include('depenses.urls', namespace='depenses')),
    path('commandes/', include('commandes.urls', namespace='commandes')),




]

# En environnement de développement (DEBUG=True), servir MEDIA et STATIC via Django
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
