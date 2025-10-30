from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.decorators import login_required # Décorateur d'authentification
from django.http import HttpResponseRedirect, HttpResponseForbidden
from .forms import LigneInventaireUpdateForm
from .models import Inventaire, Produit, CategorieProduit, LigneInventaire, Fournisseur, Approvisionnement, LigneApprovisionnement, LIEU_CHOICES
from functools import wraps
from django.core.exceptions import ValidationError # Utilisé pour gérer les erreurs de validation
from decimal import Decimal # Utilisé pour les opérations Decimal

# =========================================================================
# IMPORTATIONS REQUISES
# =========================================================================
# Importation du décorateur de rôle de l'application 'personnel'
from personnel.decorators import role_required 

# Importation des modèles et formulaires de l'application 'produits'
from .models import Inventaire, Produit, CategorieProduit
# Assurez-vous que ces formulaires existent dans produits/forms.py
# from .forms import InventaireForm, LigneInventaireFormSet, ProduitForm, CategorieProduitForm 

# --- STUBS D'IMPORT (Si les formulaires ne sont pas encore créés) ---
# Si le fichier 'produits/forms.py' n'existe pas, décommentez ceci pour éviter un plantage.
try:
    from .forms import InventaireForm, LigneInventaireFormSet, ProduitForm, CategorieProduitForm, ApprovisionnementForm, LigneApprovisionnementFormSet, FournisseurForm, LigneApprovisionnementForm

except ImportError:
    class InventaireForm: pass
    class LigneInventaireFormSet: pass
    class ProduitForm: pass
    class CategorieProduitForm: pass
# --- FIN STUBS D'IMPORT

# =========================================================================
# CONSTANTES DE RÔLES (Basées sur personnel.models.ROLE_CHOICES)
# =========================================================================
# Rôles ayant un pouvoir de gestion/validation avancé (Boss > Manager)
ROLES_GERANCE = ['boss', 'manager', 'secretaire'] 
# Rôles ayant accès à la gestion de stock et à la création d'inventaire
ROLES_STOCK_MANAGERS = ['boss', 'secretaire'] 
# Rôles ayant accès en lecture/écriture à la vente (lecture des produits)
ROLES_VUE_PRODUIT = ['boss',  'secretaire', 'caissier', 'cuisinier', 'hotesse']

# Roles pour la validatin de l'approvisionnement
ROLES_VALIDATION_APPROVISIONNEMNT = ['boss', 'secretaire']



# =========================================================================
# UTILS (Fonction utilitaire)
# =========================================================================

def can_edit_inventaire(inventaire, user):
    """
    Vérifie si l'utilisateur peut modifier un inventaire (initiateur + statut 'en_attente').
    """
    # Vérifie si l'utilisateur actuel est celui qui a initié la session
    is_initiator = inventaire.initiateur == user
    # Vérifie si le statut permet la modification
    is_pending = inventaire.statut == 'en_attente'
    
    # L'inventaire est modifiable si l'utilisateur est l'initiateur ET que le statut est 'en_attente'.
    return is_initiator and is_pending

# ---------------------------------------------------------------------------------------
# 1. GESTION DES CATÉGORIES (CRUD) - Accès Boss/Manager/Secrétaire
# ---------------------------------------------------------------------------------------

@login_required # L'utilisateur doit être connecté.
@role_required(allowed_roles=ROLES_GERANCE)
def category_list(request):
    """Vue fonctionnelle pour lister toutes les catégories de produits."""
    # Récupérer tous les objets CategorieProduit.
    categories = CategorieProduit.objects.all().order_by('nom')
    # Rendre le template en passant la liste des catégories au contexte.
    return render(request, 'categories/category_list.html', {'categories': categories})

@login_required # L'utilisateur doit être connecté.
@role_required(allowed_roles=ROLES_GERANCE)
def category_create(request):
    """Vue fonctionnelle pour créer une nouvelle catégorie."""
    # Vérification de la méthode HTTP (soumission du formulaire).
    if request.method == 'POST':
        # Instanciation du formulaire avec les données de la requête.
        form = CategorieProduitForm(request.POST)
        # Validation du formulaire.
        if form.is_valid():
            # Sauvegarde des données dans la base de données.
            form.save()
            # Ajout d'un message flash de succès.
            messages.success(request, "La catégorie a été créée avec succès.")
            # Redirection vers la liste des catégories.
            return redirect('produits:category_list')
    else:
        # Instanciation d'un formulaire vide pour la méthode GET.
        form = CategorieProduitForm()
    # Rendu du template du formulaire.
    return render(request, 'categories/category_form.html', {'form': form})

@login_required # L'utilisateur doit être connecté.
@role_required(allowed_roles=ROLES_GERANCE)
def category_update(request, pk):
    """Vue fonctionnelle pour modifier une catégorie existante."""
    # Récupération de l'objet CategorieProduit par sa clé primaire (ou 404).
    category = get_object_or_404(CategorieProduit, pk=pk)
    
    if request.method == 'POST':
        # Instanciation du formulaire avec les données POST et l'instance à modifier.
        form = CategorieProduitForm(request.POST, instance=category)
        if form.is_valid():
            # Sauvegarde de l'objet mis à jour.
            form.save()
            # Message de succès.
            messages.success(request, f"La catégorie '{category.nom}' a été mise à jour.")
            # Redirection.
            return redirect('produits:category_list')
    else:
        # Pré-remplissage du formulaire avec l'instance existante pour la méthode GET.
        form = CategorieProduitForm(instance=category)
    # Rendu du template.
    return render(request, 'categories/category_form.html', {'form': form, 'category': category})

@login_required # L'utilisateur doit être connecté.
@role_required(allowed_roles=ROLES_GERANCE)
def category_delete(request, pk):
    """Vue fonctionnelle pour supprimer une catégorie."""
    # Récupération de l'objet.
    category = get_object_or_404(CategorieProduit, pk=pk)
    
    if request.method == 'POST':
        # Suppression de l'objet après confirmation POST.
        category.delete()
        # Message de succès.
        messages.success(request, f"La catégorie '{category.nom}' a été supprimée.")
        # Redirection.
        return redirect('produits:category_list')
        
    # Rendu du template de confirmation.
    return render(request, 'categories/category_confirm_delete.html', {'category': category})

# ---------------------------------------------------------------------------------------
# 2. GESTION DES PRODUITS (CRUD)
# ---------------------------------------------------------------------------------------

@login_required # L'utilisateur doit être connecté.
@role_required(allowed_roles=ROLES_VUE_PRODUIT)
def product_list(request):
    """Vue fonctionnelle pour lister tous les produits. Accessible aux rôles de vente et de gestion."""
    # Récupération de tous les produits, triés par statut actif puis par nom.
    products = Produit.objects.all().order_by('-is_active', 'nom')
    # Rendu du template.
    return render(request, 'produits/product_list.html', {'products': products})

@login_required # L'utilisateur doit être connecté.
@role_required(allowed_roles=ROLES_STOCK_MANAGERS)
def product_create(request):
    """Vue fonctionnelle pour créer un nouveau produit. Réservé aux managers de stock."""
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            # Sauvegarde avec commit=False pour modifier l'instance avant l'enregistrement final.
            produit = form.save(commit=False)
            # Logique pour s'assurer que le stock initial est synchronisé avec le stock actuel à la création.
            produit.stock_initial = produit.stock_actuel 
            # Sauvegarde finale de l'objet Produit.
            produit.save()
            messages.success(request, "Le produit a été créé avec succès.")
            return redirect('produits:product_list')
    else:
        # Formulaire vide.
        form = ProduitForm()
    # Rendu du template.
    return render(request, 'produits/product_form.html', {'form': form, 'title': "Créer un nouveau Produit"})

@login_required # L'utilisateur doit être connecté.
@role_required(allowed_roles=ROLES_STOCK_MANAGERS)
def product_update(request, pk):
    """Vue fonctionnelle pour modifier un produit existant. Réservé aux managers de stock."""
    product = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        # Instanciation liée à l'instance et aux données POST.
        form = ProduitForm(request.POST, instance=product)
        if form.is_valid():
            # La méthode save() du modèle Produit gère le calcul de la marge.
            form.save() 
            messages.success(request, f"Le produit '{product.nom}' a été mis à jour.")
            return redirect('produits:product_list')
    else:
        # Formulaire pré-rempli.
        form = ProduitForm(instance=product)
    # Rendu du template.
    return render(request, 'produits/product_form.html', {'form': form, 'title': f"Modifier {product.nom}", 'product': product})

@login_required # L'utilisateur doit être connecté.
@role_required(allowed_roles=ROLES_GERANCE)
def product_delete(request, pk):
    """Vue fonctionnelle pour supprimer un produit. Réservé à la gérance."""
    product = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        # Suppression.
        product.delete()
        messages.success(request, f"Le produit '{product.nom}' a été supprimé.")
        return redirect('produits:product_list')
    # Rendu du template de confirmation.
    return render(request, 'produits/product_confirm_delete.html', {'product': product})


# ---------------------------------------------------------------------------------------
# 3. GESTION DES INVENTAIRES (Fonctions)
# ---------------------------------------------------------------------------------------

# @login_required # L'utilisateur doit être connecté.
# @role_required(allowed_roles=ROLES_STOCK_MANAGERS)
# def inventaire_list(request):
#     """Vue fonctionnelle pour afficher la liste de toutes les sessions d'inventaire."""
#     # Récupérer les inventaires non annulés, triés par date de création.
#     inventaires = Inventaire.objects.exclude(statut='annule').order_by('-date_creation')
#     return render(request, 'produits/inventaire_list.html', {'object_list': inventaires})

# @login_required # L'utilisateur doit être connecté.
# @role_required(allowed_roles=ROLES_STOCK_MANAGERS)
# def inventaire_detail(request, pk):
#     """Vue fonctionnelle pour afficher le détail d'un inventaire spécifique."""
#     # Récupération de l'objet Inventaire.
#     inventaire = get_object_or_404(Inventaire, pk=pk)
    
#     # Appel de la méthode pour recalculer les totaux au cas où des lignes auraient été modifiées indirectement.
#     inventaire.calculer_totaux_globaux() 
    
#     # Récupérer les lignes d'inventaire liées (produits dénombrables).
#     lignes = inventaire.lignes.filter(produit__nature='denombrable')
    
#     # Déterminer si l'utilisateur est autorisé à éditer l'inventaire.
#     can_edit = can_edit_inventaire(inventaire, request.user)
    
#     # Vérifier si l'utilisateur est un validateur (Boss, Manager, Secrétaire).
#     is_validator = request.user.is_superuser or (hasattr(request.user, 'personnel_profile') and request.user.personnel_profile.role in ROLES_GERANCE)
    
#     # L'inventaire est validable s'il est 'en_attente' ET si l'utilisateur est un validateur.
#     can_validate = inventaire.statut == 'en_attente' and is_validator
    
#     return render(request, 'produits/inventaire_detail.html', {
#         'inventaire': inventaire,
#         'lignes': lignes,
#         'can_edit': can_edit,
#         'can_validate': can_validate,
#     })


# @login_required
# @role_required(allowed_roles=ROLES_STOCK_MANAGERS)
# def inventaire_create_update(request, pk=None):
#     """Vue fonctionnelle pour la création ou la modification d'un inventaire."""
    
#     inventaire = None
    
#     # Logique pour la modification (si pk est fourni)
#     if pk:
#         inventaire = get_object_or_404(Inventaire, pk=pk)
#         if not can_edit_inventaire(inventaire, request.user):
#             messages.error(request, "Vous ne pouvez pas modifier cet inventaire.")
#             return redirect('produits:inventaire_detail', pk=pk)

#     if request.method == 'POST':
#         form = InventaireForm(request.POST, instance=inventaire)
#         formset = LigneInventaireFormSet(request.POST, instance=inventaire)
        
#         # DEBUG: Afficher les données pour comprendre le problème
#         print("=== DEBUG ===")
#         print("POST data:", request.POST)
#         print("Form is valid:", form.is_valid())
#         print("Formset is valid:", formset.is_valid())
        
#         if form.is_valid():
#             print("Formulaire principal valide")
#             if formset.is_valid():
#                 print("Formset valide")
#                 try:
#                     with transaction.atomic():
#                         new_inventaire = form.save(commit=False)
                        
#                         # Logique de création
#                         if not new_inventaire.pk:
#                             new_inventaire.initiateur = request.user
#                             new_inventaire.statut = 'en_attente'
                        
#                         new_inventaire.save()
                        
#                         # Sauvegarder le formset
#                         instances = formset.save(commit=False)
#                         for instance in instances:
#                             instance.inventaire = new_inventaire
#                             instance.save()
                        
#                         # Supprimer les lignes marquées pour suppression
#                         for form in formset.deleted_forms:
#                             if form.instance.pk:
#                                 form.instance.delete()
                        
#                         # Recalcul des totaux
#                         new_inventaire.calculer_totaux_globaux()
                        
#                         action = "modifié" if pk else "créé"
#                         messages.success(request, f"L'inventaire a été {action} et mis en attente de validation.")
#                         return redirect('produits:inventaire_detail', pk=new_inventaire.pk)
                        
#                 except Exception as e:
#                     messages.error(request, f"Erreur lors de l'enregistrement: {str(e)}")
#                     print("Erreur:", str(e))
#             else:
#                 print("Erreurs formset:", formset.errors)
#                 print("Erreurs non-form:", formset.non_form_errors())
#                 messages.error(request, "Veuillez corriger les erreurs dans les lignes d'inventaire.")
#         else:
#             print("Erreurs formulaire:", form.errors)
#             messages.error(request, "Veuillez corriger les erreurs dans le formulaire principal.")

#     else:
#         form = InventaireForm(instance=inventaire)
#         formset = LigneInventaireFormSet(instance=inventaire)
        
#     # Pour le contexte template
#     produits = Produit.objects.filter(nature='denombrable', is_active=True).order_by('nom')
    
#     return render(request, 'produits/inventaire_form.html', {
#         'form': form,
#         'ligne_formset': formset,
#         'inventaire': inventaire,
#         'is_update': pk is not None,
#         'produits': produits,
#     })




# @login_required # L'utilisateur doit être connecté.
# @role_required(allowed_roles=ROLES_GERANCE)
# def inventaire_validate(request, pk):
#     """Vue fonctionnelle pour la validation finale d'un inventaire par la gérance."""
#     inventaire = get_object_or_404(Inventaire, pk=pk)

#     # Vérification du statut avant la validation.
#     if inventaire.statut != 'en_attente':
#         messages.error(request, "Cet inventaire n'est pas en attente de validation.")
#         return redirect('produits:inventaire_detail', pk=pk)

#     if request.method == 'POST':
#         try:
#             # Appel de la méthode transactionnelle pour valider et appliquer les changements de stock.
#             inventaire.appliquer_validation(utilisateur_secretaire=request.user) 
#             messages.success(request, f"L'inventaire '{inventaire.nom}' a été validé et le stock mis à jour.")
#         except ValidationError as e:
#             # Capture des erreurs de validation (ex: stock négatif).
#             messages.error(request, f"Erreur de validation: {e.message}")
#         except Exception as e:
#             messages.error(request, f"Erreur inattendue lors de la validation : {e}")
        
#     return redirect('produits:inventaire_detail', pk=pk)

# ######################

# @login_required
# @role_required(allowed_roles=ROLES_STOCK_MANAGERS)
# def ligne_inventaire_edit(request, pk):
#     """Vue pour modifier une ligne d'inventaire individuelle."""
#     ligne = get_object_or_404(LigneInventaire, pk=pk)
#     inventaire = ligne.inventaire
    
#     # Vérifier les permissions
#     if not can_edit_inventaire(inventaire, request.user):
#         messages.error(request, "Vous ne pouvez pas modifier cette ligne d'inventaire.")
#         return redirect('produits:inventaire_detail', pk=inventaire.pk)
    
#     if request.method == 'POST':
#         form = LigneInventaireUpdateForm(request.POST, instance=ligne)
#         if form.is_valid():
#             form.save()
#             # Recalculer les totaux de l'inventaire parent
#             inventaire.calculer_totaux_globaux()
#             messages.success(request, f"La ligne pour '{ligne.produit.nom}' a été mise à jour.")
#             return redirect('produits:inventaire_detail', pk=inventaire.pk)
#     else:
#         form = LigneInventaireUpdateForm(instance=ligne)
    
#     return render(request, 'produits/ligne_inventaire_edit.html', {
#         'form': form,
#         'ligne': ligne,
#         'inventaire': inventaire,
#     })


# ---------------------------------------------------------------------------------------
# 3. GESTION DES INVENTAIRES (Fonctions)
# ---------------------------------------------------------------------------------------

@login_required 
@role_required(allowed_roles=ROLES_STOCK_MANAGERS)
def inventaire_list(request):
    """Vue fonctionnelle pour afficher la liste de toutes les sessions d'inventaire."""
    inventaires = Inventaire.objects.exclude(statut='annule').order_by('-date_creation')
    return render(request, 'inventaires/inventaire_list.html', {'object_list': inventaires})

@login_required 
@role_required(allowed_roles=ROLES_STOCK_MANAGERS)
def inventaire_detail(request, pk):
    """Vue fonctionnelle pour afficher le détail d'un inventaire spécifique."""
    inventaire = get_object_or_404(Inventaire, pk=pk)
    
    inventaire.calculer_totaux_globaux() 
    
    lignes = inventaire.lignes.filter(produit__nature='denombrable')
    
    can_edit = can_edit_inventaire(inventaire, request.user)
    
    is_validator = request.user.is_superuser or (hasattr(request.user, 'personnel_profile') and request.user.personnel_profile.role in ROLES_GERANCE)
    
    can_validate = inventaire.statut == 'en_attente' and is_validator
    
    return render(request, 'inventaires/inventaire_detail.html', {
        'inventaire': inventaire,
        'lignes': lignes,
        'can_edit': can_edit,
        'can_validate': can_validate,
    })


@login_required
@role_required(allowed_roles=ROLES_STOCK_MANAGERS)
def inventaire_create_update(request, pk=None):
    """Vue fonctionnelle pour la création ou la modification d'un inventaire."""
    
    inventaire = None
    
    if pk:
        inventaire = get_object_or_404(Inventaire, pk=pk)
        if not can_edit_inventaire(inventaire, request.user):
            messages.error(request, "Vous ne pouvez pas modifier cet inventaire.")
            return redirect('produits:inventaire_detail', pk=pk)

    if request.method == 'POST':
        form = InventaireForm(request.POST, instance=inventaire)
        formset = LigneInventaireFormSet(request.POST, instance=inventaire)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    new_inventaire = form.save(commit=False)
                    
                    if not new_inventaire.pk:
                        new_inventaire.initiateur = request.user
                        new_inventaire.statut = 'en_attente'
                    
                    new_inventaire.save()
                    
                    instances = formset.save(commit=False)
                    for instance in instances:
                        
                        # CORRECTION CRUCIALE : Capture du stock théorique (stock_actuel du Produit)
                        # au moment de la première sauvegarde de la LigneInventaire.
                        if instance.produit:
                            # Capture uniquement si c'est une nouvelle instance ou si stock_initial est vide
                            if not instance.pk or instance.stock_initial is None:
                                # Utilisez le stock actuel du produit comme stock initial pour la ligne
                                instance.stock_initial = instance.produit.stock_actuel
                                
                        instance.inventaire = new_inventaire
                        instance.save()
                    
                    for form in formset.deleted_forms:
                        if form.instance.pk:
                            form.instance.delete()
                    
                    new_inventaire.calculer_totaux_globaux()
                    
                    action = "modifié" if pk else "créé"
                    messages.success(request, f"L'inventaire a été {action} et mis en attente de validation.")
                    return redirect('produits:inventaire_detail', pk=new_inventaire.pk)
                    
            except Exception as e:
                messages.error(request, f"Erreur lors de l'enregistrement: {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans les lignes d'inventaire.")

    else:
        form = InventaireForm(instance=inventaire)
        formset = LigneInventaireFormSet(instance=inventaire)
        
    produits = Produit.objects.filter(nature='denombrable', is_active=True).order_by('nom')
    
    return render(request, 'inventaires/inventaire_form.html', {
        'form': form,
        'ligne_formset': formset,
        'inventaire': inventaire,
        'is_update': pk is not None,
        'produits': produits,
    })


@login_required
@role_required(allowed_roles=ROLES_STOCK_MANAGERS)
def inventaire_ligne_update(request, pk):
    """Vue pour modifier une ligne d'inventaire spécifique."""
    
    ligne = get_object_or_404(LigneInventaire, pk=pk) # La NameError est corrigée par l'importation
    inventaire = ligne.inventaire

    if inventaire.statut != 'en_attente' or inventaire.initiateur != request.user:
        messages.error(request, "Vous ne pouvez modifier cette ligne que si l'inventaire est en attente et que vous êtes l'initiateur.")
        return redirect('produits:inventaire_detail', pk=inventaire.pk)

    if request.method == 'POST':
        form = LigneInventaireUpdateForm(request.POST, instance=ligne)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    new_ligne = form.save() 
                    
                    inventaire.calculer_totaux_globaux()
                    
                    messages.success(request, f"La ligne d'inventaire pour '{new_ligne.produit.nom}' a été mise à jour. Les totaux ont été recalculés.")
                    return redirect('produits:inventaire_detail', pk=inventaire.pk)
                    
            except Exception as e:
                messages.error(request, f"Erreur lors de la mise à jour de la ligne: {str(e)}")
                
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire de ligne.")
    
    else:
        form = LigneInventaireUpdateForm(instance=ligne)
        
    return render(request, 'inventaires/inventaire_ligne_form.html', {
        'form': form,
        'ligne': ligne,
        'inventaire': inventaire,
    })


@login_required 
@role_required(allowed_roles=ROLES_GERANCE)
def inventaire_validate(request, pk):
    """Vue fonctionnelle pour la validation finale d'un inventaire par la gérance."""
    inventaire = get_object_or_404(Inventaire, pk=pk)

    if inventaire.statut != 'en_attente':
        messages.error(request, "Cet inventaire n'est pas en attente de validation.")
        return redirect('produits:inventaire_detail', pk=pk)

    if request.method == 'POST':
        try:
            inventaire.appliquer_validation(utilisateur_secretaire=request.user) 
            messages.success(request, f"L'inventaire '{inventaire.nom}' a été validé et le stock mis à jour.")
        except ValidationError as e:
            messages.error(request, f"Erreur de validation: {e.message}")
        except Exception as e:
            messages.error(request, f"Erreur inattendue lors de la validation : {e}")
        
    return redirect('inventaires:inventaire_detail', pk=pk)



####### 27 -10- 2025 #############

ROLES_FOURNISSEUR = ['boss', 'secretaire']
# Roles pour la validatin de l'approvisionnement
ROLES_AJOUT_APPROVISIONNEMNT = ['boss', 'secretaire', 'cuisinier', 'caissier', 'technicien', 'serveur']

# Ce role permet de tout faire
TOUT_ROLE = ['boss', 'admin']


# =======================================================================================
# VUES DE GESTION DES FOURNISSEURS (CRUD)
# =======================================================================================

@login_required 
@role_required(allowed_roles=ROLES_FOURNISSEUR)
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all().order_by('nom')
    return render(request, 'fournisseurs/fournisseur_list.html', {
        'object_list': fournisseurs,
    })

@login_required
@role_required(allowed_roles=ROLES_FOURNISSEUR)
def fournisseur_create_update(request, pk=None):
    if pk:
        fournisseur = get_object_or_404(Fournisseur, pk=pk)
        title = f"Modifier Fournisseur : {fournisseur.nom}"
    else:
        fournisseur = None
        title = "Créer un Nouveau Fournisseur"
    
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le fournisseur '{form.instance.nom}' a été enregistré.")
            return redirect('produits:fournisseur_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = FournisseurForm(instance=fournisseur)
        
    return render(request, 'fournisseurs/fournisseur_form.html', {
        'form': form,
        'title': title,
    })

@login_required
@role_required(allowed_roles=ROLES_FOURNISSEUR)
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        nom = fournisseur.nom
        fournisseur.delete()
        messages.success(request, f"Le fournisseur '{nom}' a été supprimé.")
        return redirect('produits:fournisseur_list')
    # Pour afficher une page de confirmation si nécessaire
    return render(request, 'fournisseurs/fournisseur_confirm_delete.html', {'fournisseur': fournisseur})



# =======================================================================================
# VUES DE GESTION D'APPROVISIONNEMENT
# =======================================================================================

@login_required 
@role_required(allowed_roles=ROLES_AJOUT_APPROVISIONNEMNT)
def approvisionnement_list(request):
    approvisionnements = Approvisionnement.objects.all().order_by('-date_approvisionnement')
    return render(request, 'approvisionnements/approvisionnement_list.html', {
        'object_list': approvisionnements,
    })


def update_appro_totals(approvisionnement):
    """Met à jour les totaux agrégés de l'Approvisionnement sans toucher au stock."""
    
    # 1. Calculer les totaux basés sur les lignes
    lignes_stats = approvisionnement.lignes_appro.aggregate(
        montant_total=Sum('montant_total_produit'),
        qte_recue=Sum('quantite_recue'),  # NOUVEAU - somme des quantités reçues
        qte_perdue=Sum('quantite_endommagee'),
        montant_perte=Sum('montant_perte'),
    )
    
    montant_achats = lignes_stats.get('montant_total') or Decimal('0.00')
    montant_perte = lignes_stats.get('montant_perte') or Decimal('0.00')
    qte_perdue = lignes_stats.get('qte_perdue') or 0
    qte_recue = lignes_stats.get('qte_recue') or 0  # NOUVEAU
    
    # 2. Mise à jour des champs de l'Approvisionnement
    approvisionnement.montant_achats_total = montant_achats
    approvisionnement.quantite_recue_total = qte_recue  # NOUVEAU
    approvisionnement.quantite_perdue_total = qte_perdue
    approvisionnement.montant_perte_total = montant_perte
    approvisionnement.cout_approvisionnement_global = montant_achats + approvisionnement.cout_transport
    
    # 3. Sauvegarde (sans commit)
    approvisionnement.save()   

@login_required
@role_required(allowed_roles=ROLES_AJOUT_APPROVISIONNEMNT)
def approvisionnement_create_update(request, pk=None):
    if pk:
        approvisionnement = get_object_or_404(Approvisionnement, pk=pk)
        
        # Interdire la modification si validé
        if approvisionnement.statut == 'valide':
            messages.warning(request, "Cet approvisionnement est validé et ne peut plus être modifié.")
            return redirect('produits:approvisionnement_detail', pk=pk)
        
        title = f"Modifier Approvisionnement : {approvisionnement.nom}"
    else:
        approvisionnement = None
        title = "Créer un Nouvel Approvisionnement"

    if request.method == 'POST':
        form = ApprovisionnementForm(request.POST, instance=approvisionnement)
        formset = LigneApprovisionnementFormSet(request.POST, instance=approvisionnement)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # 1. Sauvegarde de l'Approvisionnement Parent
                    approvisionnement = form.save(commit=False)
                    if not approvisionnement.pk:
                        approvisionnement.personnel = request.user
                        approvisionnement.statut = 'en_attente'
                    approvisionnement.save()
                    
                    # 2. Sauvegarde des Lignes (les méthodes save des lignes calculent les PA unitaires et pertes)
                    formset.instance = approvisionnement
                    formset.save()
                    
                    # 3. Mise à jour des totaux agrégés (sans toucher au stock)
                    update_appro_totals(approvisionnement)
                    
                    action = "modifié" if pk else "enregistré"
                    messages.success(request, f"L'approvisionnement '{approvisionnement.nom}' a été {action} et est en attente de validation.")
                    return redirect('produits:approvisionnement_detail', pk=approvisionnement.pk)
                    
            except Exception as e:
                messages.error(request, f"Erreur critique lors de l'opération : {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire ou dans les lignes de produits.")

    else:
        form = ApprovisionnementForm(instance=approvisionnement)
        formset = LigneApprovisionnementFormSet(instance=approvisionnement)
        
    return render(request, 'approvisionnements/approvisionnement_form.html', {
        'form': form,
        'ligne_formset': formset,
        'title': title,
        'approvisionnement': approvisionnement,
    })



def _is_user_in_allowed_roles(user, allowed_roles):
    """
    Vérifie si l'utilisateur est superutilisateur OU s'il possède un rôle autorisé.
    Cette logique reflète la vérification dans votre décorateur role_required.
    """
    if user.is_superuser:
        return True
    
    # Logique de vérification du personnel_profile
    if hasattr(user, 'personnel_profile'):
        try:
            user_role = user.personnel_profile.role 
            return user_role in allowed_roles
        except AttributeError:
            return False
    return False

def user_can_validate_approvisionement(user):
    """Vérifie si l'utilisateur a le rôle requis (ROLES_FOURNISSEUR) pour valider l'Approvisionnement."""
    return _is_user_in_allowed_roles(user, ROLES_FOURNISSEUR)


@login_required
@role_required(allowed_roles=ROLES_AJOUT_APPROVISIONNEMNT) # Rôle minimum pour voir le détail
def approvisionnement_detail(request, pk):
    """
    Vue fonctionnelle pour afficher le détail d'un approvisionnement spécifique.
    Logique de permission inspirée par inventaire_detail.
    """
    approvisionnement = get_object_or_404(Approvisionnement, pk=pk)
    lignes = approvisionnement.lignes_appro.all()
    
    # 🌟 INSPIRÉ DE LA LOGIQUE DE L'INVENTAIRE :
    
    # 1. Détermination du Validateur (équivalent à 'is_validator' de l'inventaire)
    is_validator = user_can_validate_approvisionement(request.user) 
    
    # 2. Détermination de la Validation (équivalent à 'can_validate' de l'inventaire)
    can_validate = approvisionnement.statut == 'en_attente' and is_validator
    
    # 3. Détermination de la Modification (équivalent à 'can_edit' de l'inventaire, mais simplifié)
    # On permet d'éditer si l'approvisionnement n'est pas encore validé
    # ET si l'utilisateur a le rôle de gestionnaire de stock.
    can_edit = approvisionnement.statut != 'valide' and _is_user_in_allowed_roles(request.user, ROLES_FOURNISSEUR)
    
    return render(request, 'approvisionnements/approvisionnement_detail.html', {
        'approvisionnement': approvisionnement,
        'lignes': lignes,
        'can_validate': can_validate, # Utilisé pour afficher le bouton Valider
        'can_edit': can_edit,         # Utilisé pour afficher le bouton Modifier/Supprimer
    })


# @login_required
# @role_required(allowed_roles=ROLES_FOURNISSEUR) 
# def approvisionnement_valider(request, pk):
#     approvisionnement = get_object_or_404(Approvisionnement, pk=pk)
    
#     if approvisionnement.statut == 'valide':
#         messages.warning(request, f"L'approvisionnement est déjà validé.")
#         return redirect('produits:approvisionnement_detail', pk=pk)

#     if request.method == 'POST':
#         try:
#             with transaction.atomic():
                
#                 # 1. Mettre à jour le stock et le prix d'achat du Produit
#                 for ligne in approvisionnement.lignes_appro.all():
#                     produit = Produit.objects.select_for_update().get(pk=ligne.produit.pk)
                    
#                     if produit.nature == 'denombrable':
#                         # Ajustement du stock
#                         produit.stock_actuel = (produit.stock_actuel or 0) + ligne.quantite_nette
                        
#                         # Mise à jour du prix d'achat (PA unitaire de la ligne)
#                         produit.prix_achat = ligne.prix_achat_unitaire
#                         produit.save()
                    
#                     # Logique pour les non-dénombrables irait ici si nécessaire
                    
#                 # 2. Mettre à jour le statut de l'Approvisionnement
#                 approvisionnement.controleur = request.user
#                 approvisionnement.date_validation = timezone.now()
#                 approvisionnement.statut = 'valide'
#                 approvisionnement.save()
                
#                 messages.success(request, f"L'approvisionnement {approvisionnement.nom} a été validé et le stock des produits mis à jour.")
        
#         except Exception as e:
#             messages.error(request, f"Erreur critique lors de la validation et mise à jour du stock : {str(e)}")
            
#         return redirect('produits:approvisionnement_detail', pk=approvisionnement.pk)
        
#     return redirect('produits:approvisionnement_detail', pk=approvisionnement.pk)


# @login_required
# @role_required(allowed_roles=ROLES_FOURNISSEUR) 
# def approvisionnement_valider(request, pk):
#     approvisionnement = get_object_or_404(Approvisionnement, pk=pk)
    
#     # Vérifications préliminaires
#     if approvisionnement.statut == 'valide':
#         messages.warning(request, "Cet approvisionnement est déjà validé.")
#         return redirect('produits:approvisionnement_detail', pk=pk)
    
#     if approvisionnement.statut == 'annule':
#         messages.error(request, "Impossible de valider un approvisionnement annulé.")
#         return redirect('produits:approvisionnement_detail', pk=pk)

#     if request.method == 'POST':
#         try:
#             with transaction.atomic():
#                 produits_modifies = []
                
#                 # 1. Vérifier d'abord toutes les contraintes
#                 for ligne in approvisionnement.lignes_appro.all():
#                     if ligne.produit.nature == 'denombrable':
#                         nouveau_stock = (ligne.produit.stock_actuel or 0) + ligne.quantite_nette
#                         if nouveau_stock < 0:
#                             raise ValidationError(
#                                 f"Stock insuffisant pour '{ligne.produit.nom}'. "
#                                 f"Stock actuel: {ligne.produit.stock_actuel}, "
#                                 f"Quantité nette: {ligne.quantite_nette}"
#                             )
                
#                 # 2. Appliquer les modifications si toutes les vérifications passent
#                 for ligne in approvisionnement.lignes_appro.all():
#                     produit = Produit.objects.select_for_update().get(pk=ligne.produit.pk)
                    
#                     if produit.nature == 'denombrable':
#                         # Sauvegarder l'ancien stock pour le log
#                         ancien_stock = produit.stock_actuel
                        
#                         # Mise à jour du stock
#                         produit.stock_actuel = (produit.stock_actuel or 0) + ligne.quantite_nette
                        
#                         # Mise à jour du prix d'achat seulement si valide
#                         if ligne.prix_achat_unitaire and ligne.prix_achat_unitaire > Decimal('0.00'):
#                             produit.prix_achat = ligne.prix_achat_unitaire
                        
#                         produit.save()
#                         produits_modifies.append({
#                             'nom': produit.nom,
#                             'ancien_stock': ancien_stock,
#                             'nouveau_stock': produit.stock_actuel,
#                             'quantite_ajoutee': ligne.quantite_nette
#                         })
                
#                 # 3. Finaliser l'approvisionnement
#                 approvisionnement.controleur = request.user
#                 approvisionnement.date_validation = timezone.now()
#                 approvisionnement.statut = 'valide'
#                 approvisionnement.save()
                
#                 # Message de succès détaillé
#                 message_succes = (
#                     f"✅ Approvisionnement '{approvisionnement.nom}' validé. "
#                     f"Stocks mis à jour pour {len(produits_modifies)} produit(s)."
#                 )
#                 messages.success(request, message_succes)
                
#                 # Log supplémentaire (optionnel)
#                 for produit in produits_modifies:
#                     print(f"Stock {produit['nom']}: {produit['ancien_stock']} → {produit['nouveau_stock']} (+{produit['quantite_ajoutee']})")
        
#         except ValidationError as e:
#             messages.error(request, f"❌ Erreur de validation : {str(e)}")
#         except Exception as e:
#             messages.error(request, f"❌ Erreur critique : {str(e)}")
            
#         return redirect('produits:approvisionnement_detail', pk=approvisionnement.pk)
    
#     # Si méthode GET, rediriger vers la page de détail
#     return redirect('produits:approvisionnement_detail', pk=approvisionnement.pk)


@login_required
@role_required(allowed_roles=ROLES_FOURNISSEUR) 
def approvisionnement_valider(request, pk):
    approvisionnement = get_object_or_404(Approvisionnement, pk=pk)
    
    if approvisionnement.statut == 'valide':
        messages.warning(request, "Cet approvisionnement est déjà validé.")
        return redirect('produits:approvisionnement_detail', pk=pk)
    
    if approvisionnement.statut == 'annule':
        messages.error(request, "Impossible de valider un approvisionnement annulé.")
        return redirect('produits:approvisionnement_detail', pk=pk)

    if request.method == 'GET':
        # Afficher la page de confirmation
        return render(request, 'approvisionnements/approvisionnement_confirm_validation.html', {
            'approvisionnement': approvisionnement
        })
    
    elif request.method == 'POST':
        # Traitement de la validation confirmée
        try:
            with transaction.atomic():
                produits_modifies = []
                
                # Vérifier toutes les contraintes
                for ligne in approvisionnement.lignes_appro.all():
                    if ligne.produit.nature == 'denombrable':
                        nouveau_stock = (ligne.produit.stock_actuel or 0) + ligne.quantite_nette
                        if nouveau_stock < 0:
                            raise ValidationError(
                                f"Stock insuffisant pour '{ligne.produit.nom}'"
                            )
                
                # Appliquer les modifications
                for ligne in approvisionnement.lignes_appro.all():
                    produit = Produit.objects.select_for_update().get(pk=ligne.produit.pk)
                    
                    if produit.nature == 'denombrable':
                        # Mise à jour du stock
                        produit.stock_actuel = (produit.stock_actuel or 0) + ligne.quantite_nette
                        
                        # Mise à jour du prix d'achat
                        if ligne.prix_achat_unitaire and ligne.prix_achat_unitaire > Decimal('0.00'):
                            produit.prix_achat = ligne.prix_achat_unitaire
                        
                        produit.save()
                        produits_modifies.append(produit.nom)
                
                # Finaliser l'approvisionnement
                approvisionnement.controleur = request.user
                approvisionnement.date_validation = timezone.now()
                approvisionnement.statut = 'valide'
                approvisionnement.save()
                
                messages.success(
                    request, 
                    f"✅ Approvisionnement validé ! Stocks mis à jour pour {len(produits_modifies)} produit(s)."
                )
                
        except ValidationError as e:
            messages.error(request, f"❌ Erreur : {str(e)}")
        except Exception as e:
            messages.error(request, f"❌ Erreur critique : {str(e)}")
            
        return redirect('produits:approvisionnement_detail', pk=approvisionnement.pk)

@login_required
@role_required(allowed_roles=TOUT_ROLE) # Seuls les Gérants/Admins peuvent supprimer
def approvisionnement_delete(request, pk):
    approvisionnement = get_object_or_404(Approvisionnement, pk=pk)
    
    if approvisionnement.statut == 'valide':
        messages.error(request, "Un approvisionnement validé ne peut pas être supprimé.")
        return redirect('produits:approvisionnement_detail', pk=pk)
    
    if request.method == 'POST':
        nom = approvisionnement.nom
        approvisionnement.delete()
        messages.success(request, f"L'approvisionnement '{nom}' a été supprimé.")
        return redirect('produits:approvisionnement_list')
        
    return render(request, 'approvisionnements/approvisionnement_confirm_delete.html', {'approvisionnement': approvisionnement})


##
@login_required
@role_required(allowed_roles=ROLES_AJOUT_APPROVISIONNEMNT)
def ligne_approvisionnement_update(request, pk):
    """
    Vue pour modifier une ligne d'approvisionnement individuelle.
    """
    ligne = get_object_or_404(LigneApprovisionnement, pk=pk)
    approvisionnement = ligne.approvisionnement
    
    # Vérifier que l'approvisionnement n'est pas validé
    if approvisionnement.statut == 'valide':
        messages.warning(request, "Impossible de modifier une ligne d'un approvisionnement validé.")
        return redirect('produits:approvisionnement_detail', pk=approvisionnement.pk)
    
    if request.method == 'POST':
        form = LigneApprovisionnementForm(request.POST, instance=ligne)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Sauvegarder la ligne modifiée
                    ligne_modifiee = form.save()
                    
                    # Mettre à jour les totaux de l'approvisionnement
                    update_appro_totals(approvisionnement)
                    
                    messages.success(request, f"La ligne pour le produit {ligne.produit.nom} a été modifiée avec succès.")
                    return redirect('produits:approvisionnement_detail', pk=approvisionnement.pk)
                    
            except Exception as e:
                messages.error(request, f"Erreur lors de la modification : {str(e)}")
    else:
        form = LigneApprovisionnementForm(instance=ligne)
    
    return render(request, 'approvisionnements/ligne_approvisionnement_form.html', {
        'form': form,
        'ligne': ligne,
        'approvisionnement': approvisionnement,
        'title': f"Modifier la ligne - {ligne.produit.nom}"
    })