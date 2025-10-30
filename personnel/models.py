# from django.db import models

# # Create your models here.
# from django.db import models
# from calendar import monthrange
# from datetime import date
# from django.contrib.auth import get_user_model # NOUVEAU

# # Récupérer le modèle d'utilisateur actif (généralement django.contrib.auth.models.User)
# User = get_user_model() # NOUVEAU
# # Définition des rôles possibles
# ROLE_CHOICES = [
#     ("hotesse", "Hôtesse"),
#     ("technicien", "Technicien de surface"),
#     ("caissier", "Caissier"),
#     ("secretaire", "Secrétaire"),
#     ("boss", "Boss"),
#     ("dj", "DJ"),
#     ("manager", "Manager"),
#     ("portier", "Portier"),
#     ("cuisinier", "Cuisinier"),
# ]

# # Définition des lieux de travail
# LIEU_CHOICES = [
#     ("terrasse", "Terrasse"),
#     ("boite", "Boîte"),
# ]

# # Définition des jours de la semaine
# JOUR_CHOICES = [
#     ("lundi", "Lundi"),
#     ("mardi", "Mardi"),
#     ("mercredi", "Mercredi"),
#     ("jeudi", "Jeudi"),
#     ("vendredi", "Vendredi"),
#     ("samedi", "Samedi"),
#     ("dimanche", "Dimanche"),
# ]

# class Personnel(models.Model):

#     user = models.OneToOneField(
#         User, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         related_name='personnel_profile'
#     ) # <-- CE CHAMP CORRIGE L'ERREUR FieldError

#     # Identifiant unique (CNIB ou Passeport)
#     id = models.CharField(max_length=20, primary_key=True)
#     # Nom et prénom
#     nom = models.CharField(max_length=100)
#     prenom = models.CharField(max_length=100)
#     # Rôle
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES)
#     # Lieu de travail : terrasse ou boîte
#     lieu_travail = models.CharField(max_length=10, choices=LIEU_CHOICES, blank=True, null=True)
#     # Salaire de base
#     salaire = models.DecimalField(max_digits=10, decimal_places=2)
    
#     # Jours de repos dynamiques (liste JSON)
#     jours_repos = models.JSONField(default=list, blank=True)  # ex: ["lundi", "mardi"]
    
#     # Nombre de jours de travail calculé pour le mois
#     jours_travail = models.PositiveIntegerField(default=30)

#     def calculer_jours_travail(self, annee, mois):
#         """Calcule le nombre de jours de travail dans le mois selon les jours de repos dynamiques"""
#         total_jours = monthrange(annee, mois)[1]  # nombre de jours dans le mois
#         jours_travail = 0
        
#         # Mapping français -> datetime weekday
#         jours_fr_to_en = {
#             "lundi": "monday",
#             "mardi": "tuesday",
#             "mercredi": "wednesday",
#             "jeudi": "thursday",
#             "vendredi": "friday",
#             "samedi": "saturday",
#             "dimanche": "sunday"
#         }
        
#         # Parcours de chaque jour du mois
#         for j in range(1, total_jours + 1):
#             d = date(annee, mois, j)
#             nom_jour = d.strftime("%A").lower()  # nom du jour en anglais
            
#             # Si le jour fait partie des jours de repos, on l'exclut
#             for jr in self.jours_repos:
#                 if nom_jour == jours_fr_to_en.get(jr):
#                     break
#             else:
#                 jours_travail += 1  # si pas dans jours_repos, c'est un jour travaillé

#         self.jours_travail = jours_travail
#         return self.jours_travail

#     def salaire_journalier(self):
#         """Calcule le salaire journalier selon les jours de travail"""
#         if self.jours_travail > 0:
#             return self.salaire / self.jours_travail
#         return 0

#     # def __str__(self):
#     #     return f"{self.nom} {self.prenom} ({self.role})"

#     # 👇 AJOUTEZ CETTE PROPRIÉTÉ
#     @property
#     def nom_complet(self):
#         """Retourne le nom complet (Prénom Nom)."""
#         return f"{self.prenom} {self.nom}"

#     def __str__(self):
#         return self.nom_complet # Utilise la nouvelle propriété


########################################

from django.db import models
from calendar import monthrange
from datetime import date
from django.contrib.auth import get_user_model

User = get_user_model() 

# Définitions des choix
ROLE_CHOICES = [
    ("hotesse", "Hôtesse"), ("technicien", "Technicien de surface"),
    ("caissier", "Caissier"), ("secretaire", "Secrétaire"),
    ("boss", "Boss"), ("dj", "DJ"), ("manager", "Manager"),
    ("portier", "Portier"), ("cuisinier", "Cuisinier"), ('serveur', 'Serveur')
]
LIEU_CHOICES = [("terrasse", "Terrasse"), ("boite", "Boîte")]
JOUR_CHOICES = [
    ("lundi", "Lundi"), ("mardi", "Mardi"), ("mercredi", "Mercredi"),
    ("jeudi", "Jeudi"), ("vendredi", "Vendredi"), ("samedi", "Samedi"),
    ("dimanche", "Dimanche"),
]

class Personnel(models.Model):

    # Lien One-to-One avec le modèle User de Django pour l'authentification
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,  # On utilise CASCADE au lieu de SET_NULL
        
        related_name='personnel_profile'
    ) 

    change_password_required = models.BooleanField(default=True) 

    id = models.CharField(max_length=20, primary_key=True) # ID unique (CNIB/Passeport)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    lieu_travail = models.CharField(max_length=10, choices=LIEU_CHOICES, blank=True, null=True)
    salaire = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Stocke les jours de repos choisis (ex: ["lundi", "mardi"])
    jours_repos = models.JSONField(default=list, blank=True)
    jours_travail = models.PositiveIntegerField(default=30)

    def calculer_jours_travail(self, annee, mois):
        """Calcule le nombre de jours de travail dans le mois selon les jours de repos."""
        total_jours_mois = monthrange(annee, mois)[1]
        jours_travail = 0
        
        # Mapping français vers l'anglais (pour utiliser d.strftime("%A").lower())
        jours_fr_to_en = {
            "lundi": "monday", "mardi": "tuesday", "mercredi": "wednesday",
            "jeudi": "thursday", "vendredi": "friday", "samedi": "saturday",
            "dimanche": "sunday"
        }
        
        # Convertit la liste des jours de repos stockés en anglais
        jours_repos_en = [jours_fr_to_en.get(jr.lower()) for jr in self.jours_repos]

        for j in range(1, total_jours_mois + 1):
            try:
                d = date(annee, mois, j)
            except ValueError:
                continue
                
            nom_jour_en = d.strftime("%A").lower()
            
            # Si le jour est un jour de repos, on passe
            if nom_jour_en in jours_repos_en:
                continue
            else:
                jours_travail += 1
                
        self.jours_travail = jours_travail
        return self.jours_travail
        
    def salaire_journalier(self):
        """Calcule le salaire journalier"""
        if self.jours_travail > 0:
            return self.salaire / self.jours_travail
        return 0

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    def __str__(self):
        return self.nom_complet