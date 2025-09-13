from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

class Boisson(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    seuil_alerte = models.PositiveIntegerField(default=10)  # email si atteint

    def __str__(self):
        return self.nom


class SuiviStock(models.Model):
    boisson = models.ForeignKey(Boisson, on_delete=models.CASCADE, related_name="suivis")
    date = models.DateField(default=timezone.now)

    # Stock initial = prend automatiquement la valeur du stock_actuel de la veille
    stock_initial = models.PositiveIntegerField()
    stock_actuel = models.PositiveIntegerField()
    justification = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Vérifie si c’est une nouvelle entrée
        if not self.pk:  
            # Cherche le suivi précédent (veille)
            dernier_suivi = SuiviStock.objects.filter(
                boisson=self.boisson
            ).order_by('-date').first()

            if dernier_suivi:
                self.stock_initial = dernier_suivi.stock_actuel  # héritage automatique
            else:
                # Première fois : on laisse l’admin saisir le stock initial
                if not self.stock_initial:
                    raise ValueError("Le stock initial doit être défini lors du premier enregistrement.")

        # Vérifie qu’une justification est donnée si les stocks diffèrent
        if self.stock_actuel != self.stock_initial and not self.justification:
            raise ValueError("Une justification est obligatoire si stock_actuel ≠ stock_initial.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.boisson.nom} - {self.date}"
