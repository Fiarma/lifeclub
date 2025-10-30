
########### COde fonctionnel #####################


# from django.db import models
# from boissons.models import Boisson
# from personnel.models import Personnel

# # Modèle Commande
# class Commande(models.Model):
#     # Statut de la commande
#     STATUT_CHOICES = [
#         ("payer", "Payé"),
#         ("impayee", "Impayée"),
#         ("en_attente", "En attente"),
#     ]

#     # Type de paiement
#     PAIEMENT_CHOICES = [
#         ("liquidite", "Liquidité"),
#         ("orange_money", "Orange Money"),
#         ("hybride", "Hybride"),
#     ]

#     personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)  # Qui a servi
#     date_commande = models.DateTimeField(auto_now_add=True)
#     statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
#     type_paiement = models.CharField(max_length=20, choices=PAIEMENT_CHOICES)

#  # NOUVEAU CHAMP : Date de validation (paiement ou passage en impayée)
#     date_validation = models.DateTimeField(null=True, blank=True) 

#     # Montants payés
#     montant_remis_client = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     montant_orange = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     montant_liquidite = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

#     # Montant à rendre si trop payé
#     monnaie_a_rendre = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     # Statut de la monnaie (remis ou avoir)
#     statut_monnaie = models.CharField(
#         max_length=20,
#         choices=[("remis", "Remis"), ("avoir", "Avoir"), ("non_applicable", "Non applicable")],
#         default="non_applicable"
#     )

#     # Montant total de la commande
#     montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     # Montant restant dû si impayée
#     montant_restant = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def __str__(self):
#         return f"Commande {self.id} - {self.personnel.nom_complet} - {self.montant_total}"


#     def __str__(self):
#         # Cette ligne est maintenant valide grâce à l'étape 1 !
#         return f"Commande {self.id} - {self.personnel.nom_complet} - {self.montant_total}" 

# # Boissons dans la commande
# class CommandeItem(models.Model):
#     commande = models.ForeignKey(Commande, related_name="items", on_delete=models.CASCADE)
#     boisson = models.ForeignKey(Boisson, on_delete=models.CASCADE)
#     quantite = models.PositiveIntegerField()
#     montant_boisson = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

#     # Calcul automatique du montant de la boisson
#     def save(self, *args, **kwargs):
#         self.montant_boisson = self.quantite * self.boisson.prix_unitaire
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.quantite} x {self.boisson.nom}"


# # Avoir lié à une commande
# class Avoir(models.Model):
#     STATUT_CHOICES = [
#         ("en_attente", "En attente"),
#         ("regle", "Réglé"),
#     ]

#     commande = models.OneToOneField(Commande, related_name="avoir", on_delete=models.CASCADE)
#     montant = models.DecimalField(max_digits=10, decimal_places=2)
#     date_creation = models.DateTimeField(auto_now_add=True)
#     date_reglement = models.DateTimeField(null=True, blank=True) 

#     statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")

#     def __str__(self):
#         return f"Avoir {self.id} - {self.montant} ({self.get_statut_display()})"
    













# ############### 02-10-2025 #############

# # reporting/models.py

# from django.db import models
# from django.utils import timezone

# # ⚠️ Assurez-vous que Boisson est importable depuis son emplacement réel
# from commandes.models import Boisson 


# class RapportVenteNocturne(models.Model):
#     """
#     Stocke le résumé financier global d'une nuit de vente complète.
#     """
#     start_time = models.DateTimeField(verbose_name="Début de la période de vente", unique=True)
#     end_time = models.DateTimeField(verbose_name="Fin de la période de vente")
    
#     # Montants agrégés
#     montant_total_vente = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     montant_total_impayees = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     montant_total_depenses = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     montant_total_avances = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     montant_decaisse = models.DecimalField(max_digits=10, decimal_places=0, default=0)
#     chiffre_affaire = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    
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
#     rapport = models.ForeignKey(
#         RapportVenteNocturne,
#         on_delete=models.CASCADE,
#         related_name="details_boissons", 
#         verbose_name="Rapport de Vente"
#     )
#     boisson = models.ForeignKey(
#         Boisson,
#         on_delete=models.PROTECT,
#         verbose_name="Boisson"
#     )
    
#     # ✅ Champ de la quantité totale vendue
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


############## o4 -10- 2025 Ajout des infos clients ################

# commandes/models.py

# from django.db import models
# from boissons.models import Boisson
# from personnel.models import Personnel
# from .utils import COUNTRY_CODES_CHOICES 


# # Modèle Commande
# class Commande(models.Model):
#     # Statut de la commande
#     STATUT_CHOICES = [
#         ("payer", "Payé"),
#         ("impayee", "Impayée"),
#         ("en_attente", "En attente"),
#     ]

#     # Type de paiement
#     PAIEMENT_CHOICES = [
#         ("liquidite", "Liquidité"),
#         ("orange_money", "Orange Money"),
#         ("hybride", "Hybride"),
#     ]

#     # --- NOUVEAUX CHAMPS CLIENT ---
    
#     # Numéro de téléphone (obligatoire)
#     code_pays_tel = models.CharField(
#         max_length=5, 
#         default="+226", 
#         verbose_name="Indicatif Téléphonique"
#     )
#     numero_telephone = models.CharField(
#         max_length=15, 
#         verbose_name="Numéro de téléphone du client"
#     )

#     # Nom et Prénom du client (non obligatoire)
#     client_nom = models.CharField(
#         max_length=100, 
#         blank=True, 
#         null=True,
#         verbose_name="Nom du client"
#     )
#     client_prenom = models.CharField(
#         max_length=100, 
#         blank=True, 
#         null=True,
#         verbose_name="Prénom du client"
#     )
    
#     # -----------------------------

#     personnel = models.ForeignKey(Personnel, on_delete=models.CASCADE)  # Qui a servi
#     date_commande = models.DateTimeField(auto_now_add=True)
#     statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
#     type_paiement = models.CharField(max_length=20, choices=PAIEMENT_CHOICES)

#  # NOUVEAU CHAMP : Date de validation (paiement ou passage en impayée)
#     date_validation = models.DateTimeField(null=True, blank=True) 

#     # Montants payés
#     montant_remis_client = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     montant_orange = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     montant_liquidite = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

#     # Montant à rendre si trop payé
#     monnaie_a_rendre = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     # Statut de la monnaie (remis ou avoir)
#     statut_monnaie = models.CharField(
#         max_length=20,
#         choices=[("remis", "Remis"), ("avoir", "Avoir"), ("non_applicable", "Non applicable")],
#         default="non_applicable"
#     )

#     # Montant total de la commande
#     montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     # Montant restant dû si impayée
#     montant_restant = models.DecimalField(max_digits=10, decimal_places=2, default=0)

#     def __str__(self):
#         client_info = f"{self.client_prenom or ''} {self.client_nom or ''}".strip() or "Client Anonyme"
#         return f"Commande {self.id} | {self.montant_total} F | Client: {client_info} | Vendeur: {self.personnel.nom_complet}"


# # Boissons dans la commande
# class CommandeItem(models.Model):
#     commande = models.ForeignKey(Commande, related_name="items", on_delete=models.CASCADE)
#     boisson = models.ForeignKey(Boisson, on_delete=models.CASCADE)
#     quantite = models.PositiveIntegerField()
#     montant_boisson = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

#     # Calcul automatique du montant de la boisson
#     def save(self, *args, **kwargs):
#         self.montant_boisson = self.quantite * self.boisson.prix_unitaire
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.quantite} x {self.boisson.nom}"


# # Avoir lié à une commande
# class Avoir(models.Model):
#     STATUT_CHOICES = [
#         ("en_attente", "En attente"),
#         ("regle", "Réglé"),
#     ]

#     commande = models.OneToOneField(Commande, related_name="avoir", on_delete=models.CASCADE)
#     montant = models.DecimalField(max_digits=10, decimal_places=2)
#     date_creation = models.DateTimeField(auto_now_add=True)
#     date_reglement = models.DateTimeField(null=True, blank=True) 

#     statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")

#     def __str__(self):
#         return f"Avoir {self.id} - {self.montant} ({self.get_statut_display()})"


# commandes/models.py

from django.db import models
from boissons.models import Boisson
from personnel.models import Personnel
from ventes.models import RapportVenteNocturne # <-- AJOUTEZ CET IMPORT
from produits.models import Produit


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

    # --- CHAMPS CLIENT ---
    
    # Numéro de téléphone (obligatoire, sans default ni null=True pour forcer la saisie)
    code_pays_tel = models.CharField(
        max_length=5, 
        default="+226", 
        verbose_name="Indicatif Téléphonique"
    )
    numero_telephone = models.CharField(
        max_length=15, 
        verbose_name="Numéro de téléphone du client"
    )

    # Nom et Prénom du client (non obligatoire)
    client_nom = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Nom du client"
    )
    client_prenom = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name="Prénom du client"
    )
    
    # ---------------------
# --- Relation au Rapport de Vente Nocturne ---
    rapport = models.ForeignKey(
        RapportVenteNocturne, 
        on_delete=models.SET_NULL, # Meilleur choix pour ne pas supprimer les commandes si un rapport est effacé
        null=True, 
        blank=True,
        related_name="commandes", # Optionnel mais recommandé
        verbose_name="Rapport de Vente Nocturne"
    )
    
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
        client_info = f"{self.client_prenom or ''} {self.client_nom or ''}".strip() or "Client Anonyme"
        return f"Commande {self.id} | {self.montant_total} F | Client: {client_info} | Vendeur: {self.personnel.nom_complet}"


# Boissons dans la commande
class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, related_name="items", on_delete=models.CASCADE)
    #boisson = models.ForeignKey(Boisson, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)

    quantite = models.PositiveIntegerField()
    montant_produit = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    # Calcul automatique du montant de la boisson
    def save(self, *args, **kwargs):
        self.montant_produit = self.quantite * self.produit.prix_vente
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"


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