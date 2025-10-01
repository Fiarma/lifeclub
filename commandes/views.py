


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

# commandes/views.py

from django.shortcuts import render
from .models import Commande, Boisson # Assurez-vous que Commande et Boisson sont importés



from django.db import transaction # <-- Assurez-vous d'avoir cet import

# ... (Vos autres imports et modèles)

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
            
            # --- 1. PRÉ-VALIDATION DU STOCK ET PRÉPARATION ---
            items_to_create = []
            stock_errors = []
            
            # Parcourir les items pour valider le stock avant de créer quoi que ce soit
            for boisson_id, quantite in items_data:
                # Utiliser get_object_or_404 pour gérer les erreurs de boisson non trouvée
                boisson = get_object_or_404(Boisson, pk=boisson_id)
                
                # Vérification du stock
                if boisson.stock_actuel < quantite:
                    stock_errors.append(f"{boisson.nom} (Demandé: {quantite}, Stock: {boisson.stock_actuel})")
                else:
                    # Stock suffisant : préparer l'item pour la création
                    items_to_create.append({'boisson': boisson, 'quantite': quantite})
            
            # Si des erreurs de stock sont détectées, afficher un message et annuler
            if stock_errors:
                error_message = "Erreur: Stock insuffisant pour les boissons suivantes : " + ", ".join(stock_errors)
                messages.error(request, error_message)
                # Rediriger vers la page d'ajout pour permettre la correction
                return redirect("commandes:ajouter_commande")


            # --- 2. CRÉATION ATOMIQUE ET MISE À JOUR DU STOCK ---
            try:
                # Utiliser transaction.atomic() pour s'assurer que si une étape échoue, tout est annulé (rollback)
                with transaction.atomic():
                    # Création de la commande
                    commande = form_commande.save()
                    total = 0
                    
                    # Création des items et mise à jour des stocks
                    for item_data in items_to_create:
                        boisson = item_data['boisson']
                        quantite = item_data['quantite']
                        
                        # A. Décrémentation du stock et sauvegarde 💥
                        boisson.stock_actuel -= quantite
                        boisson.save(update_fields=['stock_actuel'])

                        # B. Création de l'item de commande
                        item = CommandeItem.objects.create(
                            commande=commande,
                            boisson=boisson,
                            quantite=quantite
                        )
                        total += item.montant_boisson

                    # Mise à jour du montant total de la commande
                    commande.montant_total = total
                    commande.save(update_fields=['montant_total'])

            except Exception as e:
                # Si une erreur inattendue se produit pendant la transaction
                messages.error(request, "Une erreur s'est produite lors de l'enregistrement de la commande.")
                return redirect("commandes:ajouter_commande")


            messages.success(request, "Commande créée avec succès et stock mis à jour.")
            return redirect("commandes:liste_commandes")
        else:
            messages.error(request, "Veuillez sélectionner le personnel et au moins une boisson avec quantité.")
    else:
        form_commande = CommandeForm()

    return render(request, "commandes/ajouter_commande.html", {
        "form_commande": form_commande,
        "boissons": boisson_list
    })


# ... (début du fichier)

# ---------------------------
# Supprimer un item d'une commande (CORRIGÉ POUR LE STOCK)
# ---------------------------
@require_POST
@csrf_exempt
def supprimer_item(request, item_id):
    item = get_object_or_404(CommandeItem, id=item_id)
    commande = item.commande
    boisson = item.boisson # Récupération de la boisson
    quantite_supprimee = item.quantite # Récupération de la quantité avant suppression

    # NOTE : Cette action n'est permise que sur les commandes 'en_attente' (logique front-end)

    # *********************************
    # REMISE EN STOCK DE LA QUANTITÉ
    # *********************************
    boisson.stock_actuel += quantite_supprimee
    boisson.save(update_fields=['stock_actuel'])

    # Suppression de l'article de la commande
    item.delete()

    # Recalcul du montant total
    total = sum([i.quantite * i.boisson.prix_unitaire for i in commande.items.all()])
    commande.montant_total = total
    commande.save()

    return JsonResponse({
        "success": True, 
        "item_id": item_id, 
        "commande_id": commande.id, 
        "commande_total": float(total), 
        "deleted": True,
        "new_stock": boisson.stock_actuel, # Optionnel : retourner le nouveau stock
        "boisson_nom": boisson.nom, # Optionnel : retourner le nom
    })

# ... (début du fichier)

# ---------------------------
# Supprimer une commande (CORRIGÉ POUR LE STOCK)
# ---------------------------
@require_POST
@csrf_exempt
def supprimer_commande(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)

    # Vérification et remise en stock uniquement si la commande est 'en_attente'
    # (Bien que la logique front-end devrait garantir cela, c'est une bonne sécurité)
    if commande.statut == 'en_attente':
        
        # 1. Récupérer tous les articles de la commande
        items = commande.items.all()
        
        # 2. Itérer et remettre chaque quantité en stock
        for item in items:
            boisson = item.boisson
            quantite_remise = item.quantite
            
            # Mise à jour du stock
            boisson.stock_actuel += quantite_remise
            boisson.save(update_fields=['stock_actuel'])

        # 3. Supprimer la commande
        commande.delete()
        
        return JsonResponse({"success": True, "commande_id": commande_id, "message": "Commande et articles remis en stock supprimés."})
    
    else:
        # Si la commande a un autre statut (payée/impayée), la suppression simple est risquée pour la comptabilité.
        # Nous allons la supprimer sans remise en stock, mais alerter l'utilisateur (ou empêcher via le front).
        commande.delete()
        return JsonResponse({"success": True, "commande_id": commande_id, "message": "Commande supprimée (stock non réajusté car statut n'est pas 'en_attente')."})


@require_POST
@csrf_exempt
def ajouter_boisson(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    boisson_id = request.POST.get("boisson_id")
    quantite = int(request.POST.get("quantite", 1))

    if not boisson_id:
        return JsonResponse({"success": False, "message": "Veuillez choisir une boisson."})

    boisson = get_object_or_404(Boisson, id=boisson_id)

    # Vérification du stock disponible
    if boisson.stock_actuel < quantite:
        return JsonResponse({"success": False, "message": f"Stock insuffisant. Reste: {boisson.stock_actuel}"})
    
    # Vérification si l'item existe déjà pour l'incrémenter au lieu de créer un doublon
    item, created = CommandeItem.objects.get_or_create(
        commande=commande,
        boisson=boisson,
        defaults={'quantite': 0}
    )

    if not created:
        # Si l'item existe, vérifions si l'ajout dépasse le stock
        if boisson.stock_actuel < item.quantite + quantite:
            return JsonResponse({"success": False, "message": f"Stock insuffisant. Reste: {boisson.stock_actuel}"})

    # Mise à jour de la quantité dans l'item
    item.quantite += quantite
    item.save()

    # *********************************
    # DÉCREMENTATION DU STOCK ACTUEL
    # *********************************
    boisson.stock_actuel -= quantite
    boisson.save(update_fields=['stock_actuel'])

    # Recalcul du montant total de la commande
    total = sum([i.quantite * i.boisson.prix_unitaire for i in commande.items.all()])
    commande.montant_total = total
    commande.save()

    return JsonResponse({
        "success": True, 
        "commande_total": float(total),
        "item_id": item.id,
        "new_stock": boisson.stock_actuel, # Retourner le nouveau stock
        "boisson_nom": boisson.nom,
    })


# ... (supprimer_item conservé - **NOTE: le stock n'est pas remis à jour ici, car une commande non validée peut être annulée.)**


# -----------------------------
# Vue : update quantité item (CORRIGÉ POUR GÉRER LE STOCK)
# -----------------------------
@csrf_exempt
@require_POST
def update_item_quantity(request, item_id):
    item = get_object_or_404(CommandeItem, pk=item_id)
    boisson = item.boisson # On récupère la boisson associée
    action = request.POST.get("action")

    if action == "increment":
        # Vérification du stock avant d'incrémenter
        if boisson.stock_actuel <= 0:
            # On ne peut pas incrémenter si le stock est déjà à 0
            return JsonResponse({"success": False, "error": f"Stock épuisé pour {boisson.nom}"})

        item.quantite += 1
        item.save()
        
        # *********************************
        # DÉCREMENTATION DU STOCK ACTUEL
        # *********************************
        boisson.stock_actuel -= 1
        boisson.save(update_fields=['stock_actuel'])
        
    elif action == "decrement":
        if item.quantite == 1:
            # Si quantité = 1 et on décrémente, on supprime l'item
            commande = item.commande
            item.delete()
            
            # *********************************
            # REMISE EN STOCK
            # *********************************
            boisson.stock_actuel += 1 
            boisson.save(update_fields=['stock_actuel'])

            total = sum([i.montant_boisson for i in commande.items.all()])
            return JsonResponse({
                "success": True,
                "deleted": True,
                "item_id": item_id,
                "commande_id": commande.id,
                "commande_total": float(total),
                "new_stock": boisson.stock_actuel, # Retourner le nouveau stock
                "boisson_nom": boisson.nom,
            })
        else:
            item.quantite -= 1
            item.save()
            
            # *********************************
            # REMISE EN STOCK
            # *********************************
            boisson.stock_actuel += 1
            boisson.save(update_fields=['stock_actuel'])
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
        "new_stock": boisson.stock_actuel, # Retourner le nouveau stock
        "boisson_nom": boisson.nom,
    })

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



from django.http import JsonResponse # <-- NOUVEL IMPORT

from django.utils import timezone # <-- NOUVEL IMPORT

def update_avoir_statut(request, avoir_id):
    if request.method == "POST":
        avoir = get_object_or_404(Avoir, pk=avoir_id)
        new_statut = request.POST.get("statut")

        if new_statut in dict(Avoir.STATUT_CHOICES):
            # Logique pour enregistrer la date de règlement
            if new_statut == 'regle' and avoir.statut != 'regle':
                avoir.date_reglement = timezone.now()
            elif new_statut == 'en_attente' and avoir.statut == 'regle':
                # Optionnel : Si on peut revenir à en_attente, effacer la date
                avoir.date_reglement = None
                
            avoir.statut = new_statut
            avoir.save()
            
            return JsonResponse({
                "success": True,
                "message": f"L’avoir {avoir.id} est maintenant {avoir.get_statut_display()}."
            })
        return JsonResponse({"success": False, "message": "Statut invalide."})
    
    # Assurez-vous d'avoir @require_POST si vous voulez cette ligne
    return JsonResponse({"success": False, "message": "Méthode non autorisée."})


from django.views.decorators.http import require_POST # <-- Nouvel import

# ... (autres vues)




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

