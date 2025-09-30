from django import forms
from .models import Commande
from personnel.models import Personnel

# Formulaire pour sélectionner le personnel
class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ["personnel"]
        widgets = {
            "personnel": forms.Select(attrs={"class": "form-select"})
        }
