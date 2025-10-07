
# Import du module models de Django pour définir des modèles
from django.db import models
# Import de settings pour référencer AUTH_USER_MODEL (utilisateur personnalisé si présent)
from django.conf import settings
# Import de timezone pour gérer les dates/horaires par défaut
from django.utils import timezone
# Import de ValidationError pour lancer des erreurs de validation personnalisées
from django.core.exceptions import ValidationError
# Import de transaction pour exécuter des opérations atomiques (tout ou rien)
from django.db import transaction


# Déclaration du modèle Boisson (fiche principale d'une boisson)
class Boisson(models.Model):
    # Nouveau champ : lieu de vente
    LIEU_CHOICES = [
        ('boite', 'Boîte'),
        ('terrasse', 'Terrasse'),
    ]
    lieu = models.CharField(
        max_length=20, 
        choices=LIEU_CHOICES, 
        default='boite',
        verbose_name="Lieu de vente"
    )
    
    # Champ 'nom' : chaîne de caractères, unique pour éviter doublons
    nom = models.CharField(max_length=100, unique=True)
    # Champ 'prix_unitaire' : prix à 2 décimales (DecimalField pour précision monétaire)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    # Champ 'stock_initial' : valeur initiale (définie une seule fois)
    stock_initial = models.PositiveIntegerField(default=0)
    # Champ 'stock_actuel' : valeur courante du stock
    stock_actuel = models.PositiveIntegerField(default=0)
    # Champ 'created_at' : date de création automatique
    created_at = models.DateTimeField(auto_now_add=True)

    # Méthode de représentation texte de l'objet (utilisée par l'admin et le shell)
    def __str__(self):
        return f"{self.nom} ({self.get_lieu_display()}) — {self.stock_actuel} unités"

    # Méthode save personnalisée pour protéger stock_initial après création
    def save(self, *args, **kwargs):
        # Si c'est une nouvelle boisson (création)
        if not self.pk:
            # Le stock initial prend la valeur du stock actuel saisi
            self.stock_initial = self.stock_actuel
        else:
            # Si l'objet existe déjà (édition), on récupère l'ancien objet
            try:
                # Récupération de l'ancienne instance depuis la base
                ancien = Boisson.objects.get(pk=self.pk)
                # On conserve l'ancienne valeur de stock_initial pour éviter modifications accidentelles
                if ancien.stock_initial is not None:
                    self.stock_initial = ancien.stock_initial
            except Boisson.DoesNotExist:
                # Si l'objet n'existe plus pour une raison quelconque, on ignore
                pass
        # Appel du save parent pour enregistrer l'objet
        super().save(*args, **kwargs)

    # Classe Meta pour l'administration
    class Meta:
        verbose_name = "Boisson"
        verbose_name_plural = "Boissons"
        ordering = ['lieu', 'nom']  # Tri par lieu puis par nom

# Déclaration du modèle HistoriqueStock (journal des contrôles journaliers)
class HistoriqueStock(models.Model):
    # Champ relationnel vers la boisson concernée
    boisson = models.ForeignKey(Boisson, on_delete=models.CASCADE, related_name="historiques")
    # Champ 'stock_initial' : valeur antérieure (copiée depuis Boisson.stock_actuel lors de la création)
    stock_initial = models.PositiveIntegerField()
    # Champ 'stock_actuel' : valeur constatée au moment du contrôle
    stock_actuel = models.PositiveIntegerField()
    # Champ 'justification' : texte libre expliquant l'écart si présent
    justification = models.TextField(blank=True, null=True)
    # Champ 'caissier' : utilisateur qui a effectué le contrôle (référence au modèle user)
    caissier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    # Champ 'date' : date/heure du contrôle, par défaut maintenant
    date = models.DateTimeField(default=timezone.now)

    # Classe Meta pour options du modèle (ici tri par date décroissante)
    class Meta:
        # Tri par défaut : les enregistrements les plus récents en premier
        ordering = ("-date",)

    # Méthode clean pour validations personnalisées avant enregistrement
    def clean(self):
        # Si stock_actuel diffère de stock_initial ET qu'aucune justification valide n'est fournie
        if self.stock_actuel != self.stock_initial and not (self.justification and self.justification.strip()):
            # Lever une erreur de validation empêchant la sauvegarde
            raise ValidationError("Une justification est obligatoire si le stock actuel est différent du stock initial.")

    # Méthode save personnalisée pour logique d'héritage et mise à jour atomique
    def save(self, *args, **kwargs):
        # On détecte si on crée un nouvel enregistrement (pk absent)
        creating = self.pk is None

        # Si création : remplir stock_initial avec la valeur courante présente sur la fiche Boisson
        if creating:
            # Récupération de la valeur du stock actuel de la boisson pour la mettre en stock_initial
            self.stock_initial = self.boisson.stock_actuel

            # Si le stock est correct, on met automatiquement la justification
            if self.stock_actuel == self.stock_initial:
                self.justification = "Stock correct"
                
        # Appel de full_clean pour exécuter clean() et autres validations Django
        self.full_clean()

        # Utilisation d'une transaction atomique pour assurer cohérence :
        # on enregistre l'historique puis on met à jour la fiche Boisson
        with transaction.atomic():
            # Appel du save parent pour persister HistoriqueStock
            super().save(*args, **kwargs)

            # Si la valeur du stock actuel sur la fiche Boisson est différente de celle saisie,
            # on met à jour Boisson.stock_actuel (sans toucher stock_initial)
            if self.boisson.stock_actuel != self.stock_actuel:
                # Affectation du nouveau stock actuel à la boisson
                self.boisson.stock_actuel = self.stock_actuel
                # Sauvegarde de la boisson en ne mettant à jour que le champ 'stock_actuel'
                self.boisson.save(update_fields=["stock_actuel"])

    # Représentation lisible de l'historique (utilisée par admin et affichages)
    def __str__(self):
        return f"{self.boisson.nom} — {self.date.strftime('%Y-%m-%d %H:%M')} (init: {self.stock_initial} / actuel: {self.stock_actuel})"
