# Import des modules Django pour créer des formulaires
from django import forms
from .models import Depense

# Formulaire pour ajouter ou éditer une dépense
class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ("personnel", "montant", "motif")  # Champs exposés

    # # Personnalisation des widgets
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Montant : champ nombre positif
    #     self.fields["montant"].widget.attrs.update({"min": 0})
    #     # Motif : textarea de 2 lignes
    #     self.fields["motif"].widget.attrs.update({"rows": 2})
    #     # Date : input date HTML5
    #     self.fields["date"].widget.attrs.update({"type": "date"})


# forms.py dans app depenses
from django import forms
# forms.py dans app depenses
from django import forms
from personnel.models import Personnel  # importer le modèle Personnel

class DepenseFilterForm(forms.Form):
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

    # Champ pour filtrer par personnel
    personnel = forms.ModelChoiceField(
        queryset=Personnel.objects.all(),  # liste de tous les personnels
        required=False,
        label="Personnel"
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
