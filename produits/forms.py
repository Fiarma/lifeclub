from django import forms
from django.forms.models import inlineformset_factory
from .models import Inventaire, LigneInventaire, Produit, CategorieProduit, Approvisionnement, Fournisseur, LigneApprovisionnement, LIEU_CHOICES
from decimal import Decimal

# --- 1. Formulaires de Produits et Catégories (CRUD) ---

class CategorieProduitForm(forms.ModelForm):
    """Formulaire pour la création/modification des catégories."""
    class Meta:
        model = CategorieProduit
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Boissons, Plats cuisinés...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

# class ProduitForm(forms.ModelForm):
#     """Formulaire pour la création/modification d'un produit."""
#     class Meta:
#         model = Produit
#         fields = [
#             'categorie', 'nature', 'lieu', 'nom', 'is_active', 
#             'prix_achat', 'prix_vente', 'stock_actuel'
#         ]
#         widgets = {
#             'categorie': forms.Select(attrs={'class': 'form-control'}),
#             'nature': forms.Select(attrs={'class': 'form-control'}),
#             'lieu': forms.Select(attrs={'class': 'form-control'}),
#             'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit (Ex: Bouteille d\'eau, T-Shirt...)'}),
#             'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
#             'prix_vente': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
#             'stock_actuel': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Laisser vide si non dénombrable'}),
#         }
#         labels = {
#             'stock_actuel': "Stock Initial/Actuel (Qté)",
#         }
        
#     def clean(self):
#         """Gestion des contraintes liées à la nature de stock."""
#         cleaned_data = super().clean()
#         nature = cleaned_data.get('nature')
#         stock_actuel = cleaned_data.get('stock_actuel')

#         if nature == 'non_denombrable':
#             # Si non dénombrable, les champs de stock sont ignorés ou réinitialisés
#             cleaned_data['stock_actuel'] = None
            
#         elif nature == 'denombrable' and (stock_actuel is None or stock_actuel < 0):
#             # Si dénombrable, le stock doit être positif ou nul
#             self.add_error('stock_actuel', "Le stock actuel est obligatoire et doit être positif pour un produit dénombrable.")

#         return cleaned_data


class ProduitForm(forms.ModelForm):
    """Formulaire pour la création/modification d'un produit."""
    class Meta:
        model = Produit
        fields = [
            'categorie', 'nature', 'lieu', 'nom', 'is_active', 
            'prix_achat', 'prix_vente', 'stock_actuel'
        ]
        widgets = {
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'nature': forms.Select(attrs={'class': 'form-control'}),
            'lieu': forms.Select(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit (Ex: Bouteille d\'eau, T-Shirt...)'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'prix_vente': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_actuel': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Laisser vide si non dénombrable'}),
        }
        labels = {
            'stock_actuel': "Stock Initial/Actuel (Qté)",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Rendre le stock non modifiable pour les instances existantes (modification)
        if self.instance.pk:
            # 1. Rendre le champ en lecture seule (readonly)
            self.fields['stock_actuel'].widget.attrs['readonly'] = 'readonly'
            
            # Optionnel : Ajouter une classe CSS pour mieux identifier le champ non modifiable
            current_classes = self.fields['stock_actuel'].widget.attrs.get('class', '')
            self.fields['stock_actuel'].widget.attrs['class'] = current_classes + ' bg-light'

        # Pour la création (instance n'a pas de pk), on laisse le champ modifiable
        # pour définir le stock initial.

    def clean(self):
        """Gestion des contraintes liées à la nature de stock."""
        cleaned_data = super().clean()
        nature = cleaned_data.get('nature')
        stock_actuel = cleaned_data.get('stock_actuel')
        
        # ----------------- Logique de validation conservée -----------------
        
        if nature == 'non_denombrable':
            # Si non dénombrable, les champs de stock sont ignorés ou réinitialisés
            cleaned_data['stock_actuel'] = None
            
        elif nature == 'denombrable' and (stock_actuel is None or stock_actuel < 0):
            # Si dénombrable, le stock doit être positif ou nul
            self.add_error('stock_actuel', "Le stock actuel est obligatoire et doit être positif pour un produit dénombrable.")

        return cleaned_data

    def save(self, commit=True):
        """Assure que le stock n'est pas modifié lors de la mise à jour."""
        
        # 1. Obtenir l'instance de Produit
        instance = super().save(commit=False)
        
        # 2. Si c'est une modification d'instance existante (pk existe)
        if self.instance.pk:
            # On empêche explicitement la modification du champ stock_actuel
            # en restaurant la valeur originale de l'instance si elle a été soumise.
            # (Cette étape est essentielle car 'readonly' côté HTML n'est pas une sécurité absolue)
            if 'stock_actuel' in self.changed_data:
                instance.stock_actuel = self.initial['stock_actuel']
        
        # 3. Sauvegarder l'instance
        if commit:
            instance.save()
            
        return instance
    

# --- 2. Formulaires d'Inventaire ---

# class InventaireForm(forms.ModelForm):
#     """Formulaire pour la création/modification de la session d'inventaire (Inventaire)."""
#     class Meta:
#         model = Inventaire
#         fields = ['nom'] 
#         widgets = {
#             'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'inventaire (ex: Fin de semaine)'}),
#         }

# class LigneInventaireForm(forms.ModelForm):
#     """Formulaire pour une seule ligne d'ajustement de stock."""
#     class Meta:
#         model = LigneInventaire
#         fields = [
#             'produit', 
#             'stock_compte', 
#             'quantite_perte', 
#             'quantite_retrouvee', 
#             'justification'
#         ]
        
#         widgets = {
#             'produit': forms.Select(attrs={'class': 'form-control select-produit'}),
#             'stock_compte': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': 'Qté'}),
#             'quantite_perte': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': '0'}),
#             'quantite_retrouvee': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': '0'}),
#             'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Raison de l\'ajustement'}),
#         }
    
#     def clean(self):
#         cleaned_data = super().clean()
#         produit = cleaned_data.get('produit')
#         q_perte = cleaned_data.get('quantite_perte') or 0
#         q_retrouvee = cleaned_data.get('quantite_retrouvee') or 0
        
#         # Le produit doit être dénombrable pour être inclus dans un ajustement
#         if produit and produit.nature == 'non_denombrable':
#             raise forms.ValidationError(f"Le produit '{produit.nom}' est non dénombrable et ne peut pas être ajusté par inventaire.")
            
#         if produit and (q_perte > 0 or q_retrouvee > 0) and produit.nature == 'denombrable' and cleaned_data.get('DELETE'):
#             # Si on supprime la ligne, pas besoin de validation de quantité
#             pass
#         elif produit and produit.nature == 'denombrable' and q_perte == 0 and q_retrouvee == 0 and not cleaned_data.get('DELETE'):
#             raise forms.ValidationError("Veuillez spécifier une quantité perdue ou retrouvée.")
        
#         return cleaned_data

# # Formset pour gérer les lignes d'inventaire
# LigneInventaireFormSet = inlineformset_factory(
#     parent_model=Inventaire, 
#     model=LigneInventaire, 
#     form=LigneInventaireForm,
#     extra=1, 
#     can_delete=True,
# )


# --- 2. Formulaires d'Inventaire ---

class InventaireForm(forms.ModelForm):
    """Formulaire pour la création/modification de la session d'inventaire (Inventaire)."""
    class Meta:
        model = Inventaire
        fields = ['nom'] 
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'inventaire (ex: Fin de semaine)'}),
        }

class LigneInventaireForm(forms.ModelForm):
    """Formulaire pour une seule ligne d'ajustement de stock."""
    
    class Meta:
        model = LigneInventaire
        fields = [
            'produit', 
            'stock_compte', 
            'quantite_perte', 
            'quantite_retrouvee', 
            'justification'
        ]
        
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control select-produit'}),
            'stock_compte': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': 'Qté'}),
            'quantite_perte': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': '0'}),
            'quantite_retrouvee': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': '0'}),
            'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Raison de l\'ajustement'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrer les produits pour n'afficher que les dénombrables actifs
        self.fields['produit'].queryset = Produit.objects.filter(
            nature='denombrable', 
            is_active=True
        ).order_by('nom')
        
        # Rendre tous les champs non obligatoires
        self.fields['quantite_perte'].required = False
        self.fields['quantite_retrouvee'].required = False
        self.fields['stock_compte'].required = False
        self.fields['justification'].required = False

    def clean(self):
        cleaned_data = super().clean()
        
        # Si la ligne est marquée pour suppression, on saute la validation
        if self.cleaned_data.get('DELETE', False):
            return cleaned_data
            
        produit = cleaned_data.get('produit')
        
        # Vérifier si un produit est sélectionné (seule validation obligatoire)
        if not produit:
            raise forms.ValidationError("Veuillez sélectionner un produit.")
            
        # Vérifier que le produit est dénombrable
        if produit and produit.nature != 'denombrable':
            raise forms.ValidationError(f"Le produit '{produit.nom}' est non dénombrable et ne peut pas être ajusté par inventaire.")
        
        # Les quantités à 0 sont parfaitement valides - PAS DE VALIDATION STRICTE
        return cleaned_data

# Formset pour gérer les lignes d'inventaire
LigneInventaireFormSet = inlineformset_factory(
    parent_model=Inventaire, 
    model=LigneInventaire, 
    form=LigneInventaireForm,
    extra=1, 
    can_delete=True,
)


###################
# class LigneInventaireUpdateForm(forms.ModelForm):
#     """Formulaire simplifié pour modifier une ligne d'inventaire existante."""
    
#     class Meta:
#         model = LigneInventaire
#         fields = [
#             'stock_compte', 
#             'quantite_perte', 
#             'quantite_retrouvee', 
#             'justification'
#         ]
        
#         widgets = {
#             'stock_compte': forms.NumberInput(attrs={
#                 'class': 'form-control text-right', 
#                 'placeholder': 'Qté comptée'
#             }),
#             'quantite_perte': forms.NumberInput(attrs={
#                 'class': 'form-control text-right', 
#                 'placeholder': '0'
#             }),
#             'quantite_retrouvee': forms.NumberInput(attrs={
#                 'class': 'form-control text-right', 
#                 'placeholder': '0'
#             }),
#             'justification': forms.Textarea(attrs={
#                 'class': 'form-control', 
#                 'rows': 3, 
#                 'placeholder': 'Raison de l\'ajustement'
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Rendre tous les champs non obligatoires
#         self.fields['quantite_perte'].required = False
#         self.fields['quantite_retrouvee'].required = False
#         self.fields['stock_compte'].required = False
#         self.fields['justification'].required = False

# ----------------------------------------------------------------------
# FORMULAIRE POUR LA MODIFICATION D'UNE LIGNE INDIVIDUELLE (CORRIGÉ)
# ----------------------------------------------------------------------
class LigneInventaireUpdateForm(forms.ModelForm):
    """Formulaire spécifique pour modifier une ligne d'inventaire EXISTANTE."""

    # CHAMP 1: Affichage du nom du produit (non lié au modèle pour être en lecture seule)
    produit_nom_display = forms.CharField(
        label="Produit Concerné",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control bg-light font-bold', 'readonly': 'readonly'})
    )

    # CHAMP 2: Affichage du stock Théorique (non lié au modèle)
    stock_initial_display = forms.IntegerField(
        label="Stock Actuel (Théorique)",
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control bg-light text-right', 'readonly': 'readonly'})
    )

    class Meta:
        model = LigneInventaire
        fields = [
            'produit',           # Maintenu ici pour que sa valeur soit sauvée (mais caché)
            'stock_compte',          
            'quantite_perte',        
            'quantite_retrouvee',    
            'justification',
        ] 
        
        widgets = {
            # CORRECTION CRUCIALE : Le champ produit DOIT être HiddenInput
            # pour que sa valeur (l'ID du produit) soit soumise au POST.
            'produit': forms.HiddenInput(),
            
            # Champs modifiables par l'utilisateur
            'stock_compte': forms.NumberInput(attrs={'class': 'form-control text-right', 'min': '0', 'placeholder': 'Qté réellement comptée'}),
            'quantite_perte': forms.NumberInput(attrs={'class': 'form-control text-right', 'min': '0', 'placeholder': 'Qté perdue justifiée'}),
            'quantite_retrouvee': forms.NumberInput(attrs={'class': 'form-control text-right', 'min': '0', 'placeholder': 'Qté retrouvée justifiée'}),
            
            'justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Raison de l\'ajustement'}),
        }
        labels = {
            'stock_compte': "Stock Compté (Décompte Physique)",
            'quantite_perte': "Qté Perdue (Justifiée)",
            'quantite_retrouvee': "Qté Retrouvée (Justifiée)",
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Le champ 'produit' est masqué et n'a pas besoin d'être rendu manuellement
        # On peut le supprimer du dict des champs pour ne pas le rendre avec {{ form.as_p }}
        if 'produit' in self.fields:
             self.fields.pop('produit')

        if self.instance.pk:
            # Remplir le champ d'affichage du nom du produit
            self.fields['produit_nom_display'].initial = self.instance.produit.nom
            
            # Initialiser le champ d'affichage du stock théorique
            self.fields['stock_initial_display'].initial = self.instance.stock_initial
        
    def clean(self):
        """
        Effectue la validation croisée pour assurer la cohérence entre les saisies.
        """
        cleaned_data = super().clean()
        
        # Récupération des valeurs
        # self.instance.produit est maintenant garanti d'exister car il a été chargé 
        # depuis la base de données et n'a pas été effacé du formulaire.
        stock_initial = self.instance.stock_initial # Le stock Théorique de la DB
        stock_compte = cleaned_data.get('stock_compte')
        qte_perdue = cleaned_data.get('quantite_perte')
        qte_retrouvee = cleaned_data.get('quantite_retrouvee')
        
        # 1. Vérification des positifs/existants
        if stock_compte is None:
             self.add_error('stock_compte', "Le Stock Compté est obligatoire.")
        elif stock_compte < 0:
             self.add_error('stock_compte', "Le Stock Compté ne peut pas être négatif.")
             
        if qte_perdue is None: qte_perdue = 0 
        if qte_retrouvee is None: qte_retrouvee = 0
            
        if qte_perdue < 0:
             self.add_error('quantite_perte', "La quantité perdue doit être positive ou nulle.")
        if qte_retrouvee < 0:
             self.add_error('quantite_retrouvee', "La quantité retrouvée doit être positive ou nulle.")

        if self.errors:
             return cleaned_data
            
        # 2. VALIDATION DE COHÉRENCE CRUCIALE
        try:
            stock_initial = Decimal(stock_initial)
            stock_compte = Decimal(stock_compte)
            qte_perdue = Decimal(qte_perdue)
            qte_retrouvee = Decimal(qte_retrouvee)
        except Exception:
            raise forms.ValidationError("Erreur de format numérique dans les stocks.")
            
        ecart_net_inventaire = stock_compte - stock_initial
        ecart_net_justification = qte_retrouvee - qte_perdue
        
        if ecart_net_inventaire != ecart_net_justification:
            message_erreur = (
                f"L'écart net entre le Stock Compté et le Stock Théorique est de **{ecart_net_inventaire}**. "
                f"Ceci ne correspond pas à la justification nette saisie (Retrouvé - Perdu = **{ecart_net_justification}**). "
                f"Veuillez ajuster les quantités pour que la justification soit équivalente à l'écart de stock."
            )
            self.add_error('quantite_perte', message_erreur)
            self.add_error('quantite_retrouvee', message_erreur)
            raise forms.ValidationError("Erreur de cohérence entre le décompte physique et les justifications (voir les messages sous les champs de quantité).")
            
        return cleaned_data

    def save(self, commit=True):
        """
        Sauvegarde la ligne et calcule les Marges et le Gain Net 
        basés sur les quantités perdues/retrouvées saisies.
        """
        ligne = super().save(commit=False)
        
        qte_perdue = Decimal(ligne.quantite_perte if ligne.quantite_perte is not None else 0)
        qte_retrouvee = Decimal(ligne.quantite_retrouvee if ligne.quantite_retrouvee is not None else 0)

        # CALCUL DES MARGES ET DU GAIN NET
        # ligne.produit est garanti d'être présent
        produit = ligne.produit
        prix_achat = Decimal(produit.prix_achat)
        prix_vente = Decimal(produit.prix_vente)
        marge_unitaire = prix_vente - prix_achat

        ligne.marge_perdue = qte_perdue * marge_unitaire
        
        # La marge retrouvée doit être basée sur le prix de vente pour l'évaluation du gain potentiel
        ligne.marge_retrouvee = qte_retrouvee * marge_unitaire 
        
        # Le gain net est la différence des marges
        ligne.gain_net_ligne = ligne.marge_retrouvee - ligne.marge_perdue

        if commit:
            ligne.save()
            
        return ligne
    


    ############### 27 -10- 2025 #########


# --- FORMULAIRES FOURNISSEUR ---

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'telephone', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# --- FORMULAIRES APPROVISIONNEMENT ---

class ApprovisionnementForm(forms.ModelForm):
    class Meta:
        model = Approvisionnement
        # Le statut, personnel, et contrôleur sont gérés par la vue
        fields = ['nom', 'date_approvisionnement', 'fournisseur', 'cout_transport'] 
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Référence de la facture/livraison'}),
            'date_approvisionnement': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control'}),
            'cout_transport': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': '0.00'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_approvisionnement'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S']


class LigneApprovisionnementForm(forms.ModelForm):
    class Meta:
        model = LigneApprovisionnement
        fields = [
            'produit', 
            'lieu', 
            'quantite_recue', 
            'quantite_endommagee',
            'montant_total_produit', 
        ]
        
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control select-produit'}),
            'lieu': forms.Select(attrs={'class': 'form-control'}),
            'quantite_recue': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': 'Qté reçue'}),
            'quantite_endommagee': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': 'Qté endommagée', 'min': 0}),
            'montant_total_produit': forms.NumberInput(attrs={'class': 'form-control text-right', 'placeholder': 'Montant facturé'}), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # S'assurer que seules les produits dénombrables actifs sont sélectionnables
        self.fields['produit'].queryset = Produit.objects.filter(
            nature='denombrable', 
            is_active=True
        ).order_by('nom')
        
    def clean(self):
        cleaned_data = super().clean()
        qte_recue = cleaned_data.get('quantite_recue') or 0
        qte_endom = cleaned_data.get('quantite_endommagee') or 0
        
        if qte_endom > qte_recue:
            raise forms.ValidationError("La quantité endommagée ne peut pas dépasser la quantité reçue.")
        
        return cleaned_data


LigneApprovisionnementFormSet = inlineformset_factory(
    parent_model=Approvisionnement, 
    model=LigneApprovisionnement, 
    form=LigneApprovisionnementForm,
    extra=1, 
    can_delete=True,
)