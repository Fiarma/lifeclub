from django.contrib import admin

# Register your models here.
# Import du module admin pour enregistrer les modèles dans l'admin Django
from django.contrib import admin
# Import des modèles Boisson et HistoriqueStock
from .models import Boisson, HistoriqueStock

# Enregistrement et configuration de Boisson dans l'admin
@admin.register(Boisson)
class BoissonAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste d'administration
    list_display = ("nom", "prix_unitaire", "stock_initial", "stock_actuel", "created_at")
    # Champs en lecture seule dans le formulaire admin
    readonly_fields = ("created_at",)
    # Champs autorisés pour la recherche
    search_fields = ("nom",)

    # Méthode permettant de définir dynamiquement les champs readonly
    def get_readonly_fields(self, request, obj=None):
        # On récupère la liste de base des champs readonly
        ro = list(self.readonly_fields)
        # Si on édite un objet existant, on rend stock_initial en lecture seule
        if obj:
            ro.append("stock_initial")
        # On retourne la liste finale des champs readonly
        return ro

# Enregistrement et configuration de HistoriqueStock dans l'admin
@admin.register(HistoriqueStock)
class HistoriqueStockAdmin(admin.ModelAdmin):
    # Colonnes affichées pour l'historique
    list_display = ("boisson", "date", "stock_initial", "stock_actuel", "caissier")
    # Filtres disponibles dans la colonne latérale
    list_filter = ("boisson", "date")
    # Champs autorisés pour la recherche textuelle
    search_fields = ("boisson__nom", "caissier__username")
    # Champs en lecture seule
    readonly_fields = ("date",)
