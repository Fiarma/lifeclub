# from django import forms
# from .models import Commande
# from personnel.models import Personnel

# # Formulaire pour sélectionner le personnel
# class CommandeForm(forms.ModelForm):
#     class Meta:
#         model = Commande
#         fields = ["personnel"]
#         widgets = {
#             "personnel": forms.Select(attrs={"class": "form-select"})
#         }


############### 04 -10- 2025 ##############

# commandes/forms.py

# from django import forms
# from .models import Commande
# from personnel.models import Personnel
# # Importation de la liste générée
# from .utils import COUNTRY_CODES_CHOICES 

# # Formulaire pour la création de commande
# class CommandeForm(forms.ModelForm):
    
#     code_pays_tel = forms.ChoiceField(
#         choices=COUNTRY_CODES_CHOICES,
#         initial='+226', # Défaut sur Burkina Faso
#         required=True,
#         widget=forms.Select(attrs={"class": "form-select flex-shrink-0", "style": "width: 150px; font-weight: bold;"}),
#         label="Indicatif"
#     )

#     class Meta:
#         model = Commande
#         # Inclure les nouveaux champs client
#         fields = [
#             "personnel", 
#             "code_pays_tel", 
#             "numero_telephone", 
#             "client_nom", 
#             "client_prenom"
#         ]
#         widgets = {
#             "personnel": forms.Select(attrs={"class": "form-select"}),
#             "numero_telephone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Numéro du client (sans l'indicatif)"}),
#             "client_nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom (Facultatif)"}),
#             "client_prenom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom (Facultatif)"}),
#         }
    
#     # Aucune validation stricte sur la longueur du numéro pour supporter les formats internationaux
#     pass

# commandes/forms.py
from django import forms
from .models import Commande
from .utils import COUNTRY_CODES_CHOICES

class CommandeForm(forms.ModelForm):
    code_pays_tel = forms.ChoiceField(
        required=True,
        widget=forms.Select(attrs={
            "class": "form-select flex-shrink-0",
            "style": "width: 150px; font-weight: bold;"
        }),
        label="Indicatif"
    )

    class Meta:
        model = Commande
        fields = [
            "personnel",
            "code_pays_tel",
            "numero_telephone",
            "client_nom",
            "client_prenom"
        ]
        widgets = {
            "personnel": forms.Select(attrs={"class": "form-select"}),
            "numero_telephone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Numéro du client (sans l'indicatif)"
            }),
            "client_nom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom (Facultatif)"}),
            "client_prenom": forms.TextInput(attrs={"class": "form-control", "placeholder": "Prénom (Facultatif)"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['code_pays_tel'].choices = COUNTRY_CODES_CHOICES
        if not self.instance.pk:
            self.initial['code_pays_tel'] = '+226'
