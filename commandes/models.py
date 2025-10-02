

from django.db import models
from boissons.models import Boisson
from personnel.models import Personnel

# Modèle Commande
class Commande(models.Model):
    # Statut de la commande
    STATUT_CHOICES = [
        ("payer", "Payé"),
        ("impayee", "Impayée"),
        ("en_attente", "En attente"),
    ]

    # Type de paiement
    PAIEMENT_CHOICES = [
        ("liquidite", "Liquidité"),
        ("orange_money", "Orange Money"),
        ("hybride", "Hybride"),
    ]

    personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)  # Qui a servi
    date_commande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
    type_paiement = models.CharField(max_length=20, choices=PAIEMENT_CHOICES)

 # NOUVEAU CHAMP : Date de validation (paiement ou passage en impayée)
    date_validation = models.DateTimeField(null=True, blank=True) 
    
    # Montants payés
    montant_remis_client = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    montant_orange = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    montant_liquidite = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Montant à rendre si trop payé
    monnaie_a_rendre = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Statut de la monnaie (remis ou avoir)
    statut_monnaie = models.CharField(
        max_length=20,
        choices=[("remis", "Remis"), ("avoir", "Avoir"), ("non_applicable", "Non applicable")],
        default="non_applicable"
    )

    # Montant total de la commande
    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Montant restant dû si impayée
    montant_restant = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Commande {self.id} - {self.personnel.nom_complet} - {self.montant_total}"


# Boissons dans la commande
class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, related_name="items", on_delete=models.CASCADE)
    boisson = models.ForeignKey(Boisson, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    montant_boisson = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    # Calcul automatique du montant de la boisson
    def save(self, *args, **kwargs):
        self.montant_boisson = self.quantite * self.boisson.prix_unitaire
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantite} x {self.boisson.nom}"


# Avoir lié à une commande
class Avoir(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("regle", "Réglé"),
    ]

    commande = models.OneToOneField(Commande, related_name="avoir", on_delete=models.CASCADE)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_reglement = models.DateTimeField(null=True, blank=True) 

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")

    def __str__(self):
        return f"Avoir {self.id} - {self.montant} ({self.get_statut_display()})"
