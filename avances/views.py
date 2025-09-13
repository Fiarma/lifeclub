# Import des utilitaires de rendu et redirection
from django.shortcuts import render, redirect, get_object_or_404
# Import du modèle Avance pour les opérations sur la BD
from .models import Avance
# Import du formulaire AvanceForm pour créer / éditer des avances
from .forms import AvanceForm

# # Vue listant toutes les avances (triées par date décroissante)
# def avance_list(request):
#     # Récupération des avances avec jointure sur personnel pour optimiser les requêtes
#     avances = Avance.objects.select_related("personnel").all().order_by("-date_avance")
#     # Rendu du template 'avance_list.html' avec le contexte
#     return render(request, "avances/avance_list.html", {"avances": avances})



# views.py dans app avances
from django.shortcuts import render
from .models import Avance
from .forms import AvanceFilterForm
def liste_avances(request):
    """
    Affiche la liste des avances avec filtrage par date, mois et personnel.
    """
    # Instancier le formulaire avec GET
    form = AvanceFilterForm(request.GET or None)

    # Récupérer toutes les avances
    avances = Avance.objects.all().order_by('-date_avance')  # tri décroissant par date

    # Si le formulaire est valide, appliquer les filtres
    if form.is_valid():
        search_type = form.cleaned_data.get("search_type")
        date_val = form.cleaned_data.get("date")
        month_val = form.cleaned_data.get("month")
        personnel_val = form.cleaned_data.get("personnel")

        # Filtre par date
        if search_type == "date" and date_val:
            avances = avances.filter(date_avance=date_val)

        # Filtre par mois
        elif search_type == "month" and month_val:
            avances = avances.filter(
                date_avance__year=month_val.year,
                date_avance__month=month_val.month
            )

        # Filtre par personnel
        if personnel_val:
            avances = avances.filter(personnel=personnel_val)

    # Renvoyer le template
    return render(request, "avances/liste_avances.html", {
        "avances": avances,
        "form": form
    })


# Vue pour ajouter une nouvelle avance
def add_avance(request):
    # Si la méthode est POST on traite le formulaire envoyé
    if request.method == "POST":
        # Instanciation du formulaire avec les données POST
        form = AvanceForm(request.POST)
        # Validation du formulaire
        if form.is_valid():
            # Sauvegarde de l'objet Avance en base
            form.save()
            # Redirection vers la liste des avances après enregistrement
            return redirect("avances:liste_avances")
    else:
        # Si méthode GET on affiche un formulaire vide
        form = AvanceForm()
    # Rendu du template d'ajout avec le formulaire
    return render(request, "avances/add_avance.html", {"form": form})

# Vue pour éditer une avance existante
def edit_avance(request, pk):
    # Récupération de l'avance ou 404 si inexistante
    avance = get_object_or_404(Avance, pk=pk)
    # Si POST : traitement du formulaire de mise à jour
    if request.method == "POST":
        # Instanciation du formulaire lié à l'instance existante
        form = AvanceForm(request.POST, instance=avance)
        # Validation
        if form.is_valid():
            # Sauvegarde des modifications
            form.save()
            # Redirection vers la liste
            return redirect("avances:liste_avances")
    else:
        # Si GET : préremplissage du formulaire avec l'instance
        form = AvanceForm(instance=avance)
    # Rendu du template d'édition
    return render(request, "avances/edit_avance.html", {"form": form})

# Vue pour supprimer une avance (confirmation puis suppression)
def delete_avance(request, pk):
    # Récupération de l'objet Avance ou 404
    avance = get_object_or_404(Avance, pk=pk)
    # Si POST : suppression confirmée
    if request.method == "POST":
        # Suppression de l'avance
        avance.delete()
        # Redirection vers la liste
        return redirect("avances:liste_avances")
    # Si GET : afficher le template de confirmation
    return render(request, "avances/delete_avance.html", {"avance": avance})
