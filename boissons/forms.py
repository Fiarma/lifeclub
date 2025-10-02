# Import du module forms de Django pour créer des formulaires
from django import forms
# Import des modèles Boisson et HistoriqueStock définis dans models.py
from .models import Boisson, HistoriqueStock

# # Définition du formulaire pour ajouter / éditer une boisson
# class BoissonForm(forms.ModelForm):
#     # Classe Meta indiquant le modèle source et les champs exposés
#     class Meta:
#         # On lie le formulaire au modèle Boisson
#         model = Boisson
#         # Champs autorisés pour création / édition via l'interface
#         fields = ("nom", "prix_unitaire")


# Import du module forms de Django pour créer des formulaires
from django import forms
# Import des modèles Boisson et HistoriqueStock définis dans models.py
from .models import Boisson, HistoriqueStock

# Définition du formulaire pour ajouter / éditer une boisson
class BoissonForm(forms.ModelForm):
    # Surcharge du champ stock_actuel pour le rendre obligatoire à la création
    stock_actuel = forms.IntegerField(
        min_value=0,
        initial=0,
        label="Stock actuel",
        help_text="Le stock initial sera automatiquement défini avec cette valeur"
    )
    
    class Meta:
        # On lie le formulaire au modèle Boisson
        model = Boisson
        # Champs autorisés pour création / édition via l'interface
        fields = ("lieu", "nom", "prix_unitaire", "stock_actuel")
        labels = {
            'lieu': 'Lieu de vente',
            'nom': 'Nom de la boisson',
            'prix_unitaire': 'Prix unitaire (FCFA)',
            'stock_actuel': 'Stock actuel'
        }
        help_texts = {
            'lieu': 'Choisissez où cette boisson sera vendue',
            'stock_actuel': 'Quantité disponible en stock'
        }
        widgets = {
            'lieu': forms.Select(attrs={'class': 'form-select'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la boisson'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_actuel': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on est en mode édition (instance existe), on ajuste le champ stock_actuel
        if self.instance and self.instance.pk:
            # On pré-remplit avec la valeur actuelle
            self.fields['stock_actuel'].initial = self.instance.stock_actuel
            # On rend le champ readonly en édition pour éviter les incohérences
            self.fields['stock_actuel'].widget.attrs['readonly'] = True
            self.fields['stock_actuel'].help_text = "Modifier le stock via la mise à jour quotidienne"

            
from django import forms
from .models import HistoriqueStock

class HistoriqueStockForm(forms.ModelForm):
    """
    Formulaire pour la mise à jour du stock.
    Le champ 'stock_actuel' est laissé vide pour saisie.
    Le champ 'justification' devient obligatoire si stock_actuel != stock_initial.
    """

    class Meta:
        model = HistoriqueStock
        fields = ("stock_actuel", "justification")  # seuls ces champs sont exposés

    def __init__(self, *args, **kwargs):
        # Extraction éventuelle de l'argument 'boisson' passé depuis la vue
        self.boisson = kwargs.pop("boisson", None)
        super().__init__(*args, **kwargs)

        # Configuration des widgets
        # Champ stock_actuel laissé vide pour saisie manuelle
        self.fields["stock_actuel"].widget.attrs.update({
            "min": 0,       # valeur minimale = 0
            "placeholder": "Saisir le stock actuel"  # placeholder pour aider l'utilisateur
        })

        # Justification configurée pour être une zone de texte plus grande
        self.fields["justification"].widget.attrs.update({
            "rows": 3,
            "placeholder": "Justification si stock différent du précédent"
        })
        # Champ justification optionnel par défaut (devient obligatoire seulement si nécessaire)
        self.fields["justification"].required = False

    def clean(self):
        """
        Validation du formulaire :
        - Si le stock actuel est différent du stock initial, justification obligatoire.
        """
        cleaned = super().clean()
        stock_actuel = cleaned.get("stock_actuel")
        justification = cleaned.get("justification")

        if self.boisson is not None:
            # Le stock initial = valeur actuelle de la boisson avant modification
            stock_initial = self.boisson.stock_actuel

            # Validation : si différence sans justification, erreur
            if stock_actuel != stock_initial and not (justification and justification.strip()):
                raise forms.ValidationError(
                    "Une justification est obligatoire si le stock actuel est différent du stock initial."
                )

            # On fixe stock_initial pour que save() l'utilise
            self.instance.stock_initial = stock_initial

        return cleaned


# Import du module forms
from django import forms

class HistoriqueStockFilterForm(forms.Form):
    # Champ select pour choisir le type de recherche
    search_type = forms.ChoiceField(
        choices=[
            ("", "---- Sélectionnez le type ----"),
            ("date", "Par date"),
            ("month", "Par mois"),
        ],
        required=False,
        label="Type de recherche"
    )

    # Champ pour filtrer par date précise
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date"
    )

    # Champ pour filtrer par mois (input type="month")
    month = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'month'}),
        input_formats=['%Y-%m'],  # accepte "YYYY-MM"
        label="Mois"
    )

    def clean(self):
        """
        Validation : on vérifie la cohérence avec search_type.
        """
        cleaned = super().clean()
        search_type = cleaned.get("search_type")
        date_val = cleaned.get("date")
        month_val = cleaned.get("month")

        # Si recherche par date mais aucune date fournie
        if search_type == "date" and not date_val:
            raise forms.ValidationError("Veuillez choisir une date.")
        # Si recherche par mois mais aucun mois fourni
        if search_type == "month" and not month_val:
            raise forms.ValidationError("Veuillez choisir un mois.")
        return cleaned
