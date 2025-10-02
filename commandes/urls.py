from django.urls import path
from . import views

app_name = 'commandes'

urlpatterns = [
    path('', views.liste_commandes, name='liste_commandes'),
    path('ajouter/', views.ajouter_commande, name='ajouter_commande'),
    path('avoirs/', views.liste_avoirs, name='liste_avoirs'),
    path("update-item/<int:item_id>/", views.update_item_quantity, name="update_item"),
    path("valider/<int:commande_id>/", views.valider_commande, name="valider_commande"),

    # Ajouter une boisson à une commande
    path('ajouter-boisson/<int:commande_id>/', views.ajouter_boisson, name='ajouter_boisson'),

    # Supprimer un item d'une commande
    path('supprimer-item/<int:item_id>/', views.supprimer_item, name='supprimer_item'),

    # Supprimer une commande complète
    path('supprimer-commande/<int:commande_id>/', views.supprimer_commande, name='supprimer_commande'),

    path('avoirs/update/<int:avoir_id>/', views.update_avoir_statut, name='update_avoir_statut'),

     # Point des Ventes
    #path('point-des-ventes/', views.point_des_ventes, name='point_des_ventes'),
]
