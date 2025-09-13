# from django.db import models                 # module pour créer des modèles Django
# from django.conf import settings             # pour utiliser le modèle User (AUTH_USER_MODEL)
# from django.utils import timezone            # pour gérer les dates
# from django.core.exceptions import ValidationError  # pour les validations personnalisées
# from django.db import transaction            # pour les transactions atomiques

# # =========================
# # Modèle Boisson
# # =========================
# class Boisson(models.Model):
#     # Nom unique de la boisson (ex: Coca Cola)
#     nom = models.CharField(max_length=100, unique=True)

#     # Prix unitaire de la boisson (2 décimales pour centimes, max 10 chiffres)
#     prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

#     # Stock initial : valeur après la nuit précédente
#     # Ce champ est défini une seule fois et ne sera plus modifié ensuite
#     stock_initial = models.PositiveIntegerField(default=0)

#     # Stock actuel : valeur courante au début de la nouvelle nuit
#     stock_actuel = models.PositiveIntegerField(default=0)

#     # Date de création de la boisson
#     created_at = models.DateTimeField(auto_now_add=True)

#     # Représentation lisible de la boisson
#     def __str__(self):
#         return f"{self.nom} — {self.stock_actuel} unités"

#     # Méthode save pour protéger stock_initial
#     def save(self, *args, **kwargs):
#         # Si la boisson existe déjà (édition)
#         if self.pk:
#             try:
#                 ancien = Boisson.objects.get(pk=self.pk)
#                 # On conserve l'ancienne valeur de stock_initial
#                 if ancien.stock_initial is not None:
#                     self.stock_initial = ancien.stock_initial
#             except Boisson.DoesNotExist:
#                 pass
#         super().save(*args, **kwargs)

# # =========================
# # Modèle HistoriqueStock
# # =========================
# class HistoriqueStock(models.Model):
#     # Relation avec la boisson
#     boisson = models.ForeignKey(Boisson, on_delete=models.CASCADE, related_name="historiques")

#     # Stock avant le contrôle (sera rempli automatiquement depuis Boisson.stock_actuel)
#     stock_initial = models.PositiveIntegerField()

#     # Stock après contrôle (saisi par le caissier)
#     stock_actuel = models.PositiveIntegerField()

#     # Justification obligatoire si stock_actuel != stock_initial
#     justification = models.TextField(blank=True, null=True)

#     # Caissier qui effectue le contrôle
#     caissier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

#     # Date du contrôle
#     date = models.DateTimeField(default=timezone.now)

#     # =========================
#     # Options supplémentaires
#     # =========================
#     class Meta:
#         ordering = ("-date",)  # tri par date décroissante, du plus récent au plus ancien

#     # =========================
#     # Validation personnalisée
#     # =========================
#     def clean(self):
#         """
#         Si stock_actuel est différent du stock_initial, 
#         la justification est obligatoire.
#         """
#         if self.stock_actuel != self.stock_initial and not (self.justification and self.justification.strip()):
#             raise ValidationError("Une justification est obligatoire si le stock actuel est différent du stock initial.")

#     # =========================
#     # Sauvegarde avec logique spéciale
#     # =========================
#     def save(self, *args, **kwargs):
#         # Détecte si c'est un nouvel objet (pas encore d'id)
#         creating = self.pk is None

#         if creating:
#             # Au moment de la création, stock_initial = stock_actuel de la boisson
#             self.stock_initial = self.boisson.stock_actuel

#         # Validation complète (appel de clean + validations Django)
#         self.full_clean()

#         # Transaction atomique : tout est sauvegardé ensemble
#         with transaction.atomic():
#             # Enregistrement du contrôle dans la base
#             super().save(*args, **kwargs)

#             # Mise à jour du stock_actuel de la boisson
#             if self.boisson.stock_actuel != self.stock_actuel:
#                 self.boisson.stock_actuel = self.stock_actuel
#                 # On ne touche pas au stock_initial de Boisson, uniquement stock_actuel
#                 self.boisson.save(update_fields=["stock_actuel"])

#     # Représentation lisible
#     def __str__(self):
#         return f"{self.boisson.nom} — {self.date.strftime('%Y-%m-%d %H:%M')} (init: {self.stock_initial} / actuel: {self.stock_actuel})"


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
        return f"{self.nom} — {self.stock_actuel} unités"

    # Méthode save personnalisée pour protéger stock_initial après création
    def save(self, *args, **kwargs):
        # Si l'objet existe déjà (édition), on récupère l'ancien objet
        if self.pk:
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
