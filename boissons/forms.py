# Import du module forms de Django pour créer des formulaires
from django import forms
# Import des modèles Boisson et HistoriqueStock définis dans models.py
from .models import Boisson, HistoriqueStock

# Définition du formulaire pour ajouter / éditer une boisson
class BoissonForm(forms.ModelForm):
    # Classe Meta indiquant le modèle source et les champs exposés
    class Meta:
        # On lie le formulaire au modèle Boisson
        model = Boisson
        # Champs autorisés pour création / édition via l'interface
        fields = ("nom", "prix_unitaire")

# # Définition du formulaire pour la mise à jour du stock (utilisé par le caissier)
# class HistoriqueStockForm(forms.ModelForm):
#     # Classe Meta indiquant le modèle source et les champs exposés
#     class Meta:
#         # On lie le formulaire au modèle HistoriqueStock
#         model = HistoriqueStock
#         # On autorise uniquement la saisie du stock_actuel et de la justification
#         fields = ("stock_actuel", "justification")

#     # Initialisation du formulaire, on attend la boisson en paramètre pour connaître le stock initial
#     def __init__(self, *args, **kwargs):
#         # Extraction éventuelle de l'argument 'boisson' passé depuis la vue
#         self.boisson = kwargs.pop("boisson", None)
#         # Appel de l'initialisation parent pour construire les champs
#         super().__init__(*args, **kwargs)
#         # Si la boisson est fournie, on préremplit et configure les widgets
#         if self.boisson:
#             # Valeur initiale du champ stock_actuel = valeur courante de la boisson
#             self.fields["stock_actuel"].initial = self.boisson.stock_actuel
#             # Attribut HTML min pour éviter de saisir des valeurs négatives via UI
#             self.fields["stock_actuel"].widget.attrs.update({"min": 0})
#             # Attribut HTML rows pour la zone de justification
#             self.fields["justification"].widget.attrs.update({"rows": 3})

#     # Validation complémentaire lors de l'envoi du formulaire
#     def clean(self):
#         # Récupération des données nettoyées par le parent
#         cleaned = super().clean()
#         # Récupération de la valeur saisie pour stock_actuel
#         stock_actuel = cleaned.get("stock_actuel")
#         # Récupération de la justification saisie
#         justification = cleaned.get("justification")
#         # Si une boisson a été fournie à l'initialisation
#         if self.boisson is not None:
#             # On considère le stock_initial comme étant la valeur stock_actuel de la boisson (valeur précédente)
#             stock_initial = self.boisson.stock_actuel
#             # Si l'utilisateur a saisi une valeur différente sans justification valide -> erreur
#             if stock_actuel != stock_initial and not (justification and justification.strip()):
#                 raise forms.ValidationError(
#                     "Une justification est obligatoire si le stock actuel est différent du stock initial."
#                 )
#             # On fixe l'attribut stock_initial de l'instance pour que save() l'utilise
#             self.instance.stock_initial = stock_initial
#         # Retour des données nettoyées si tout est ok
#         return cleaned


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


# from django import forms

# class HistoriqueStockFilterForm(forms.Form):
#     # Champ pour filtrer par date précise (jour)
#     date = forms.DateField(
#         required=False,  # facultatif
#         widget=forms.DateInput(attrs={'type': 'date'}),  # affichage calendrier HTML
#         label="Rechercher par date"  # label affiché dans le formulaire
#     )

#     # Champ pour filtrer par mois (année + mois)
#     month = forms.DateField(
#         required=False,  # facultatif
#         widget=forms.DateInput(attrs={'type': 'month'}),  # affichage sélecteur mois HTML
#         label="Rechercher par mois"  # label affiché
#     )

#     def clean(self):
#         """
#         Validation personnalisée :
#         - Interdit de remplir les deux champs en même temps
#         """
#         cleaned = super().clean()  # récupère les données nettoyées
#         if cleaned.get('date') and cleaned.get('month'):
#             # Lever une erreur si les deux sont remplis
#             raise forms.ValidationError("Veuillez remplir soit la date, soit le mois, pas les deux.")
#         return cleaned

# Import du module forms de Django
# from django import forms

# # Formulaire filtrage historique (date OU mois)
# class HistoriqueStockFilterForm(forms.Form):
#     # Champ pour filtrer par date précise (jour)
#     date = forms.DateField(
#         required=False,  # facultatif
#         widget=forms.DateInput(attrs={'type': 'date'}),  # affiche un sélecteur de date
#         label="Rechercher par date"  # étiquette du champ
#     )

#     # Champ pour filtrer par mois (input type="month" envoie "YYYY-MM")
#     # On accepte explicitement le format '%Y-%m' via input_formats
#     month = forms.DateField(
#         required=False,  # facultatif
#         widget=forms.DateInput(attrs={'type': 'month'}),  # sélecteur mois côté navigateur
#         input_formats=['%Y-%m'],  # permet de parser "YYYY-MM" en date (sera 1er du mois)
#         label="Rechercher par mois"  # étiquette du champ
#     )

#     def clean(self):
#         """
#         Validation : on interdit de remplir les deux champs en même temps.
#         """
#         cleaned = super().clean()  # récupérer les données nettoyées
#         # Si l'utilisateur a rempli à la fois date et month => erreur
#         if cleaned.get('date') and cleaned.get('month'):
#             raise forms.ValidationError("Veuillez remplir soit la date, soit le mois, pas les deux.")
#         return cleaned


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
