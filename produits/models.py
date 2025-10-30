from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, F
from decimal import Decimal

# --- NOUVEAU MODÈLE : CategorieProduit ---
class CategorieProduit(models.Model):
    """Permet de définir dynamiquement les catégories de produits (Boisson, Cuisine, etc.)"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    class Meta:
        verbose_name = "Catégorie de Produit"
        verbose_name_plural = "Catégories de Produits"
        ordering = ['nom']

    def __str__(self):
        return self.nom

# --- CHOIX ENUMÉRÉS ---
NATURE_CHOICES = [
    ('denombrable', 'Dénombrable (Stock)'),
    ('non_denombrable', 'Non Dénombrable (Vente par plat/unité)'),
]

LIEU_CHOICES = [
    ('boite', 'Boîte'),
    ('terrasse', 'Terrasse'),
]

# MISE À JOUR : Retrait du statut 'brouillon'
STATUT_CHOICES = [
    ('en_attente', 'En attente de validation'), # Statut initial après création/fermeture par le personnel
    ('valide', 'Validé et appliqué'),
    ('annule', 'Annulé'),
]

# --- MODÈLE PRINCIPAL : Produit ---
class Produit(models.Model):
    # Classification
    categorie = models.ForeignKey(
        CategorieProduit,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Catégorie de produit"
    )
    nature = models.CharField(
        max_length=20,
        choices=NATURE_CHOICES,
        default='denombrable',
        verbose_name="Nature de stock"
    )
    lieu = models.CharField(
        max_length=20, 
        choices=LIEU_CHOICES, 
        default='boite',
        verbose_name="Lieu de vente"
    )
    
    nom = models.CharField(max_length=100, unique=True)
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Produit actif (en vente)"
    )
    
    # Tarification
    prix_achat = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        verbose_name="Prix d'achat (FCFA)"
    )
    prix_vente = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=0,
        verbose_name="Prix de vente (FCFA)"
    )
    marge = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        editable=False, 
        verbose_name="Marge (Bénéfice)"
    )
    
    # Stock (null=True/blank=True pour les produits non dénombrables)
    stock_initial = models.PositiveIntegerField(default=0, null=True, blank=True)
    stock_actuel = models.PositiveIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        categorie_nom = self.categorie.nom if self.categorie else "Non classé"
        statut = "✅" if self.is_active else "❌"
        stock = f"{self.stock_actuel} u." if self.stock_actuel is not None else "N/A"
        return f"{statut} [{categorie_nom}] {self.nom} ({stock})"

    def save(self, *args, **kwargs):
        # 1. Calcul de la marge : Prix de Vente - Prix d'Achat
        self.marge = self.prix_vente - self.prix_achat
        
        # 2. Gestion de stock pour les non-dénombrables
        if self.nature == 'non_denombrable':
            self.stock_initial = None
            self.stock_actuel = None
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-is_active', 'categorie__nom', 'nom']

# ---------------------------------------------------------------------------------------
# --- NOUVEAUX MODÈLES DE GESTION D'INVENTAIRE (Groupe et Ligne) ---
# ---------------------------------------------------------------------------------------

class Inventaire(models.Model):
    """
    Modèle qui regroupe une session d'inventaire, les totaux globaux
    et la logique de validation.
    """
    nom = models.CharField(max_length=150, verbose_name="Nom de la session d'inventaire")
    
    # Gestion de la validation
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente', # Statut initial, signifiant "Fermé" pour le personnel
        verbose_name="Statut de la validation"
    )
    
    # Personnel qui a initié la session
    initiateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='inventaires_initiés',
        verbose_name="Personnel initiateur de l'inventaire"
    )
    
    # Secrétaire ou manager qui valide
    secretaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='inventaires_validés',
        verbose_name="Secrétaire/Manager Validateur"
    )
    
    date_creation = models.DateTimeField(default=timezone.now)
    date_validation = models.DateTimeField(null=True, blank=True) # Date de validation

    # --- CHAMPS TOTAUX AUTO-CALCULÉS (Sommes des LignesInventaire liées) ---
    produits_perdus_total = models.PositiveIntegerField(default=0, verbose_name="Total Qté Perdue")
    produits_retrouves_total = models.PositiveIntegerField(default=0, verbose_name="Total Qté Retrouvée")
    
    prix_achat_perte_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total PA Perdu")
    prix_vente_perte_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total PV Perdu")
    
    prix_achat_retrouves_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total PA Retrouvé")
    prix_vente_retrouves_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total PV Retrouvé")
    
    marge_perdue_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Marge Perdue")
    marge_retrouvee_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Marge Retrouvée")
    
    gain_net_global = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Gain Net Global")

    def calculer_totaux_globaux(self):
        """
        Calcule et met à jour tous les champs totaux de l'inventaire
        en agrégeant les valeurs des lignes liées.
        """
        # Utiliser `lignes` comme related_name de LigneInventaire
        aggregation = self.lignes.filter(produit__nature='denombrable').aggregate(
            produits_perdus_total=Sum('quantite_perte'),
            produits_retrouves_total=Sum('quantite_retrouvee'),
            
            prix_achat_perte_total=Sum('prix_achat_perte'),
            prix_vente_perte_total=Sum('prix_vente_perte'),
            
            prix_achat_retrouves_total=Sum('prix_achat_retrouves'),
            prix_vente_retrouves_total=Sum('prix_vente_retrouves'),
            
            marge_perdue_total=Sum('marge_perdue'),
            marge_retrouvee_total=Sum('marge_retrouvee'),
            
            gain_net_global=Sum('gain_net_ligne')
        )
        
        # S'assurer qu'on utilise 0 ou 0.0 si le résultat de l'agrégation est None
        self.produits_perdus_total = aggregation.get('produits_perdus_total') or 0
        self.produits_retrouves_total = aggregation.get('produits_retrouves_total') or 0
        self.prix_achat_perte_total = aggregation.get('prix_achat_perte_total') or Decimal(0)
        self.prix_vente_perte_total = aggregation.get('prix_vente_perte_total') or Decimal(0)
        self.prix_achat_retrouves_total = aggregation.get('prix_achat_retrouves_total') or Decimal(0)
        self.prix_vente_retrouves_total = aggregation.get('prix_vente_retrouves_total') or Decimal(0)
        self.marge_perdue_total = aggregation.get('marge_perdue_total') or Decimal(0)
        self.marge_retrouvee_total = aggregation.get('marge_retrouvee_total') or Decimal(0)
        self.gain_net_global = aggregation.get('gain_net_global') or Decimal(0)
        
        # Sauvegarder les totaux
        self.save()


    def appliquer_validation(self, utilisateur_secretaire):
        """
        Valide l'inventaire et applique les ajustements de stock.
        """
        if self.statut != 'en_attente':
            raise ValidationError("Seuls les inventaires en attente de validation peuvent être validés.")

        with transaction.atomic():
            # 1. Recalculer et enregistrer les totaux globaux pour l'enregistrement final
            self.calculer_totaux_globaux()
            
            # 2. Parcourir et appliquer l'ajustement pour chaque ligne dénombrable
            for ligne in self.lignes.filter(produit__nature='denombrable'):
                produit = Produit.objects.select_for_update().get(pk=ligne.produit.pk)
                
                q_retrouvee = ligne.quantite_retrouvee or 0
                q_perdue = ligne.quantite_perte or 0
                quantite_nette_impactee = q_retrouvee - q_perdue
                
                nouveau_stock = produit.stock_actuel + quantite_nette_impactee
                
                if nouveau_stock < 0:
                    raise ValidationError(f"L'ajustement pour le produit '{produit.nom}' résulterait en un stock négatif.")
                
                # Mise à jour du Produit
                produit.stock_actuel = nouveau_stock
                produit.save() 
                
                # Mise à jour de la LigneInventaire pour la traçabilité
                # Stock avant l'ajustement
                ligne.stock_initial = produit.stock_actuel - quantite_nette_impactee 
                # Stock après l'ajustement
                ligne.stock_actuel = nouveau_stock
                ligne.save()
            
            # 3. Finaliser l'Inventaire
            self.statut = 'valide'
            self.secretaire = utilisateur_secretaire
            self.date_validation = timezone.now()
            self.save() # Sauvegarde du statut et du validateur

        return True

    def __str__(self):
        statut_label = dict(STATUT_CHOICES).get(self.statut, self.statut)
        gain = f"{self.gain_net_global:.2f} FCFA"
        return f"Inventaire {self.nom} - Statut: {statut_label} - Gain Net: {gain}"

    class Meta:
        ordering = ("-date_creation",)
        verbose_name = "Session d'Inventaire"
        verbose_name_plural = "Sessions d'Inventaire"


class LigneInventaire(models.Model):
    """
    Représente une ligne de produit spécifique dans le cadre d'une session d'inventaire.
    Contient les quantités ajustées et les calculs financiers par produit.
    """
    inventaire = models.ForeignKey(
        Inventaire,
        on_delete=models.CASCADE,
        related_name="lignes",
        verbose_name="Session d'Inventaire parente"
    )
    
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE, 
        related_name="lignes_inventaire",
        verbose_name="Produit concerné"
    )
    
    # Champs d'état du stock (enregistrés à la validation pour la traçabilité)
    stock_initial = models.PositiveIntegerField(null=True, blank=True, editable=False)
    stock_actuel = models.PositiveIntegerField(null=True, blank=True, editable=False)
    
    # --- CHAMPS D'AJUSTEMENT (Saisie par le Personnel) ---
    stock_compte = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock Physique Compté",
        null=True, 
        blank=True
    )
    quantite_perte = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité Perdue/Endommagée (Calculé ou Saisi)"
    )
    quantite_retrouvee = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité Retrouvée/Ajoutée (Calculé ou Saisi)"
    )
    
    justification = models.TextField(blank=True, null=True)
    
    # --- CHAMPS CALCULÉS PAR LIGNE ---
    
    # Perte
    prix_achat_perte = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="PA Perte")
    prix_vente_perte = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="PV Perte")
    marge_perdue = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="Marge Perdue")
    
    # Retrouvé
    prix_achat_retrouves = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="PA Retrouvé")
    prix_vente_retrouves = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="PV Retrouvé")
    marge_retrouvee = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="Marge Retrouvée")
    
    # Résultat Net
    gain_net_ligne = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False, verbose_name="Gain Net de la Ligne")

    def save(self, *args, **kwargs):
        # Assurez-vous que les quantités sont des nombres
        q_retrouvee = self.quantite_retrouvee or 0
        q_perdue = self.quantite_perte or 0

        # Calcul des métriques financières uniquement si le produit est dénombrable et a des prix définis
        if self.produit.nature == 'denombrable':
            produit = self.produit
            marge_unitaire = produit.marge
            prix_achat = produit.prix_achat
            prix_vente = produit.prix_vente
            
            # Calculs de perte
            self.prix_achat_perte = prix_achat * Decimal(q_perdue)
            self.prix_vente_perte = prix_vente * Decimal(q_perdue)
            self.marge_perdue = marge_unitaire * Decimal(q_perdue)
            
            # Calculs de retrouvé
            self.prix_achat_retrouves = prix_achat * Decimal(q_retrouvee)
            self.prix_vente_retrouves = prix_vente * Decimal(q_retrouvee)
            self.marge_retrouvee = marge_unitaire * Decimal(q_retrouvee)
            
            # Calcul du gain net de la ligne
            self.gain_net_ligne = self.marge_retrouvee - self.marge_perdue
        else:
             # Réinitialiser les champs calculés pour les produits non dénombrables
            self.prix_achat_perte = Decimal(0)
            self.prix_vente_perte = Decimal(0)
            self.marge_perdue = Decimal(0)
            self.prix_achat_retrouves = Decimal(0)
            self.prix_vente_retrouves = Decimal(0)
            self.marge_retrouvee = Decimal(0)
            self.gain_net_ligne = Decimal(0)

        super().save(*args, **kwargs)
        
        # Note: La mise à jour des totaux de l'Inventaire parent doit idéalement être gérée par 
        # un signal post_save ou dans la vue pour des raisons de performance. 

    def __str__(self):
        q_perte = self.quantite_perte or 0
        q_retrouvee = self.quantite_retrouvee or 0
        return f"Ligne {self.inventaire.nom} : {self.produit.nom} (P: {q_perte} | R: {q_retrouvee})"

    class Meta:
        ordering = ("produit__nom",)
        verbose_name = "Ligne d'Inventaire"
        verbose_name_plural = "Lignes d'Inventaire"


################ 27 -10- 2025 ##############

# ---------------------------------------------------------------------------------------
# MODÈLES DE GESTION DES FOURNISSEURS ET APPROVISIONNEMENTS
# ---------------------------------------------------------------------------------------

class Fournisseur(models.Model):
    nom = models.CharField(max_length=150, unique=True, verbose_name="Nom du Fournisseur")
    telephone = models.CharField(max_length=20, unique=True, verbose_name="Téléphone")
    adresse = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ['nom']

    def __str__(self):
        return self.nom

class Approvisionnement(models.Model):
    nom = models.CharField(max_length=150, verbose_name="Nom/Référence de l'Approvisionnement")
    date_approvisionnement = models.DateTimeField(default=timezone.now, verbose_name="Date de Réception")
    
    personnel = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='approvisionnements_enregistres',
        verbose_name="Personnel ayant enregistré"
    )
    
    fournisseur = models.ForeignKey(
        Fournisseur, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='approvisionnements',
        verbose_name="Fournisseur"
    )
    
    telephone_fournisseur = models.CharField(
        max_length=20, 
        editable=False, 
        blank=True, 
        null=True, 
        verbose_name="Téléphone (snapshot)"
    )
    
    cout_transport = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Coût du Transport"
    )
    
    # NOUVEAU CHAMP - Quantité totale reçue
    quantite_recue_total = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Quantité Totale Reçue"
    )
    
    montant_achats_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        editable=False, 
        verbose_name="Montant Total des Achats (Produits)"
    )

    cout_approvisionnement_global = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        editable=False, 
        verbose_name="Coût Global de l'Approvisionnement"
    )
    
    quantite_perdue_total = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Quantité Totale Perdue"
    )

    montant_perte_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        editable=False, 
        verbose_name="Montant Total des Pertes"
    )
    
    # CHAMPS DE CONTRÔLE/VALIDATION
    controleur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approvisionnements_controles',
        verbose_name="Contrôleur/Validateur"
    )
    
    date_validation = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de Validation/Contrôle"
    )
    
    # Utilisation du statut pour déterminer la validation
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='en_attente',
        verbose_name="Statut de l'Approvisionnement"
    )

    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Approvisionnement"
        verbose_name_plural = "Approvisionnements"
        ordering = ("-date_approvisionnement",)
        
    def save(self, *args, **kwargs):
        if self.fournisseur and not self.telephone_fournisseur:
            self.telephone_fournisseur = self.fournisseur.telephone
            
        super().save(*args, **kwargs)


class LigneApprovisionnement(models.Model):
    approvisionnement = models.ForeignKey(
        Approvisionnement,
        on_delete=models.CASCADE,
        related_name="lignes_appro",
        verbose_name="Approvisionnement parent"
    )
    
    produit = models.ForeignKey(
        Produit, 
        on_delete=models.CASCADE, 
        related_name="lignes_appro",
        verbose_name="Produit concerné"
    )
    
    lieu = models.CharField(
        max_length=20, 
        choices=LIEU_CHOICES, 
        default='boite',
        verbose_name="Lieu de Stockage"
    )
    
    quantite_recue = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité Approvisionnée (Reçue)"
    )
    
    quantite_endommagee = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité Endommagée/Perdue à la Réception"
    )
    
    quantite_nette = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name="Quantité Nette (pour le stock)"
    )

    montant_total_produit = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Coût Total Facturé pour ce Produit"
    )
    
    prix_achat_unitaire = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        editable=False, 
        verbose_name="Prix d'Achat Unitaire (Calculé)"
    )
    
    montant_perte = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        editable=False,
        verbose_name="Montant Perte (Endommagement)"
    )

    @property
    def cout_total_ligne_net(self):
        """Le coût réel des produits qui entrent en stock (Montant Facturé - Perte monétaire)."""
        return self.montant_total_produit - self.montant_perte
    
    class Meta:
        verbose_name = "Ligne d'Approvisionnement"
        verbose_name_plural = "Lignes d'Approvisionnement"
        ordering = ("produit__nom",)
        
    def save(self, *args, **kwargs):
        self.quantite_nette = self.quantite_recue - self.quantite_endommagee
        
        if self.quantite_nette < 0:
            raise ValidationError("La quantité endommagée ne peut pas dépasser la quantité reçue.")

        # 1. Calcul du Prix d'Achat Unitaire
        if self.quantite_recue > 0:
            self.prix_achat_unitaire = self.montant_total_produit / self.quantite_recue
        else:
            self.prix_achat_unitaire = Decimal('0.00')

        # 2. Calcul de la Perte Monétaire (Qté Endommagée * PA Unitaire)
        self.montant_perte = self.quantite_endommagee * self.prix_achat_unitaire
        
        # NOTE : Nous ne touchons pas au stock ici, l'update est dans la vue de validation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ligne {self.approvisionnement.nom} : {self.produit.nom} ({self.quantite_nette} net)"