from django import forms
from .models import Avance

class AvanceForm(forms.ModelForm):
    class Meta:
        model = Avance
        fields = ["personnel", "montant", "date_avance", "motif"]
