# # from django import forms
# # from .models import Personnel, JOUR_CHOICES

# # class PersonnelForm(forms.ModelForm):
# #     # Formulaire pour ajouter ou modifier un employé
    
# #     # Champ multi-select pour les jours de repos dynamiques
# #     jours_repos = forms.MultipleChoiceField(
# #         choices=JOUR_CHOICES,
# #         widget=forms.CheckboxSelectMultiple,
# #         required=False,
# #         label="Jours de repos"
# #     )

# #     class Meta:
# #         model = Personnel
# #         fields = ["id", "nom", "prenom", "role", "lieu_travail", "salaire", "jours_repos"]

# #     def clean(self):
# #         """Validation complémentaire"""
# #         cleaned = super().clean()
# #         lieu = cleaned.get("lieu_travail")
# #         jours = cleaned.get("jours_repos", [])
        
# #         # Si Boîte, il doit y avoir au moins 2 jours de repos
# #         if lieu == "boite" and len(jours) < 2:
# #             raise forms.ValidationError("Pour la Boîte, veuillez choisir au moins 2 jours de repos.")
        
# #         # Pour Terrasse, au moins 1 jour
# #         if lieu == "terrasse" and len(jours) < 1:
# #             raise forms.ValidationError("Pour la Terrasse, veuillez choisir au moins 1 jour de repos.")
        
# #         return cleaned


# ####################################################
# from django import forms
# from django.db import transaction
# from django.contrib.auth import get_user_model
# from .models import Personnel, JOUR_CHOICES

# User = get_user_model()

# # ----------------------------------------------
# # 1. Formulaire de CRÉATION (Employés réguliers)
# # ----------------------------------------------
# # class PersonnelCreationForm(forms.ModelForm):
# #     # Champs pour le compte User
# #     username = forms.CharField(max_length=150, label="Nom d'utilisateur (Login)", help_text="Ex: 'jdupont'") 
# #     email = forms.EmailField(label="Adresse E-mail", help_text="Nécessaire pour la réinitialisation de mot de passe.")
# #     password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe Initial", help_text="À communiquer à l'employé.")
    
# #     # Champ du profil Personnel
# #     jours_repos = forms.MultipleChoiceField(
# #         choices=JOUR_CHOICES,
# #         widget=forms.CheckboxSelectMultiple,
# #         required=False,
# #         label="Jours de repos"
# #     )

# #     class Meta:
# #         model = Personnel
# #         fields = ["id", "nom", "prenom", "role", "lieu_travail", "salaire", "jours_repos", 'username', 'email', 'password']
        
# #     def clean(self):
# #         cleaned = super().clean()
# #         username = cleaned.get("username")
# #         lieu = cleaned.get("lieu_travail")
# #         jours = cleaned.get("jours_repos", [])
        
# #         if username and User.objects.filter(username=username).exists():
# #             self.add_error('username', "Ce nom d'utilisateur est déjà utilisé.")
            
# #         if lieu == "boite" and len(jours) < 2:
# #             self.add_error('jours_repos', "Pour la Boîte, veuillez choisir au moins 2 jours de repos.")
# #         if lieu == "terrasse" and len(jours) < 1:
# #             self.add_error('jours_repos', "Pour la Terrasse, veuillez choisir au moins 1 jour de repos.")
        
# #         return cleaned

# #     @transaction.atomic
# #     def save(self, commit=True):
# #         user = User.objects.create_user(
# #             username=self.cleaned_data['username'],
# #             email=self.cleaned_data['email'], 
# #             password=self.cleaned_data['password'],
# #             is_staff=True
# #         )
        
# #         personnel = super().save(commit=False)
# #         personnel.user = user
        
# #         if commit:
# #             personnel.save()
            
# #         return personnel

# # ----------------------------------------------
# # 1. Formulaire de CRÉATION (Employés réguliers)
# # ----------------------------------------------
# class PersonnelCreationForm(forms.ModelForm):
#     # ATTENTION : 'username' est RETIRÉ d'ici car il sera généré automatiquement
#     email = forms.EmailField(label="Adresse E-mail", help_text="Nécessaire pour l'activation et la réinitialisation de mot de passe.")
#     password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe Initial", help_text="Sera écrasé par le premier changement de l'employé.")
    
#     # Champ du profil Personnel
#     jours_repos = forms.MultipleChoiceField(
#         choices=JOUR_CHOICES,
#         widget=forms.CheckboxSelectMultiple,
#         required=False,
#         label="Jours de repos"
#     )

#     class Meta:
#         model = Personnel
#         # RETRAIT de 'username' des fields
#         fields = ["id", "nom", "prenom", "role", "lieu_travail", "salaire", "jours_repos", 'email', 'password']
        
#     def clean(self):
#         cleaned = super().clean()
#         email = cleaned.get("email")
#         lieu = cleaned.get("lieu_travail")
#         jours = cleaned.get("jours_repos", [])
        
#         # CORRECTION : Vérification de l'unicité de l'e-mail (Obligatoire pour le flow d'activation)
#         if email and User.objects.filter(email=email).exists():
#             self.add_error('email', "Cette adresse e-mail est déjà utilisée par un autre employé. L'e-mail doit être unique.")
            
#         if lieu == "boite" and len(jours) < 2:
#             self.add_error('jours_repos', "Pour la Boîte, veuillez choisir au moins 2 jours de repos.")
#         if lieu == "terrasse" and len(jours) < 1:
#             self.add_error('jours_repos', "Pour la Terrasse, veuillez choisir au moins 1 jour de repos.")
        
#         return cleaned

#     @transaction.atomic
#     def save(self, commit=True):
#         # 1. Sauvegarde le Personnel pour obtenir l'ID (pk)
#         personnel = super().save(commit=False)
#         if commit:
#             personnel.save()
        
#         # 2. Génération automatique de l'username à partir de l'ID
#         # On utilise le PK de l'objet Personnel comme username
#         auto_username = str(personnel.pk) 
        
#         # 3. Création du compte User avec l'username auto-généré
#         user = User.objects.create_user(
#             username=auto_username,
#             email=self.cleaned_data['email'], 
#             password=self.cleaned_data['password'],
#             is_staff=True
#         )
        
#         # 4. Lien du Personnel avec l'utilisateur nouvellement créé
#         personnel.user = user
        
#         if commit:
#             # Re-sauvegarde pour lier l'objet User à l'objet Personnel
#             personnel.save() 
            
#         return personnel

# # ----------------------------------------------
# # 2. Formulaire de MODIFICATION
# # ----------------------------------------------
# class PersonnelEditForm(forms.ModelForm):
#     jours_repos = forms.MultipleChoiceField(
#         choices=JOUR_CHOICES,
#         widget=forms.CheckboxSelectMultiple,
#         required=False,
#         label="Jours de repos"
#     )

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance and self.instance.jours_repos:
#             self.initial['jours_repos'] = self.instance.jours_repos

#     class Meta:
#         model = Personnel
#         fields = ["nom", "prenom", "role", "lieu_travail", "salaire", "jours_repos"]
        
#     def clean(self):
#         cleaned = super().clean()
#         lieu = cleaned.get("lieu_travail")
#         jours = cleaned.get("jours_repos", [])
        
#         if lieu == "boite" and len(jours) < 2:
#             self.add_error('jours_repos', "Pour la Boîte, veuillez choisir au moins 2 jours de repos.")
#         if lieu == "terrasse" and len(jours) < 1:
#             self.add_error('jours_repos', "Pour la Terrasse, veuillez choisir au moins 1 jour de repos.")
        
#         cleaned['jours_repos'] = jours
#         return cleaned


from django import forms
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Personnel, JOUR_CHOICES # Assurez-vous que JOUR_CHOICES est bien importé

User = get_user_model()

# ----------------------------------------------
# 1. Formulaire de CRÉATION (Employés réguliers)
# ----------------------------------------------
class PersonnelCreationForm(forms.ModelForm):
    # 'username' est RETIRÉ d'ici car il sera généré automatiquement
    email = forms.EmailField(label="Adresse E-mail", help_text="Nécessaire pour l'activation et la réinitialisation de mot de passe.")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe Initial", help_text="Sera écrasé par le premier changement de l'employé.")
    
    # Champ du profil Personnel
    jours_repos = forms.MultipleChoiceField(
        choices=JOUR_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Jours de repos"
    )

    class Meta:
        model = Personnel
        # RETRAIT de 'username' des fields
        fields = ["id", "nom", "prenom", "role", "lieu_travail", "salaire", "jours_repos", 'email', 'password']
        
    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        lieu = cleaned.get("lieu_travail")
        jours = cleaned.get("jours_repos", [])
        
        # Vérification de l'unicité de l'e-mail (IMPORTANT pour le flow d'activation)
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "Cette adresse e-mail est déjà utilisée par un autre employé. L'e-mail doit être unique.")
            
        if lieu == "boite" and len(jours) < 2:
            self.add_error('jours_repos', "Pour la Boîte, veuillez choisir au moins 2 jours de repos.")
        if lieu == "terrasse" and len(jours) < 1:
            self.add_error('jours_repos', "Pour la Terrasse, veuillez choisir au moins 1 jour de repos.")
        
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        
        # 1. Crée l'objet Personnel en mémoire SANS le sauvegarder dans la DB.
        personnel = super().save(commit=False)
        
        # 2. Sauvegarde l'objet Personnel une première fois SANS l'User
        # Ceci est nécessaire pour obtenir un PK/ID à utiliser comme username
        # ATTENTION: Il faut rendre 'user' nullable temporairement si c'est la première insertion
        # OU, si 'id' est un champ personnalisé non auto-incrémenté, on peut faire autrement:
        
        # --- SOLUTION EFFICACE : Créer l'User avec un username temporaire, puis lier ---
        
        # 2a. Crée l'objet User avec un username temporaire (pour éviter les erreurs de NOT NULL sur le User Model)
        user = User.objects.create_user(
            username="temp_user", 
            email=self.cleaned_data['email'], 
            password=self.cleaned_data['password'],
            is_staff=True
        )

        # 2b. LIAISON : Affecte l'objet User à l'objet Personnel en mémoire
        personnel.user = user

        # 3. Sauvegarde finale de l'objet Personnel dans la DB. 
        # C'est ici que le champ user_id est renseigné correctement.
        if commit:
            personnel.save() 
            
            # 4. MISE À JOUR : Le Personnel a maintenant son PK/ID. Nous l'utilisons pour corriger l'User.
            auto_username = str(personnel.pk) # Récupère l'ID réel après insertion
            
            # 5. Mise à jour de l'User avec le bon username
            user.username = auto_username
            user.save() 
            
        return personnel

# ----------------------------------------------
# 2. Formulaire de MODIFICATION
# ----------------------------------------------
class PersonnelEditForm(forms.ModelForm):
# ... (votre code reste inchangé)
    jours_repos = forms.MultipleChoiceField(
        choices=JOUR_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Jours de repos"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.jours_repos:
            self.initial['jours_repos'] = self.instance.jours_repos

    class Meta:
        model = Personnel
        fields = ["nom", "prenom", "role", "lieu_travail", "salaire", "jours_repos"]
        
    def clean(self):
        cleaned = super().clean()
        lieu = cleaned.get("lieu_travail")
        jours = cleaned.get("jours_repos", [])
        
        if lieu == "boite" and len(jours) < 2:
            self.add_error('jours_repos', "Pour la Boîte, veuillez choisir au moins 2 jours de repos.")
        if lieu == "terrasse" and len(jours) < 1:
            self.add_error('jours_repos', "Pour la Terrasse, veuillez choisir au moins 1 jour de repos.")
        
        cleaned['jours_repos'] = jours
        return cleaned