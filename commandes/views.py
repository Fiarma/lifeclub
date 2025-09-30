

# from django.shortcuts import render
# from .models import Commande

# def liste_commandes(request):
#     # Précharger les items pour éviter des requêtes supplémentaires
#     commandes = Commande.objects.prefetch_related('items', 'items__boisson').all().order_by('-date_commande')
#     return render(request, "commandes/liste_commandes.html", {"commandes": commandes})

	
	


# # commandes/views.py
# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import Commande, CommandeItem
# from personnel.models import Personnel
# from boissons.models import Boisson



# # Imports des modèles et formulaires locaux
# from .models import Commande, CommandeItem
# from .forms import CommandeForm
# from boissons.models import Boisson


# def ajouter_commande(request):
#     boisson_list = Boisson.objects.all()

#     if request.method == "POST":
#         form_commande = CommandeForm(request.POST)
#         boisson_ids = request.POST.getlist("boisson")
#         quantites = request.POST.getlist("quantite")

#         items_data = []
#         for b, q in zip(boisson_ids, quantites):
#             if b and q:
#                 try:
#                     items_data.append((int(b), int(q)))
#                 except ValueError:
#                     continue

#         if form_commande.is_valid() and items_data:
#             commande = form_commande.save()

#             total = 0
#             for boisson_id, quantite in items_data:
#                 boisson = get_object_or_404(Boisson, pk=boisson_id)
#                 item = CommandeItem.objects.create(
#                     commande=commande,
#                     boisson=boisson,
#                     quantite=quantite
#                 )
#                 total += item.montant_boisson  # accumulate montant de chaque item

#             # ⚡ Mise à jour du montant total après avoir créé tous les items
#             commande.montant_total = total
#             commande.save()

#             messages.success(request, "Commande créée avec succès.")
#             return redirect("commandes:liste_commandes")
#         else:
#             messages.error(request, "Veuillez sélectionner le personnel et au moins une boisson avec quantité.")
#     else:
#         form_commande = CommandeForm()

#     return render(request, "commandes/ajouter_commande.html", {
#         "form_commande": form_commande,
#         "boissons": boisson_list
#     })

# from django.views.decorators.http import require_POST


# @csrf_exempt  # ⚠️ garde-le si tu n’as pas configuré le CSRF côté JS
# @require_POST
# def update_item_quantity(request, item_id):
#     """
#     Incrémente ou décrémente la quantité d’un item.
#     Si la quantité tombe à 0, l’item est supprimé.
#     Recalcule aussi le montant total de la commande.
#     """
#     item = get_object_or_404(CommandeItem, pk=item_id)
#     action = request.POST.get("action")

#     if action == "increment":
#         item.quantite += 1
#         item.save()
#     elif action == "decrement":
#         item.quantite -= 1
#         if item.quantite > 0:
#             item.save()
#         else:
#             # Supprimer l’item si quantité = 0
#             item.delete()
#             commande = item.commande
#             total = sum([i.montant_boisson for i in commande.items.all()])
#             return JsonResponse({
#                 "success": True,
#                 "deleted": True,
#                 "item_id": item_id,
#                 "commande_id": commande.id,
#                 "commande_total": float(total),
#             })
#     else:
#         return JsonResponse({"success": False, "error": "Action invalide"})

#     commande = item.commande
#     total = sum([i.montant_boisson for i in commande.items.all()])

#     return JsonResponse({
#         "success": True,
#         "deleted": False,
#         "item_id": item.id,
#         "commande_id": commande.id,
#         "quantite": item.quantite,
#         "item_montant": float(item.montant_boisson),
#         "commande_total": float(total),
#     })



# # Valider commande
# @require_POST
# @csrf_exempt
# def valider_commande(request, commande_id):
#     commande = get_object_or_404(Commande, id=commande_id)
#     type_paiement = request.POST.get("type_paiement")
#     montant_liquidite = float(request.POST.get("montant_liquidite", 0))
#     montant_orange = float(request.POST.get("montant_orange", 0))
#     statut_monnaie = request.POST.get("statut_monnaie")

#     commande.type_paiement = type_paiement
#     commande.montant_liquidite = montant_liquidite if montant_liquidite > 0 else None
#     commande.montant_orange = montant_orange if montant_orange > 0 else None

#     montant_total = float(commande.montant_total)
#     avoir_cree = False
#     message_avoir = ""

#     # Liquidité
#     if type_paiement == "liquidite":
#         if montant_liquidite == montant_total:
#             commande.statut = "payer"
#         elif montant_liquidite > montant_total:
#             monnaie = montant_liquidite - montant_total
#             commande.monnaie_a_rendre = monnaie
#             commande.statut = "payer"

#             if statut_monnaie == "avoir":
#                 avoir, created = Avoir.objects.get_or_create(
#                     commande=commande,
#                     defaults={"montant": monnaie, "statut": "en_attente"}
#                 )
#                 if created:
#                     avoir_cree = True
#                     message_avoir = f"Avoir créé pour la commande {commande.id} : {monnaie} F."
#                 commande.statut_monnaie = "avoir"
#             else:
#                 commande.statut_monnaie = "remis"
#         else:
#             commande.statut = "impayee"

#     elif type_paiement == "orange_money":
#         commande.statut = "payer"

#     elif type_paiement == "hybride":
#         if (montant_liquidite + montant_orange) == montant_total:
#             commande.statut = "payer"
#         else:
#             commande.statut = "impayee"

#     else:
#         commande.statut = "en_attente"

#     commande.save()

#     return JsonResponse({
#         "success": True,
#         "commande_id": commande.id,
#         "statut": commande.get_statut_display(),
#         "monnaie": str(commande.monnaie_a_rendre),
#         "statut_monnaie": commande.statut_monnaie,
#         "avoir_cree": avoir_cree,
#         "message_avoir": message_avoir
#     })


# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Commande, CommandeItem, Avoir

# # Liste des avoirs (en attente et réglés)
# def liste_avoirs(request):
#     """
#     Affiche tous les avoirs liés aux commandes :
#     - En attente
#     - Réglés
#     """
#     avoirs_en_attente = Avoir.objects.filter(statut="en_attente").order_by("-date_creation")
#     avoirs_regles = Avoir.objects.filter(statut="regle").order_by("-date_creation")

#     return render(request, "avoirs/liste_avoirs.html", {
#         "avoirs_en_attente": avoirs_en_attente,
#         "avoirs_regles": avoirs_regles,
#     })


# # Régler un avoir
# def regler_avoir(request, avoir_id):
#     """
#     Change le statut d'un avoir à "regle" :
#     - Supprime de la liste en attente
#     - Ajoute automatiquement à la liste des avoirs réglés
#     """
#     avoir = get_object_or_404(Avoir, pk=avoir_id)
#     if avoir.statut != "regle":
#         avoir.statut = "regle"
#         avoir.save()
#         messages.success(request, f"L’avoir {avoir.id} de {avoir.montant} F a été réglé.")
#     else:
#         messages.info(request, f"L’avoir {avoir.id} est déjà réglé.")

#     return redirect("commandes:liste_avoirs")


#############################################################

# commandes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import Commande, CommandeItem, Avoir
from .forms import CommandeForm
from boissons.models import Boisson
from personnel.models import Personnel


# -----------------------------
# Vue : liste des commandes
# -----------------------------
def liste_commandes(request):
    commandes = Commande.objects.prefetch_related('items', 'items__boisson').all().order_by('-date_commande')
    boisson_list = Boisson.objects.all()

    return render(request, "commandes/liste_commandes.html", {"commandes": commandes, 'boissons':boisson_list})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Commande, CommandeItem, Boisson

# ---------------------------
# Ajouter une boisson à une commande
# ---------------------------
@require_POST
@csrf_exempt
def ajouter_boisson(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    boisson_id = request.POST.get("boisson_id")
    quantite = int(request.POST.get("quantite", 1))

    if not boisson_id:
        return JsonResponse({"success": False, "message": "Veuillez choisir une boisson."})

    boisson = get_object_or_404(Boisson, id=boisson_id)

    # Création de l'item dans la commande
    item = CommandeItem.objects.create(
        commande=commande,
        boisson=boisson,
        quantite=quantite
    )

    # Recalcul du montant total de la commande
    total = sum([i.quantite * i.boisson.prix_unitaire for i in commande.items.all()])
    commande.montant_total = total
    commande.save()

    return JsonResponse({"success": True, "commande_total": total})


# ---------------------------
# Supprimer un item d'une commande
# ---------------------------
@require_POST
@csrf_exempt
def supprimer_item(request, item_id):
    item = get_object_or_404(CommandeItem, id=item_id)
    commande = item.commande
    item.delete()

    # Recalcul du montant total
    total = sum([i.quantite * i.boisson.prix_unitaire for i in commande.items.all()])
    commande.montant_total = total
    commande.save()

    return JsonResponse({"success": True, "item_id": item_id, "commande_id": commande.id, "commande_total": total, "deleted": True})


# ---------------------------
# Supprimer une commande
# ---------------------------
@require_POST
@csrf_exempt
def supprimer_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    commande.delete()
    return JsonResponse({"success": True, "commande_id": commande_id})


# # -----------------------------
# # Vue : ajouter une commande
# # -----------------------------
# def ajouter_commande(request):
#     boisson_list = Boisson.objects.all()

#     if request.method == "POST":
#         form_commande = CommandeForm(request.POST)
#         boisson_ids = request.POST.getlist("boisson")
#         quantites = request.POST.getlist("quantite")

#         items_data = []
#         for b, q in zip(boisson_ids, quantites):
#             if b and q:
#                 try:
#                     items_data.append((int(b), int(q)))
#                 except ValueError:
#                     continue

#         if form_commande.is_valid() and items_data:
#             commande = form_commande.save()
#             for boisson_id, quantite in items_data:
#                 boisson = get_object_or_404(Boisson, pk=boisson_id)
#                 CommandeItem.objects.create(commande=commande, boisson=boisson, quantite=quantite)

#             messages.success(request, "Commande créée avec succès.")
#             return redirect("commandes:liste_commandes")
#         else:
#             messages.error(request, "Veuillez sélectionner le personnel et au moins une boisson avec quantité.")
#     else:
#         form_commande = CommandeForm()

#     return render(request, "commandes/ajouter_commande.html", {
#         "form_commande": form_commande,
#         "boissons": boisson_list
#     })



def ajouter_commande(request):
    boisson_list = Boisson.objects.all()

    if request.method == "POST":
        form_commande = CommandeForm(request.POST)
        boisson_ids = request.POST.getlist("boisson")
        quantites = request.POST.getlist("quantite")

        items_data = []
        for b, q in zip(boisson_ids, quantites):
            if b and q:
                try:
                    items_data.append((int(b), int(q)))
                except ValueError:
                    continue

        if form_commande.is_valid() and items_data:
            commande = form_commande.save()

            total = 0
            for boisson_id, quantite in items_data:
                boisson = get_object_or_404(Boisson, pk=boisson_id)
                item = CommandeItem.objects.create(
                    commande=commande,
                    boisson=boisson,
                    quantite=quantite
                )
                total += item.montant_boisson  # accumulate montant de chaque item

            # ⚡ Mise à jour du montant total après avoir créé tous les items
            commande.montant_total = total
            commande.save()

            messages.success(request, "Commande créée avec succès.")
            return redirect("commandes:liste_commandes")
        else:
            messages.error(request, "Veuillez sélectionner le personnel et au moins une boisson avec quantité.")
    else:
        form_commande = CommandeForm()

    return render(request, "commandes/ajouter_commande.html", {
        "form_commande": form_commande,
        "boissons": boisson_list
    })


# -----------------------------
# Vue : update quantité item
# -----------------------------
@csrf_exempt
@require_POST
def update_item_quantity(request, item_id):
    item = get_object_or_404(CommandeItem, pk=item_id)
    action = request.POST.get("action")

    if action == "increment":
        item.quantite += 1
        item.save()
    elif action == "decrement":
        item.quantite -= 1
        if item.quantite > 0:
            item.save()
        else:
            commande = item.commande
            item.delete()
            total = sum([i.montant_boisson for i in commande.items.all()])
            return JsonResponse({
                "success": True,
                "deleted": True,
                "item_id": item_id,
                "commande_id": commande.id,
                "commande_total": float(total),
            })
    else:
        return JsonResponse({"success": False, "error": "Action invalide"})

    commande = item.commande
    total = sum([i.montant_boisson for i in commande.items.all()])

    return JsonResponse({
        "success": True,
        "deleted": False,
        "item_id": item.id,
        "commande_id": commande.id,
        "quantite": item.quantite,
        "item_montant": float(item.montant_boisson),
        "commande_total": float(total),
    })


# -----------------------------
# Vue : valider commande
# -----------------------------
# @require_POST
# @csrf_exempt
# def valider_commande(request, commande_id):
#     commande = get_object_or_404(Commande, id=commande_id)
#     type_paiement = request.POST.get("type_paiement")
#     montant_liquidite = float(request.POST.get("montant_liquidite", 0))
#     montant_orange = float(request.POST.get("montant_orange", 0))
#     statut_monnaie = request.POST.get("statut_monnaie")  # ✅ corrigé

#     commande.type_paiement = type_paiement
#     commande.montant_liquidite = montant_liquidite if montant_liquidite > 0 else None
#     commande.montant_orange = montant_orange if montant_orange > 0 else None

#     montant_total = float(commande.montant_total)
#     avoir_cree = False
#     message_avoir = ""

#     # Liquidité
#     if type_paiement == "liquidite":
#         if montant_liquidite == montant_total:
#             commande.statut = "payer"
#         elif montant_liquidite > montant_total:
#             monnaie = montant_liquidite - montant_total
#             commande.monnaie_a_rendre = monnaie
#             commande.statut = "payer"

#             if statut_monnaie == "avoir":
#                 avoir = Avoir.objects.create(
#                     commande=commande,
#                     montant=monnaie,
#                     statut="en_attente"
#                 )
#                 avoir_cree = True
#                 message_avoir = f"Avoir #{avoir.id} de {monnaie} F créé avec succès."
#                 commande.statut_monnaie = "avoir"
#             else:
#                 commande.statut_monnaie = "remis"
#         else:
#             commande.statut = "impayee"

#     elif type_paiement == "orange_money":
#         commande.statut = "payer"

#     elif type_paiement == "hybride":
#         if (montant_liquidite + montant_orange) == montant_total:
#             commande.statut = "payer"
#         else:
#             commande.statut = "impayee"

#     else:
#         commande.statut = "en_attente"

#     commande.save()

#     return JsonResponse({
#         "success": True,
#         "commande_id": commande.id,
#         "statut": commande.get_statut_display(),
#         "monnaie": str(commande.monnaie_a_rendre),
#         "statut_monnaie": commande.statut_monnaie,
#         "avoir_cree": avoir_cree,
#         "message_avoir": message_avoir
#     })


# -----------------------------
# Vue : valider commande
# -----------------------------
# @require_POST
# @csrf_exempt
# def valider_commande(request, commande_id):
#     commande = get_object_or_404(Commande, id=commande_id)
#     type_paiement = request.POST.get("type_paiement")
#     montant_liquidite = float(request.POST.get("montant_liquidite", 0))
#     montant_orange = float(request.POST.get("montant_orange", 0))
#     statut_monnaie = request.POST.get("statut_monnaie")  # "avoir" ou "remis"

#     # Reset monnaie avant calcul
#     commande.monnaie_a_rendre = 0
#     commande.statut_monnaie = None  

#     commande.type_paiement = type_paiement
#     commande.montant_liquidite = montant_liquidite if montant_liquidite > 0 else None
#     commande.montant_orange = montant_orange if montant_orange > 0 else None

#     montant_total = float(commande.montant_total)
#     avoir_cree = False
#     message_avoir = ""

#     # Paiement par liquidité
#     if type_paiement == "liquidite":
#         if montant_liquidite == montant_total:
#             commande.statut = "payer"

#         elif montant_liquidite > montant_total:
#             monnaie = montant_liquidite - montant_total
#             commande.monnaie_a_rendre = monnaie
#             commande.statut = "payer"

#             if statut_monnaie == "avoir":
#                 # ✅ Ici on enregistre bien SEULEMENT la monnaie en avoir
#                 avoir = Avoir.objects.create(
#                     commande=commande,
#                     montant=monnaie,
#                     statut="en_attente"
#                 )
#                 avoir_cree = True
#                 message_avoir = f"Avoir #{avoir.id} de {monnaie} F créé avec succès."
#                 commande.statut_monnaie = "avoir"
#             else:
#                 commande.statut_monnaie = "remis"

#         else:
#             commande.statut = "impayee"

#     # Paiement par Orange Money
#     elif type_paiement == "orange_money":
#         if montant_orange == montant_total:
#             commande.statut = "payer"
#         else:
#             commande.statut = "impayee"

#     # Paiement hybride
#     elif type_paiement == "hybride":
#         if (montant_liquidite + montant_orange) == montant_total:
#             commande.statut = "payer"
#         elif (montant_liquidite + montant_orange) > montant_total:
#             monnaie = (montant_liquidite + montant_orange) - montant_total
#             commande.monnaie_a_rendre = monnaie
#             commande.statut = "payer"

#             if statut_monnaie == "avoir":
#                 avoir = Avoir.objects.create(
#                     commande=commande,
#                     montant=monnaie,
#                     statut="en_attente"
#                 )
#                 avoir_cree = True
#                 message_avoir = f"Avoir #{avoir.id} de {monnaie} F créé avec succès."
#                 commande.statut_monnaie = "avoir"
#             else:
#                 commande.statut_monnaie = "remis"
#         else:
#             commande.statut = "impayee"

#     else:
#         commande.statut = "en_attente"

#     commande.save()

#     return JsonResponse({
#         "success": True,
#         "commande_id": commande.id,
#         "statut": commande.get_statut_display(),
#         "monnaie": str(commande.monnaie_a_rendre),
#         "statut_monnaie": commande.statut_monnaie,
#         "avoir_cree": avoir_cree,
#         "message_avoir": message_avoir
#     })

 # elif type_paiement == "hybride":
    #     total_paye = montant_liquidite + montant_orange  # somme des 2 modes

    #     # Si la somme couvre au moins le montant total
    #     if total_paye >= montant_total:
    #         commande.statut = "payer"
    #         commande.montant_restant = 0
    #         commande.monnaie_a_rendre = total_paye - montant_total  # peut être 0 ou positif

    #         # Si trop payé → possibilité de monnaie
    #         if commande.monnaie_a_rendre > 0:
    #             if statut_monnaie == "avoir":
    #                 avoir = Avoir.objects.create(
    #                     commande=commande,
    #                     montant=commande.monnaie_a_rendre,
    #                     statut="en_attente"
    #                 )
    #                 avoir_cree = True
    #                 message_avoir = f"Avoir #{avoir.id} de {commande.monnaie_a_rendre} F créé avec succès."
    #                 commande.statut_monnaie = "avoir"
    #                 commande.monnaie_a_rendre = 0
    #             else:
    #                 commande.statut_monnaie = "remis"
    #         else:
    #             commande.statut_monnaie = "non_applicable"

    #     # Si le total payé est insuffisant
    #     else:
    #         commande.statut = "impayee"
    #         commande.montant_restant = montant_total - total_paye
    #         commande.monnaie_a_rendre = 0
    #         commande.statut_monnaie = "non_applicable"
    #         message_erreur = f"Commande impayée : il manque {commande.montant_restant} F."

    # -----------------------------
    # Cas par défaut (sécurité)
    # -----------------------------

# -----------------------------
# Vue : liste des avoirs
# -----------------------------
def liste_avoirs(request):
    avoirs_en_attente = Avoir.objects.filter(statut="en_attente").order_by("-date_creation")
    avoirs_regles = Avoir.objects.filter(statut="regle").order_by("-date_creation")

    return render(request, "avoirs/liste_avoirs.html", {
        "avoirs_en_attente": avoirs_en_attente,
        "avoirs_regles": avoirs_regles,
    })


# -----------------------------
# Vue : régler un avoir
# -----------------------------
def regler_avoir(request, avoir_id):
    avoir = get_object_or_404(Avoir, pk=avoir_id)
    if avoir.statut != "regle":
        avoir.statut = "regle"
        avoir.save()
        messages.success(request, f"L’avoir {avoir.id} de {avoir.montant} F a été réglé.")
    else:
        messages.info(request, f"L’avoir {avoir.id} est déjà réglé.")

    return redirect("commandes:liste_avoirs")


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Commande, Avoir

# -----------------------------
# Vue : valider commande
# -----------------------------
# @require_POST
# @csrf_exempt
# def valider_commande(request, commande_id):
#     # Récupère la commande via son ID
#     commande = get_object_or_404(Commande, id=commande_id)

#     # Récupère les données envoyées depuis le formulaire
#     type_paiement = request.POST.get("type_paiement")  # liquidité, orange_money ou hybride
#     montant_liquidite = float(request.POST.get("montant_liquidite", 0))  # montant liquide saisi
#     montant_orange = float(request.POST.get("montant_orange", 0))  # montant Orange Money saisi
#     statut_monnaie = request.POST.get("statut_monnaie")  # remis ou avoir

#     # Mise à jour du type de paiement dans la commande
#     commande.type_paiement = type_paiement
#     commande.montant_liquidite = montant_liquidite if montant_liquidite > 0 else None
#     commande.montant_orange = montant_orange if montant_orange > 0 else None

#     # Récupère le montant total de la commande
#     montant_total = float(commande.montant_total)

#     # Variables pour le retour JSON
#     avoir_cree = False
#     message_avoir = ""
#     message_erreur = ""

#     # -----------------------------
#     # Cas 1 : Paiement en liquidité
#     # -----------------------------
#     if type_paiement == "liquidite":
#         # Si le client paie exactement le montant
#         if montant_liquidite == montant_total:
#             commande.statut = "payer"  # ✅ commande réglée
#             commande.monnaie_a_rendre = 0
#             commande.montant_restant = 0
#             commande.statut_monnaie = "non_applicable"

#         # Si le client paie moins que le montant total
#         elif montant_liquidite < montant_total:
#             commande.statut = "impayee"  # ❌ commande impayée
#             commande.montant_restant = montant_total - montant_liquidite  # calcule ce qu’il reste à payer
#             commande.monnaie_a_rendre = 0
#             commande.statut_monnaie = "non_applicable"
#             message_erreur = f"Commande impayée : il manque {commande.montant_restant} F."

#         # Si le client paie plus que le montant total
#         else:
#             monnaie = montant_liquidite - montant_total  # calcule la monnaie à rendre
#             commande.statut = "payer"
#             commande.monnaie_a_rendre = monnaie
#             commande.montant_restant = 0

#             # Si la monnaie est laissée en avoir
#             if statut_monnaie == "avoir":
#                 avoir = Avoir.objects.create(
#                     commande=commande,
#                     montant=monnaie,
#                     statut="en_attente"
#                 )
#                 avoir_cree = True
#                 message_avoir = f"Avoir #{avoir.id} de {monnaie} F créé avec succès."
#                 commande.statut_monnaie = "avoir"
#                 commande.monnaie_a_rendre = 0  # car transformé en avoir

#             else:
#                 commande.statut_monnaie = "remis"  # monnaie rendue

#     # -----------------------------
#     # Cas 2 : Paiement par Orange Money
#     # -----------------------------
#     elif type_paiement == "orange_money":
#         # Le caissier confirme qu’il a reçu le montant exact
#         commande.montant_orange = montant_total
#         commande.statut = "payer"
#         commande.monnaie_a_rendre = 0
#         commande.montant_restant = 0
#         commande.statut_monnaie = "non_applicable"

#     # -----------------------------
#     # Cas 3 : Paiement hybride (cash + OM)
#     # -----------------------------

#         # -----------------------------
#     # Cas 3 : Paiement hybride (cash + OM)
#     # -----------------------------
#     elif type_paiement == "hybride":
#         total_paye = montant_liquidite + montant_orange  # somme des 2 modes

#         # Si la somme couvre au moins le montant total
#         if total_paye >= montant_total:
#             commande.statut = "payer"
#             commande.montant_restant = 0

#             # ✅ Même si le client donne plus, on considère qu'il a ajouté les frais de retrait
#             # Donc pas de monnaie à rendre et pas d'avoir
#             commande.monnaie_a_rendre = 0
#             commande.statut_monnaie = "non_applicable"

#             # On enregistre exactement le montant de la commande
#             commande.montant_liquidite = montant_liquidite
#             commande.montant_orange = montant_total - montant_liquidite

#         # Si le total payé est insuffisant
#         else:
#             commande.statut = "impayee"
#             commande.montant_restant = montant_total - total_paye
#             commande.monnaie_a_rendre = 0
#             commande.statut_monnaie = "non_applicable"
#             message_erreur = f"Commande impayée : il manque {commande.montant_restant} F."

   
#     else:
#         commande.statut = "en_attente"
#         commande.monnaie_a_rendre = 0
#         commande.montant_restant = 0
#         commande.statut_monnaie = "non_applicable"

#     # Sauvegarde des modifications
#     commande.save()

#     # Réponse JSON envoyée au frontend
#     return JsonResponse({
#         "success": True if commande.statut == "payer" else False,
#         "commande_id": commande.id,
#         "statut": commande.get_statut_display(),
#         "monnaie": str(commande.monnaie_a_rendre),
#         "statut_monnaie": commande.statut_monnaie,
#         "avoir_cree": avoir_cree,
#         "message_avoir": message_avoir,
#         "message_erreur": message_erreur,
#         "montant_restant": str(commande.montant_restant)
#     })


from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Commande, Avoir

# @require_POST
# @csrf_exempt
# def valider_commande(request, commande_id):
#     # Récupère la commande via son ID
#     commande = get_object_or_404(Commande, id=commande_id)

#     # -----------------------------
#     # Récupère les données du formulaire en sécurisant la conversion
#     # -----------------------------
#     type_paiement = request.POST.get("type_paiement")  # liquidite, orange_money, hybride

#     try:
#         montant_liquidite = float(request.POST.get("montant_liquidite") or 0)
#     except ValueError:
#         montant_liquidite = 0

#     try:
#         montant_orange = float(request.POST.get("montant_orange") or 0)
#     except ValueError:
#         montant_orange = 0

#     statut_monnaie = request.POST.get("statut_monnaie")  # remis ou avoir

#     # Mise à jour du type de paiement
#     commande.type_paiement = type_paiement
#     commande.montant_liquidite = montant_liquidite if montant_liquidite > 0 else None
#     commande.montant_orange = montant_orange if montant_orange > 0 else None

#     # Montant total de la commande
#     montant_total = float(commande.montant_total)

#     # Variables pour le retour JSON
#     avoir_cree = False
#     message_avoir = ""
#     message_erreur = ""

#     # -----------------------------
#     # Cas 1 : Paiement en liquidité
#     # -----------------------------
#     if type_paiement == "liquidite":
#         if montant_liquidite == montant_total:
#             # Montant exact → commande payée
#             commande.statut = "payer"
#             commande.monnaie_a_rendre = 0
#             commande.montant_restant = 0
#             commande.statut_monnaie = "non_applicable"

#         elif montant_liquidite < montant_total:
#             # Montant insuffisant → commande impayée
#             commande.statut = "impayee"
#             commande.montant_restant = montant_total - montant_liquidite
#             commande.monnaie_a_rendre = 0
#             commande.statut_monnaie = "non_applicable"
#             message_erreur = f"Commande impayée : il manque {commande.montant_restant} F."

#         else:
#             # Montant supérieur → monnaie à rendre ou avoir
#             monnaie = montant_liquidite - montant_total
#             commande.statut = "payer"
#             commande.montant_restant = 0

#             if statut_monnaie == "avoir":
#                 # Crée un avoir
#                 avoir = Avoir.objects.create(
#                     commande=commande,
#                     montant=monnaie,
#                     statut="en_attente"
#                 )
#                 avoir_cree = True
#                 message_avoir = f"Avoir #{avoir.id} de {monnaie} F créé avec succès."
#                 commande.statut_monnaie = "avoir"
#                 commande.monnaie_a_rendre = 0  # car transformé en avoir
#             else:
#                 # Monnaie rendue directement
#                 commande.monnaie_a_rendre = monnaie
#                 commande.statut_monnaie = "remis"

#     # -----------------------------
#     # Cas 2 : Paiement par Orange Money
#     # -----------------------------
#     elif type_paiement == "orange_money":
#         commande.montant_orange = montant_total
#         commande.statut = "payer"
#         commande.monnaie_a_rendre = 0
#         commande.montant_restant = 0
#         commande.statut_monnaie = "non_applicable"

#     # -----------------------------
#     # Cas 3 : Paiement hybride (liquidite + OM)
#     # -----------------------------
#     elif type_paiement == "hybride":
#         total_paye = montant_liquidite + montant_orange

#         if total_paye >= montant_total:
#             # Total couvre la commande → payé
#             commande.statut = "payer"
#             commande.montant_restant = 0
#             commande.monnaie_a_rendre = 0
#             commande.statut_monnaie = "non_applicable"

#             # Enregistre exactement le montant de la commande
#             commande.montant_liquidite = montant_liquidite
#             commande.montant_orange = montant_total - montant_liquidite

#         else:
#             # Total insuffisant → impayée
#             commande.statut = "impayee"
#             commande.montant_restant = montant_total - total_paye
#             commande.monnaie_a_rendre = 0
#             commande.statut_monnaie = "non_applicable"
#             message_erreur = f"Commande impayée : il manque {commande.montant_restant} F."

#     # -----------------------------
#     # Cas par défaut (inattendu)
#     # -----------------------------
#     else:
#         commande.statut = "en_attente"
#         commande.monnaie_a_rendre = 0
#         commande.montant_restant = 0
#         commande.statut_monnaie = "non_applicable"

#     # -----------------------------
#     # Sauvegarde des modifications
#     # -----------------------------
#     commande.save()

#     # -----------------------------
#     # Retour JSON
#     # -----------------------------
#     return JsonResponse({
#         "success": True if commande.statut == "payer" else False,
#         "commande_id": commande.id,
#         "statut": commande.get_statut_display(),
#         "monnaie": str(commande.monnaie_a_rendre),
#         "statut_monnaie": commande.statut_monnaie,
#         "avoir_cree": avoir_cree,
#         "message_avoir": message_avoir,
#         "message_erreur": message_erreur,
#         "montant_restant": str(commande.montant_restant)
#     })


@require_POST
@csrf_exempt
def valider_commande(request, commande_id):
    # Récupère la commande via son ID
    commande = get_object_or_404(Commande, id=commande_id)

    # Récupère les données envoyées depuis le formulaire
    type_paiement = request.POST.get("type_paiement")  # liquidité, orange_money ou hybride
    montant_liquidite = float(request.POST.get("montant_liquidite", 0))  # montant liquide saisi
    montant_orange = float(request.POST.get("montant_orange", 0))  # montant Orange Money saisi
    statut_monnaie = request.POST.get("statut_monnaie")  # remis ou avoir

    # Mise à jour du type de paiement dans la commande
    commande.type_paiement = type_paiement
    commande.montant_liquidite = montant_liquidite if montant_liquidite > 0 else None
    commande.montant_orange = montant_orange if montant_orange > 0 else None

    # Récupère le montant total de la commande
    montant_total = float(commande.montant_total)

    # Variables pour le retour JSON
    avoir_cree = False
    message_avoir = ""
    message_erreur = ""

    # -----------------------------
    # Cas 1 : Paiement en liquidité
    # -----------------------------
    if type_paiement == "liquidite":
        if montant_liquidite == montant_total:
            commande.statut = "payer"
            commande.monnaie_a_rendre = 0
            commande.montant_restant = 0
            commande.statut_monnaie = "non_applicable"

        elif montant_liquidite < montant_total:
            commande.statut = "impayee"
            commande.montant_restant = montant_total - montant_liquidite
            commande.monnaie_a_rendre = 0
            commande.statut_monnaie = "non_applicable"
            message_erreur = f"Commande impayée : il manque {commande.montant_restant} F."

        else:  # montant_liquidite > montant_total
            monnaie = montant_liquidite - montant_total
            commande.statut = "payer"
            commande.monnaie_a_rendre = monnaie
            commande.montant_restant = 0

            if statut_monnaie == "avoir":
                avoir = Avoir.objects.create(
                    commande=commande,
                    montant=monnaie,
                    statut="en_attente"
                )
                avoir_cree = True
                message_avoir = f"Avoir #{avoir.id} de {monnaie} F créé avec succès."
                commande.statut_monnaie = "avoir"
                commande.monnaie_a_rendre = 0
            else:
                commande.statut_monnaie = "remis"

    # -----------------------------
    # Cas 2 : Paiement par Orange Money
    # -----------------------------
    elif type_paiement == "orange_money":
        commande.montant_orange = montant_total
        commande.statut = "payer"
        commande.monnaie_a_rendre = 0
        commande.montant_restant = 0
        commande.statut_monnaie = "non_applicable"

    # -----------------------------
    # Cas 3 : Paiement hybride (cash + OM)
    # -----------------------------
    elif type_paiement == "hybride":
        total_paye = montant_liquidite + montant_orange

        if total_paye >= montant_total:
            commande.statut = "payer"
            commande.montant_restant = 0
            # Pas de monnaie à rendre pour les frais supplémentaires
            commande.monnaie_a_rendre = 0
            commande.statut_monnaie = "non_applicable"
            # On ajuste le montant OM pour que le total reste égal au montant de la commande
            commande.montant_orange = montant_total - montant_liquidite
        else:
            commande.statut = "impayee"
            commande.montant_restant = montant_total - total_paye
            commande.monnaie_a_rendre = 0
            commande.statut_monnaie = "non_applicable"
            message_erreur = f"Commande impayée : il manque {commande.montant_restant} F."

    else:
        commande.statut = "en_attente"
        commande.monnaie_a_rendre = 0
        commande.montant_restant = 0
        commande.statut_monnaie = "non_applicable"

    # Sauvegarde des modifications
    commande.save()

    # Réponse JSON envoyée au frontend
    return JsonResponse({
        "success": True,  # la requête a été traitée correctement
        "statut_valide": True if commande.statut == "payer" else False,
        "commande_id": commande.id,
        "statut": commande.get_statut_display(),
        "monnaie": str(commande.monnaie_a_rendre),
        "statut_monnaie": commande.statut_monnaie,
        "avoir_cree": avoir_cree,
        "message_avoir": message_avoir,
        "message_erreur": message_erreur,
        "montant_restant": str(commande.montant_restant)
    })
