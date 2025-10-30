from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


urlpatterns = [
    # Route d'administration standard
    path('admin/', admin.site.urls),

    # Routes d'authentification (login, logout, password reset)
    #path('accounts/', include('django.contrib.auth.urls')),

 # Redirige la racine (/) vers la page de connexion
    path('', lambda request: redirect('users:login'), name='home_root'), 
    
    # Authentification (Login, Logout, Reset Password)
    path('users/', include('users.urls', namespace='users')),
    # Inclure les routes de l'app 'boissons'
    path('boissons/', include('boissons.urls', namespace='boissons')),
    path('personnel/', include('personnel.urls', namespace='personnel')),
    path('avance/', include('avances.urls', namespace='avances')),
    path('depense/', include('depenses.urls', namespace='depenses')),
    path('commandes/', include('commandes.urls', namespace='commandes')),
    path('ventes/', include('ventes.urls', namespace='ventes')),
    path('statistiques/', include('statistiques.urls', namespace='statistiques')),
    path('produits/', include('produits.urls', namespace='produits')),








]

# En environnement de développement (DEBUG=True), servir MEDIA et STATIC via Django
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
