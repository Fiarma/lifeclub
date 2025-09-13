from django.contrib import admin

# Register your models here.
# Import du module forms de Django pour créer un ModelForm personnalisé pour l'admin
from django import forms
# Import du module admin de Django pour enregistrer le modèle dans l'interface d'administration
from django.contrib import admin
# Import du modèle Personnel et de la constante JOUR_CHOICES depuis le même module models
from .models import Personnel, JOUR_CHOICES

# Définition d'un ModelForm personnalisé pour l'admin afin d'afficher jours_repos en multi-choix (checkboxes)
class PersonnelAdminForm(forms.ModelForm):
    # Déclaration d'un champ MultipleChoiceField pour jours_repos avec rendu en CheckboxSelectMultiple
    jours_repos = forms.MultipleChoiceField(
        choices=JOUR_CHOICES,                         # choix des jours (lundi..dimanche)
        widget=forms.CheckboxSelectMultiple,         # widget case à cocher multiple pour meilleure ergonomie
        required=False,                              # champ facultatif
        label="Jours de repos"                       # libellé affiché dans l'admin
    )

    # Spécification du modèle source et des champs à inclure dans ce ModelForm
    class Meta:
        model = Personnel
        fields = "__all__"

    # Initialisation du formulaire : si l'instance a déjà des jours_repos, on les préremplit
    def __init__(self, *args, **kwargs):
        # Appel de l'initialisation parent pour construire les champs
        super().__init__(*args, **kwargs)
        # Si l'instance existe et contient des jours_repos, on les positionne comme valeur initiale du champ
        if getattr(self, "instance", None) and getattr(self.instance, "jours_repos", None):
            # Assure que l'initial est une liste
            self.fields["jours_repos"].initial = list(self.instance.jours_repos)

    # Nettoyage/normalisation du champ jours_repos avant sauvegarde : s'assurer d'avoir une liste (JSONField)
    def clean_jours_repos(self):
        # Récupération des valeurs sélectionnées (liste ou None)
        data = self.cleaned_data.get("jours_repos", [])
        # Retourne toujours une liste (JSONField attend une liste)
        return list(data)


# Enregistrement et configuration du modèle Personnel dans l'admin
@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    # Utilisation du ModelForm personnalisé défini ci-dessus
    form = PersonnelAdminForm

    # Colonnes à afficher dans la liste d'objets de l'administration
    list_display = (
        "id",
        "nom",
        "prenom",
        "role",
        "lieu_travail",
        "jours_repos_display",  # méthode affichant joliment les jours de repos
        "salaire",
        "jours_travail",
    )

    # Filtres dans la barre latérale pour faciliter la recherche
    list_filter = ("role", "lieu_travail")

    # Champs sur lesquels effectuer des recherches textuelles
    search_fields = ("id", "nom", "prenom")

    # Ordre par défaut des enregistrements dans l'admin
    ordering = ("nom", "prenom")

    # Champs en lecture seule (par ex. jours_travail calculé)
    readonly_fields = ("jours_travail",)

    # Définition d'une méthode utilitaire pour afficher les jours_repos sous forme lisible
    def jours_repos_display(self, obj):
        # Si l'objet n'a pas de jours_repos, afficher un tiret
        if not obj.jours_repos:
            return "-"
        # Joindre la liste par des virgules pour affichage propre
        return ", ".join(obj.jours_repos)

    # Définir le titre de colonne pour la méthode jours_repos_display
    jours_repos_display.short_description = "Jours de repos"
