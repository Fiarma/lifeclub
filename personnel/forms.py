from django import forms
from .models import Personnel, JOUR_CHOICES

class PersonnelForm(forms.ModelForm):
    # Formulaire pour ajouter ou modifier un employé
    
    # Champ multi-select pour les jours de repos dynamiques
    jours_repos = forms.MultipleChoiceField(
        choices=JOUR_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Jours de repos"
    )

    class Meta:
        model = Personnel
        fields = ["id", "nom", "prenom", "role", "lieu_travail", "salaire", "jours_repos"]

    def clean(self):
        """Validation complémentaire"""
        cleaned = super().clean()
        lieu = cleaned.get("lieu_travail")
        jours = cleaned.get("jours_repos", [])
        
        # Si Boîte, il doit y avoir au moins 2 jours de repos
        if lieu == "boite" and len(jours) < 2:
            raise forms.ValidationError("Pour la Boîte, veuillez choisir au moins 2 jours de repos.")
        
        # Pour Terrasse, au moins 1 jour
        if lieu == "terrasse" and len(jours) < 1:
            raise forms.ValidationError("Pour la Terrasse, veuillez choisir au moins 1 jour de repos.")
        
        return cleaned
