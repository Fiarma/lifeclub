from django.contrib import admin
from .models import CategorieProduit, Produit, Inventaire, LigneInventaire

# Enregistrement des modèles de base
admin.site.register(CategorieProduit)

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'categorie', 'nature', 'lieu', 
        'stock_actuel', 'prix_vente', 'marge', 
        'is_active'
    )
    list_filter = ('is_active', 'nature', 'lieu', 'categorie')
    search_fields = ('nom',)
    # Marge est auto-calculée, stock_initial protégé
    readonly_fields = ('marge', 'stock_initial',)


# Inline pour afficher les LignesInventaire dans l'Inventaire (Admin)
class LigneInventaireInline(admin.TabularInline):
    model = LigneInventaire
    extra = 0
    # Rendre les champs calculés en lecture seule
    readonly_fields = (
        'stock_initial', 'stock_actuel',
        'prix_achat_perte', 'prix_vente_perte', 'marge_perdue',
        'prix_achat_retrouves', 'prix_vente_retrouves', 'marge_retrouvee',
        'gain_net_ligne',
    )
    # Masquer l'affichage des quantités si l'Inventaire est Validé ou Annulé
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.statut != 'en_attente':
            # Rendre tous les champs de saisie non éditables si l'inventaire est Validé/Annulé
            return self.readonly_fields + ('produit', 'stock_compte', 'quantite_perte', 'quantite_retrouvee', 'justification')
        return self.readonly_fields
        
    def has_add_permission(self, request, obj=None):
        # Interdire l'ajout si l'inventaire est Validé ou Annulé
        return obj is None or obj.statut == 'en_attente'

    def has_delete_permission(self, request, obj=None):
        # Interdire la suppression si l'inventaire est Validé ou Annulé
        return obj is None or obj.statut == 'en_attente'

@admin.register(Inventaire)
class InventaireAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'statut', 'date_creation', 'initiateur', 'secretaire', 
        'gain_net_global', 'produits_perdus_total'
    )
    list_filter = ('statut', 'date_creation', 'secretaire')
    search_fields = ('nom',)
    inlines = [LigneInventaireInline]
    
    # Rendre les champs de totaux globaux en lecture seule
    readonly_fields = (
        'date_creation', 'date_validation', 'initiateur', 'secretaire',
        'produits_perdus_total', 'produits_retrouves_total',
        'prix_achat_perte_total', 'prix_vente_perte_total',
        'prix_achat_retrouves_total', 'prix_vente_retrouves_total',
        'marge_perdue_total', 'marge_retrouvee_total', 'gain_net_global',
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Rendre le statut non modifiable manuellement
        if obj and obj.statut != 'en_attente':
            return self.readonly_fields + ('nom', 'statut')
        return self.readonly_fields
        
    def save_model(self, request, obj, form, change):
        # Définir l'initiateur à la création
        if not obj.pk:
            obj.initiateur = request.user
        super().save_model(request, obj, form, change)
