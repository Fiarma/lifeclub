

# from django.db import models
# from django.utils import timezone

# # Importations des modèles externes (Boisson, Personnel) et outils Django
# from boissons.models import Boisson 
# from personnel.models import Personnel
# from django.db.models import DecimalField, Sum, F, Case, When 
# # La ligne 'from commandes.models import Boisson' est redondante si 'from boissons.models import Boisson' est présent

# class RapportVenteNocturne(models.Model):
#     """
#     Stocke le résumé financier global d'une nuit de vente complète.
#     """
#     # Début de la période de vente, unique pour éviter les doublons de rapport
#     start_time = models.DateTimeField(verbose_name="Début de la période de vente", unique=True)
#     # Fin de la période de vente
#     end_time = models.DateTimeField(verbose_name="Fin de la période de vente")
    
#     # Montants agrégés du rapport financier
#     montant_total_vente = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     montant_total_impayees = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     montant_total_depenses = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     montant_total_avances = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     montant_decaisse = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     chiffre_affaire = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
#     # Date d'enregistrement de l'archive
#     date_enregistrement = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Rapport Vente du {self.start_time.strftime('%d/%m/%Y')} (Fin: {self.end_time.strftime('%H:%M')})"

#     class Meta:
#         ordering = ['-start_time']
#         verbose_name = "Rapport de Vente Nocturne"
#         verbose_name_plural = "Rapports de Vente Nocturne"


# class DetailVenteBoisson(models.Model):
#     """
#     Détail de la quantité et du montant total vendus pour une boisson donnée 
#     dans le cadre d'un RapportVenteNocturne.
#     """
#     # Clé étrangère vers le rapport principal
#     rapport = models.ForeignKey(
#         RapportVenteNocturne,
#         on_delete=models.CASCADE,
#         related_name="details_boissons", 
#         verbose_name="Rapport de Vente"
#     )
#     # Clé étrangère vers la boisson (protégée)
#     boisson = models.ForeignKey(
#         Boisson,
#         on_delete=models.PROTECT,
#         verbose_name="Boisson"
#     )
    
#     quantite_totale = models.PositiveIntegerField(
#         default=0,
#         verbose_name="Quantité Totale Vendue"
#     )
    
#     montant_total = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0,
#         verbose_name="Montant Total de la Boisson"
#     )
    
#     prix_unitaire_au_moment_vente = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         verbose_name="Prix unitaire de référence"
#     )

#     def __str__(self):
#         return f"{self.boisson.nom} ({self.quantite_totale}x) - {self.rapport}"
    
#     class Meta:
#         unique_together = ('rapport', 'boisson') 
#         ordering = ['-montant_total']


# class PerformancePersonnelNocturne(models.Model):
#     """
#     Archive les statistiques de performance d'un employé sur une période de rapport donnée.
#     """
#     # Lien vers le rapport de vente nocturne
#     rapport = models.ForeignKey(
#         RapportVenteNocturne, 
#         related_name='performance_personnel',
#         on_delete=models.CASCADE,
#         verbose_name="Rapport de Vente Nocturne"
#     )
#     # Lien vers l'employé
#     personnel = models.ForeignKey(
#         Personnel,
#         on_delete=models.PROTECT, 
#         verbose_name="Employé concerné"
#     )
#     # Montant total des ventes attribué à cet employé
#     montant_vendu_total = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=0,
#         verbose_name="Montant Total Vendu (Théorique)"
#     )
#     # Montant des impayés pris en charge par cet employé
#     montant_impaye_personnel = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=0,
#         verbose_name="Montant Impayé à son nom"
#     )
#     # Quantité totale de boissons vendues par cet employé
#     quantite_totale_boissons_vendues = models.PositiveIntegerField(
#         default=0,
#         verbose_name="Quantité Totale de Boissons Vendues"
#     )
#     # NOUVEAU CHAMP : Montant total des avances prises par ce personnel
#     montant_total_avances_personnel = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2, 
#         default=0,
#         verbose_name="Montant Total des Avances"
#     )

#        # NOUVEAU CHAMP : Détail des ventes par boisson pour cet employé (clé manquante)
#     details_boissons_vendues_archive = models.JSONField(
#         null=True, 
#         blank=True,
#         verbose_name="Détail des boissons vendues archivé"
#     ) 

#     class Meta:
#         verbose_name = "Performance du Personnel Nocturne"
#         # Empêche un doublon pour un même rapport/personnel
#         unique_together = ('rapport', 'personnel') 
        
#     def __str__(self):
#         return f"Performance de {self.personnel.prenom} {self.personnel.nom} pour {self.rapport.start_time.date()}"


#############################

from django.db import models
from django.utils import timezone
from django.db.models import JSONField # Importation de JSONField
from django.db.models import DecimalField, Sum, F, Case, When, UniqueConstraint, Q 

# Importations des modèles externes (Boisson, Personnel)
from boissons.models import Boisson 
from personnel.models import Personnel


class RapportVenteNocturne(models.Model):
    """
    Stocke le résumé financier global d'une nuit de vente complète.
    """
    start_time = models.DateTimeField(verbose_name="Début de la période de vente", unique=True)
    # end_time est optionnel tant que le rapport est actif
    end_time = models.DateTimeField(verbose_name="Fin de la période de vente", null=True, blank=True)
    
    # GESTION DE SESSION : État de la session (Ouvert/Fermé)
    is_active = models.BooleanField(
        default=False,
        verbose_name="Session de Vente Active"
    )
    # GESTION DE SESSION : Caissier responsable de l'ouverture
    caissier = models.ForeignKey(
        Personnel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Caissier Responsable de la Session"
    )

    # Montants agrégés du rapport financier
    montant_total_vente = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_total_impayees = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_total_depenses = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_total_avances = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    montant_decaisse = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    chiffre_affaire = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
    date_enregistrement = models.DateTimeField(default=timezone.now)

    def __str__(self):
        status = "EN COURS 🟢" if self.is_active else "TERMINÉ 🔴"
        return f"Rapport Vente du {self.start_time.strftime('%d/%m/%Y %H:%M')} ({status})"

    class Meta:
        ordering = ['-start_time']
        verbose_name = "Rapport de Vente Nocturne"
        verbose_name_plural = "Rapports de Vente Nocturne"
        # Contrainte pour garantir qu'un seul rapport peut être actif à la fois
        constraints = [
            UniqueConstraint(fields=['is_active'], condition=Q(is_active=True), name='unique_active_session')
        ]


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


class PerformancePersonnelNocturne(models.Model):
    """
    Archive les statistiques de performance d'un employé sur une période de rapport donnée.
    """
    rapport = models.ForeignKey(
        RapportVenteNocturne, 
        related_name='performance_personnel',
        on_delete=models.CASCADE,
        verbose_name="Rapport de Vente Nocturne"
    )
    personnel = models.ForeignKey(
        Personnel,
        on_delete=models.PROTECT, 
        verbose_name="Employé concerné"
    )
    montant_vendu_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Montant Total Vendu (Théorique)"
    )
    montant_impaye_personnel = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Montant Impayé à son nom"
    )
    quantite_totale_boissons_vendues = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité Totale de Boissons Vendues"
    )
    montant_total_avances_personnel = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Montant Total des Avances"
    )

    # Détail des ventes par boisson pour cet employé
    details_boissons_vendues_archive = models.JSONField(
        null=True, 
        blank=True,
        verbose_name="Détail des boissons vendues archivé"
    ) 

    class Meta:
        verbose_name = "Performance du Personnel Nocturne"
        unique_together = ('rapport', 'personnel') 
        
    def __str__(self):
        return f"Performance de {self.personnel.prenom} {self.personnel.nom} pour {self.rapport.start_time.date()}"