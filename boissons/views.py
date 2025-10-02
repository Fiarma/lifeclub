from django.shortcuts import render

# Create your views here.
# Import pour rendre des templates et gérer les redirections
from django.shortcuts import render, get_object_or_404, redirect
# Import du décorateur pour exiger une connexion utilisateur
#from django.contrib.auth.decorators import login_required
# Import pour afficher des messages flash (success / error)
from django.contrib import messages
# Import des modèles utilisés par les vues
from .models import Boisson, HistoriqueStock
# Import des formulaires utilisés par les vues
from .forms import BoissonForm, HistoriqueStockForm

# Vue pour lister toutes les boissons (affichage principal)
#@login_required
# def liste_boissons(request):
#     # Récupération de toutes les boissons triées par nom
#     boissons = Boisson.objects.all().order_by("nom")
#     # Rendu du template 'liste_boissons.html' avec le contexte
#     return render(request, "boissons/liste_boissons.html", {"boissons": boissons})


# Vue pour lister toutes les boissons (affichage principal)
#@login_required
def liste_boissons(request):
    # Récupération de toutes les boissons triées par lieu puis nom
    boissons = Boisson.objects.all().order_by("lieu", "nom")
    
    # Séparation par lieu pour l'affichage
    boissons_boite = boissons.filter(lieu='boite')
    boissons_terrasse = boissons.filter(lieu='terrasse')
    
    # Rendu du template 'liste_boissons.html' avec le contexte
    return render(request, "boissons/liste_boissons.html", {
        "boissons": boissons,
        "boissons_boite": boissons_boite,
        "boissons_terrasse": boissons_terrasse
    })

# Vue pour ajouter une nouvelle boisson (accessible aux utilisateurs connectés)
#@login_required
# def add_boisson(request):
#     # Si la méthode HTTP est POST : traitement du formulaire
#     if request.method == "POST":
#         # Instanciation du formulaire avec les données envoyées
#         form = BoissonForm(request.POST)
#         # Validation du formulaire
#         if form.is_valid():
#             # Sauvegarde de la nouvelle boisson en base
#             form.save()
#             # Message de succès pour l'utilisateur
#             messages.success(request, "Nouvelle boisson ajoutée avec succès.")
#             # Redirection vers la liste des boissons
#             return redirect("boissons:liste_boissons")
#     else:
#         # Si méthode GET : on crée un formulaire vide pour affichage
#         form = BoissonForm()
#     # Rendu du template d'ajout avec le formulaire
#     return render(request, "boissons/add_boisson.html", {"form": form})


# Vue pour ajouter une nouvelle boisson (accessible aux utilisateurs connectés)
#@login_required
def add_boisson(request):
    # Si la méthode HTTP est POST : traitement du formulaire
    if request.method == "POST":
        # Instanciation du formulaire avec les données envoyées
        form = BoissonForm(request.POST)
        # Validation du formulaire
        if form.is_valid():
            # Sauvegarde de la nouvelle boisson en base
            boisson = form.save()
            # Message de succès pour l'utilisateur
            messages.success(request, f"Nouvelle boisson '{boisson.nom}' ajoutée avec succès au stock {boisson.get_lieu_display()}.")
            # Redirection vers la liste des boissons
            return redirect("boissons:liste_boissons")
    else:
        # Si méthode GET : on crée un formulaire vide pour affichage
        form = BoissonForm()
    # Rendu du template d'ajout avec le formulaire
    return render(request, "boissons/add_boisson.html", {"form": form})


from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def edit_boisson(request, boisson_id):
    boisson = get_object_or_404(Boisson, id=boisson_id)
    
    if request.method == "POST":
        form = BoissonForm(request.POST, instance=boisson)
        if form.is_valid():
            form.save()
            messages.success(request, f"La boisson '{boisson.nom}' a été modifiée avec succès.")
            return redirect("boissons:liste_boissons")
    else:
        form = BoissonForm(instance=boisson)
    
    return render(request, "boissons/edit_boisson.html", {"form": form, "boisson": boisson})

# Vue pour supprimer une boisson (confirmation puis suppression)
#@login_required
def delete_boisson(request, boisson_id):
    # Récupération de la boisson ou 404
    boisson = get_object_or_404(Boisson, id=boisson_id)
    # Si POST : confirmation reçue, on supprime
    if request.method == "POST":
        # Suppression de la boisson (cascade supprime les historiques liés)
        boisson.delete()
        # Message de succès
        messages.success(request, "Boisson supprimée avec succès.")
        # Redirection vers liste
        return redirect("boissons:liste_boissons")
    # Si GET : on affiche la page de confirmation
    return render(request, "boissons/delete_boisson.html", {"boisson": boisson})

# Vue pour la mise à jour du stock (formulaire du caissier)
#@login_required
def maj_stock(request, boisson_id):
    # Récupération de la boisson ciblée
    boisson = get_object_or_404(Boisson, id=boisson_id)
    # Si POST : on traite le formulaire
    if request.method == "POST":
        # Instanciation du formulaire en passant la boisson pour validation
        form = HistoriqueStockForm(request.POST, boisson=boisson)
        # Validation du formulaire
        if form.is_valid():
            # Création de l'instance HistoriqueStock sans la sauvegarder immédiatement
            historique = form.save(commit=False)
            # Association explicite au modèle Boisson
            historique.boisson = boisson
            # Enregistrement de l'utilisateur (caissier) qui a effectué la saisie
            historique.caissier = request.user
            # Sauvegarde (logic de save() du modèle mettra à jour Boisson.stock_actuel)
            historique.save()
            # Message de succès
            messages.success(request, "Mise à jour du stock enregistrée avec succès.")
            # Redirection vers la liste des boissons
            return redirect("boissons:liste_boissons")
        else:
            # Si invalid : message d'erreur (les détails s'affichent dans le template)
            messages.error(request, "Erreur : vérifiez le formulaire.")
    else:
        # Si GET : on construit le formulaire avec la boisson pour préremplissage
        form = HistoriqueStockForm(boisson=boisson)
    # Rendu du template de mise à jour avec le formulaire et la boisson
    return render(request, "boissons/maj_stock.html", {"form": form, "boisson": boisson})



from django.shortcuts import render, get_object_or_404
from .models import Boisson, HistoriqueStock
from .forms import HistoriqueStockFilterForm





def historique_stock(request, boisson_id):
    # Récupérer la boisson
    boisson = get_object_or_404(Boisson, pk=boisson_id)

    # Instancier le formulaire avec GET
    form = HistoriqueStockFilterForm(request.GET or None)

    # Récupérer l'historique complet
    historiques = boisson.historiques.all()

    # Si le formulaire est valide, filtrer
    if form.is_valid():
        search_type = form.cleaned_data.get("search_type")
        date_val = form.cleaned_data.get("date")
        month_val = form.cleaned_data.get("month")

        if search_type == "date" and date_val:
            historiques = historiques.filter(date__date=date_val)
        elif search_type == "month" and month_val:
            historiques = historiques.filter(
                date__year=month_val.year,
                date__month=month_val.month
            )

    # Retour du template
    return render(request, "boissons/historique_stock.html", {
        "boisson": boisson,
        "historiques": historiques,
        "form": form
    })
