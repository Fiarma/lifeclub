# Import de path pour définir les routes
from django.urls import path
# Import des vues locales
from . import views

# Définition du namespace de l'app pour les URLs inversées
app_name = "boissons"

# Liste des routes disponibles pour l'application boissons
urlpatterns = [
    # Route racine : liste des boissons
    path("", views.liste_boissons, name="liste_boissons"),
    # Route pour ajouter une nouvelle boisson
    path("add/", views.add_boisson, name="add_boisson"),
    # Route pour éditer une boisson existante
    path("edit/<int:boisson_id>/", views.edit_boisson, name="edit_boisson"),
    # Route pour supprimer une boisson (confirmation)
    path("delete/<int:boisson_id>/", views.delete_boisson, name="delete_boisson"),
    # Route pour mettre à jour le stock (caissier)
    path("maj/<int:boisson_id>/", views.maj_stock, name="maj_stock"),

    path("historique/<int:boisson_id>/", views.historique_stock, name="historique_stock"),

]
