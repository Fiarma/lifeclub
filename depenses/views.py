from django.shortcuts import render

# Create your views here.
# Import Django
from django.shortcuts import render, redirect, get_object_or_404
from .models import Depense
from .forms import DepenseForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from ventes.decorators import session_required # NOUVEAU

# # Liste des dépenses avec possibilité de recherche par date ou par mois
# def liste_depenses(request):
#     # On récupère tous les enregistrements
#     depenses = Depense.objects.all()

#     # Gestion du filtre recherche
#     search_type = request.GET.get("search_type")  # 'date' ou 'mois'
#     search_value = request.GET.get("search_value")  # valeur saisie

#     if search_type and search_value:
#         if search_type == "date":
#             depenses = depenses.filter(date=search_value)
#         elif search_type == "mois":
#             # recherche par mois au format YYYY-MM
#             year, month = map(int, search_value.split("-"))
#             depenses = depenses.filter(date__year=year, date__month=month)

#     # Tri par date décroissante
#     depenses = depenses.order_by("-date")

#     return render(request, "depenses/liste_depenses.html", {
#         "depenses": depenses,
#         "search_type": search_type,
#         "search_value": search_value
#     })


# views.py dans app depenses
from django.shortcuts import render
from .models import Depense
from .forms import DepenseFilterForm
# views.py dans app depenses
from django.shortcuts import render
from .models import Depense
from .forms import DepenseFilterForm

def liste_depenses(request):
    """
    Affiche la liste des dépenses avec possibilité de filtrage par date, mois ou personnel.
    """
    # Instancier le formulaire avec GET
    form = DepenseFilterForm(request.GET or None)

    # Récupérer toutes les dépenses
    depenses = Depense.objects.all().order_by('-date')  # tri décroissant par date

    # Si le formulaire est valide, filtrer les dépenses
    if form.is_valid():
        search_type = form.cleaned_data.get("search_type")
        date_val = form.cleaned_data.get("date")
        month_val = form.cleaned_data.get("month")
        personnel_val = form.cleaned_data.get("personnel")

        # Filtre par date précise
        if search_type == "date" and date_val:
            depenses = depenses.filter(date=date_val)
        # Filtre par mois
        elif search_type == "month" and month_val:
            depenses = depenses.filter(
                date__year=month_val.year,
                date__month=month_val.month
            )
        # Filtre par personnel
        if personnel_val:
            depenses = depenses.filter(personnel=personnel_val)

    # Retourner le template avec le formulaire et les dépenses
    return render(request, "depenses/liste_depenses.html", {
        "depenses": depenses,
        "form": form
    })


# Ajouter une dépense
@login_required
@session_required # <--- APPLICATION DU CONTRÔLE DE SESSION
def add_depense(request):
    if request.method == "POST":
        form = DepenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("depenses:liste_depenses")
    else:
        form = DepenseForm()
    return render(request, "depenses/add_depense.html", {"form": form})

# Éditer une dépense existante
@login_required
@session_required # <--- APPLICATION DU CONTRÔLE DE SESSION
def edit_depense(request, depense_id):
    depense = get_object_or_404(Depense, id=depense_id)
    if request.method == "POST":
        form = DepenseForm(request.POST, instance=depense)
        if form.is_valid():
            form.save()
            return redirect("depenses:liste_depenses")
    else:
        form = DepenseForm(instance=depense)
    return render(request, "depenses/edit_depense.html", {"form": form})

# Supprimer une dépense
@login_required
@session_required # <--- APPLICATION DU CONTRÔLE DE SESSION
def delete_depense(request, depense_id):
    depense = get_object_or_404(Depense, id=depense_id)
    if request.method == "POST":
        depense.delete()
        return redirect("depenses:liste_depenses")
    return render(request, "depenses/delete_depense.html", {"depense": depense})
