from django.urls import path
from . import views

# Namespace de l'app pour les URLs inversées
app_name = "depenses"

urlpatterns = [
    path("", views.liste_depenses, name="liste_depenses"),
    path("add/", views.add_depense, name="add_depense"),
    path("edit/<int:depense_id>/", views.edit_depense, name="edit_depense"),
    path("delete/<int:depense_id>/", views.delete_depense, name="delete_depense"),
]
