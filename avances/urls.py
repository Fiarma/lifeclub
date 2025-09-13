# Import de path pour définir les routes
from django.urls import path
# Import des vues locales
from . import views

# Namespace de l'app pour URL reversing
app_name = "avances"

# Définition des routes de l'app avances
urlpatterns = [
    # Route racine : liste des avances
    path("", views.liste_avances, name="liste_avances"),
    # Route pour ajouter une avance
    path("add/", views.add_avance, name="add_avance"),
    # Route pour éditer une avance existante
    path("edit/<int:pk>/", views.edit_avance, name="edit_avance"),
    # Route pour supprimer une avance
    path("delete/<int:pk>/", views.delete_avance, name="delete_avance"),
]
