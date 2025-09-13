from django.contrib import admin

# Register your models here.
# Import du module admin pour enregistrer les modèles dans l'admin Django
from django.contrib import admin
# Import du modèle Avance défini dans models.py
from .models import Avance

# Enregistrement et configuration du modèle Avance dans l'admin
@admin.register(Avance)
class AvanceAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste d'administration
    list_display = ("personnel", "montant", "date_avance", "motif")
    # Filtres disponibles dans la barre latérale pour affiner la recherche
    list_filter = ("date_avance", "personnel")
    # Champs sur lesquels la recherche textuelle sera effectuée
    search_fields = ("personnel__nom", "personnel__prenom", "motif")
