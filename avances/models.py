from django.db import models

# Create your models here.
# Import pour gérer la relation avec Personnel
from django.db import models
from django.utils import timezone
from personnel.models import Personnel  # ✅ On importe explicitement le modèle Personnel depuis l'app personnel


class Avance(models.Model):
    # Relation avec le personnel qui reçoit l'avance
    personnel = models.ForeignKey(
        Personnel,              # Lien avec le modèle Personnel
        on_delete=models.CASCADE,       # Si le personnel est supprimé, on supprime ses avances
        related_name="avances"          # Permet d'accéder aux avances via personnel.avances.all()
    )

    # Montant de l'avance
    montant = models.DecimalField(
        max_digits=10,                  # Max 99999999.99
        decimal_places=2,               # Deux chiffres après la virgule
        verbose_name="Montant de l'avance"
    )

    # Date où l'avance a été donnée
    date_avance = models.DateField(
        default=timezone.now,           # Par défaut : aujourd'hui
        verbose_name="Date de l'avance"
    )

    # Optionnel : motif ou commentaire
    motif = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Motif de l'avance"
    )

    def __str__(self):
        # Affichage lisible : nom + montant + date
        return f"{self.personnel.nom} {self.personnel.prenom} - {self.montant} FCFA le {self.date_avance}"
