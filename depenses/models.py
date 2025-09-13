from django.db import models

# Create your models here.
# Import des modules Django nécessaires pour les modèles
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

# Import du modèle Personnel depuis l'app personnel
from personnel.models import Personnel

# Modèle Depense
class Depense(models.Model):

    # La date de la dépense, par défaut aujourd'hui
    date = models.DateField(default=timezone.now, verbose_name="Date")
    
    # La personne qui a pris l'argent
    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE, verbose_name="Personne")
    
    # Le montant dépensé
    montant = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Montant")
    
    # Le motif de la dépense (justification)
    motif = models.CharField(max_length=255, verbose_name="Motif")
    

    # Métadonnées
    class Meta:
        ordering = ("-date",)  # Tri par date décroissante

    # Méthode pour vérifier la validité avant sauvegarde
    def clean(self):
        # Montant doit être positif
        if self.montant <= 0:
            raise ValidationError("Le montant doit être supérieur à 0.")

    # Méthode affichage lisible dans l'admin
    def __str__(self):
        return f"{self.personnel.nom} — {self.montant} FCFA le {self.date} ({self.motif})"
