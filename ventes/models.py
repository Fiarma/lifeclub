from django.db import models

# Create your models here.

############### 02-10-2025 #############

# reporting/models.py

from django.db import models
from django.utils import timezone

# ⚠️ Assurez-vous que Boisson est importable depuis son emplacement réel
from commandes.models import Boisson 


class RapportVenteNocturne(models.Model):
    """
    Stocke le résumé financier global d'une nuit de vente complète.
    """
    start_time = models.DateTimeField(verbose_name="Début de la période de vente", unique=True)
    end_time = models.DateTimeField(verbose_name="Fin de la période de vente")
    
    # Montants agrégés
    montant_total_vente = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_total_impayees = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_total_depenses = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_total_avances = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_decaisse = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    chiffre_affaire = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
    date_enregistrement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Rapport Vente du {self.start_time.strftime('%d/%m/%Y')} (Fin: {self.end_time.strftime('%H:%M')})"

    class Meta:
        ordering = ['-start_time']
        verbose_name = "Rapport de Vente Nocturne"
        verbose_name_plural = "Rapports de Vente Nocturne"


class DetailVenteBoisson(models.Model):
    """
    Détail de la quantité et du montant total vendus pour une boisson donnée 
    dans le cadre d'un RapportVenteNocturne.
    """
    rapport = models.ForeignKey(
        RapportVenteNocturne,
        on_delete=models.CASCADE,
        related_name="details_boissons", 
        verbose_name="Rapport de Vente"
    )
    boisson = models.ForeignKey(
        Boisson,
        on_delete=models.PROTECT,
        verbose_name="Boisson"
    )
    
    # ✅ Champ de la quantité totale vendue
    quantite_totale = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité Totale Vendue"
    )
    
    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Montant Total de la Boisson"
    )
    
    prix_unitaire_au_moment_vente = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Prix unitaire de référence"
    )

    def __str__(self):
        return f"{self.boisson.nom} ({self.quantite_totale}x) - {self.rapport}"
    
    class Meta:
        unique_together = ('rapport', 'boisson') 
        ordering = ['-montant_total']