from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Depense

# Enregistrement du modèle Depense dans l'admin
@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ("personnel", "montant", "motif", "date")  # colonnes affichées
    list_filter = ("date", "personnel")  # filtres à droite
    search_fields = ("personnel__nom", "motif")  # barre recherche
