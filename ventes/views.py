from django.shortcuts import render

# Create your views here.

##################### Details

from depenses.models import Depense 
from avances.models import Avance
from .models import RapportVenteNocturne, DetailVenteBoisson # Modèles du rapport

from commandes.models import Commande, CommandeItem, Avoir
from  commandes.forms import CommandeForm
from boissons.models import Boisson
from personnel.models import Personnel
from datetime import timedelta, datetime
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Sum, F
from django.utils import timezone
from datetime import timedelta, datetime

# ==============================================================================
# VUES DU POINT DES VENTES (PDV)
# ==============================================================================

# def get_last_completed_sales_period(now=None):
#     """
#     Détermine la période de vente qui vient d'être achevée (terminée à 06h00).
#     """
#     if now is None:
#         now = timezone.now()
    
#     if now.hour < 6:
#         end_time = now.replace(hour=6, minute=0, second=0, microsecond=0) - timedelta(days=1)
#     else:
#         end_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        
#     start_time = end_time - timedelta(hours=12)
    
#     return start_time, end_time

# commandes/views.py


# ... (autres imports)

# REMARQUE : 01h00 du matin est l'heure de fin. 
# En format 24h, 01h00 = 1.
# END_HOUR = 1 
# PERIOD_DURATION_HOURS = 18 # 07h00 -> 01h00 du matin suivant fait 18 heures


# def get_last_completed_sales_period(now=None):
#     """
#     Détermine la période de vente qui vient d'être achevée (terminée à 01h00 du matin).
#     """
#     if now is None:
#         now = timezone.now()
    
#     # 1. Déterminer l'heure de fin (END_TIME)
    
#     # Si l'heure actuelle est AVANT l'heure de fin (01h00 du matin), 
#     # cela signifie que la période de vente actuelle est toujours en cours.
#     if now.hour < END_HOUR:
#         # L'heure de fin achevée était H-24 heures.
#         end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0) - timedelta(days=1)
#     else:
#         # L'heure de fin achevée était H (ce matin à 01h00).
#         end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
        
#     # 2. Déterminer l'heure de début (START_TIME)
    
#     # Le début est la fin moins la durée totale de la période (18 heures).
#     start_time = end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
#     return start_time, end_time


# def calculer_et_sauvegarder_rapport(start_time, end_time):
#     """
#     Effectue les calculs, sauvegarde le rapport principal et les détails des ventes.
#     Retourne le RapportVenteNocturne enregistré ou existant.
#     """
#     # 1. Tenter de récupérer le rapport existant
#     try:
#         rapport = RapportVenteNocturne.objects.prefetch_related('details_boissons').get(start_time=start_time)
#         return rapport
#     except RapportVenteNocturne.DoesNotExist:
#         pass # Continuer pour calculer et enregistrer

#     # --- Étape A : Calculs QuerySet ---
#     commandes_valides_qs = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     )
#     commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

#     ventes_boissons_qs = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).values(
#         'boisson__id', 
#         'boisson__nom', 
#         'boisson__prix_unitaire'
#     ).annotate(
#         quantite_totale=Sum('quantite'), 
#         montant_total=Sum(F('quantite') * F('boisson__prix_unitaire'))
#     ).order_by('-montant_total')

#     # --- Étape B : Calculs Financiers ---
#     montant_total_vente = ventes_boissons_qs.aggregate(total=Sum('montant_total'))['total'] or 0

#     montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
#     # Filtrage des Depense et Avance sur les deux dates civiles couvertes (DateField)
#     montant_total_depenses = Depense.objects.filter(date__gte=start_time.date(), date__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0
#     montant_total_avances = Avance.objects.filter(date_avance__gte=start_time.date(), date_avance__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0

#     montant_decaisse = montant_total_impayees + montant_total_depenses + montant_total_avances
#     chiffre_affaire = montant_total_vente - montant_decaisse

#     # --- Étape C : Sauvegarde du nouveau rapport principal ---
#     rapport = RapportVenteNocturne.objects.create(
#         start_time=start_time,
#         end_time=end_time,
#         montant_total_vente=montant_total_vente,
#         montant_total_impayees=montant_total_impayees,
#         montant_total_depenses=montant_total_depenses,
#         montant_total_avances=montant_total_avances,
#         montant_decaisse=montant_decaisse,
#         chiffre_affaire=chiffre_affaire,
#     )
    
#     # --- Étape D : Sauvegarde des détails des boissons (quantité incluse) ---
#     details_a_creer = []
    
#     for vente in ventes_boissons_qs:
#         details_a_creer.append(
#             DetailVenteBoisson(
#                 rapport=rapport,
#                 boisson_id=vente['boisson__id'], 
#                 quantite_totale=vente['quantite_totale'],
#                 montant_total=vente['montant_total'],
#                 prix_unitaire_au_moment_vente=vente['boisson__prix_unitaire']
#             )
#         )
    
#     DetailVenteBoisson.objects.bulk_create(details_a_creer)

#     return rapport

# from datetime import timedelta, datetime 
# from django.db.models import Q, Sum, F 

# def point_des_ventes(request):
    
#     start_time_default, end_time_default = get_last_completed_sales_period()
#     date_str = request.GET.get('date') 
    
#     rapport = None
    
#     if date_str:
#         try:
#             # Essayer de convertir la date de la requête au format attendu (YYYY-MM-DD HH:MM:SS)
#             start_time_to_check = timezone.make_aware(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S'))
            
#             # Récupérer le rapport enregistré
#             rapport = RapportVenteNocturne.objects.prefetch_related('details_boissons').get(start_time=start_time_to_check)
#             ventes_boissons = rapport.details_boissons.all()
            
#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             # Si la date est invalide ou le rapport non trouvé, revenir au dernier rapport complété
#             rapport = calculer_et_sauvegarder_rapport(start_time_default, end_time_default)
#             ventes_boissons = rapport.details_boissons.all()
            
#     else:
#         # Aucun paramètre 'date', on s'occupe du dernier rapport achevé et on le sauvegarde si nécessaire
#         rapport = calculer_et_sauvegarder_rapport(start_time_default, end_time_default)
#         ventes_boissons = rapport.details_boissons.all()

#     context = {
#         "start_time": rapport.start_time,
#         "end_time": rapport.end_time,
#         "ventes_boissons": ventes_boissons,
        
#         "montant_total_vente": rapport.montant_total_vente,
#         "montant_total_impayees": rapport.montant_total_impayees,
#         "montant_total_depenses": rapport.montant_total_depenses,
#         "montant_total_avances": rapport.montant_total_avances,
#         "montant_decaisse": rapport.montant_decaisse,
#         "chiffre_affaire": rapport.chiffre_affaire,
#     }

#     return render(request, "stats/point_des_ventes.html", context)

# commandes/views.py


# ... (autres imports)

# Variables pour le créneau de test 7h00 -> 1h00 du matin suivant (18 heures)
END_HOUR = 1 
PERIOD_DURATION_HOURS = 18

def get_last_completed_sales_period(now=None):
    """
    [UTILISÉE POUR L'ARCHIVAGE] Détermine la période de vente qui vient d'être achevée.
    """
    if now is None:
        now = timezone.now()
    
    if now.hour < END_HOUR:
        end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
        
    start_time = end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
    return start_time, end_time

def get_current_sales_period(now=None):
    """
    [UTILISÉE POUR L'AFFICHAGE PAR DÉFAUT] Détermine la période de vente EN COURS.
    """
    if now is None:
        now = timezone.now()
    
    # 1. Déterminer la prochaine fois que la période doit se terminer (01h00 demain)
    next_end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
    
    # Si cette heure de fin (01h00 aujourd'hui) est déjà passée, on passe à demain.
    if next_end_time <= now:
        next_end_time += timedelta(days=1)
        
    # 2. Déterminer l'heure de début (18 heures avant)
    start_time = next_end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
    return start_time, next_end_time


# commandes/views.py

# ... (Après les fonctions get_current_sales_period et calculer_ventes_en_temps_reel)

def calculer_et_sauvegarder_rapport(start_time, end_time):
    """
    Effectue les calculs, sauvegarde le rapport principal et les détails des ventes 
    (quantité par boisson) s'ils n'existent pas.
    """
    # 1. Tenter de récupérer le rapport existant
    try:
        rapport = RapportVenteNocturne.objects.prefetch_related('details_boissons').get(start_time=start_time)
        return rapport
    except RapportVenteNocturne.DoesNotExist:
        pass # Continuer pour calculer et enregistrer

    # --- Étape A : Calculs QuerySet ---
    commandes_valides_qs = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    )
    commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

    ventes_boissons_qs = CommandeItem.objects.filter(
        commande_id__in=commandes_valides_ids
    ).values(
        'boisson__id', 
        'boisson__nom', 
        'boisson__prix_unitaire'
    ).annotate(
        quantite_totale=Sum('quantite'), 
        montant_total=Sum(F('quantite') * F('boisson__prix_unitaire'))
    ).order_by('-montant_total')

    # --- Étape B : Calculs Financiers ---
    montant_total_vente = ventes_boissons_qs.aggregate(total=Sum('montant_total'))['total'] or 0

    montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
    montant_total_depenses = Depense.objects.filter(date__gte=start_time.date(), date__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0
    montant_total_avances = Avance.objects.filter(date_avance__gte=start_time.date(), date_avance__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0

    montant_decaisse = montant_total_impayees + montant_total_depenses + montant_total_avances
    chiffre_affaire = montant_total_vente - montant_decaisse

    # --- Étape C : Sauvegarde du nouveau rapport principal ---
    rapport = RapportVenteNocturne.objects.create(
        start_time=start_time,
        end_time=end_time,
        montant_total_vente=montant_total_vente,
        montant_total_impayees=montant_total_impayees,
        montant_total_depenses=montant_total_depenses,
        montant_total_avances=montant_total_avances,
        montant_decaisse=montant_decaisse,
        chiffre_affaire=chiffre_affaire,
    )
    
    # --- Étape D : Sauvegarde des détails des boissons (quantité incluse) ---
    details_a_creer = []
    
    for vente in ventes_boissons_qs:
        details_a_creer.append(
            DetailVenteBoisson(
                rapport=rapport,
                boisson_id=vente['boisson__id'], 
                quantite_totale=vente['quantite_totale'],
                montant_total=vente['montant_total'],
                prix_unitaire_au_moment_vente=vente['boisson__prix_unitaire']
            )
        )
    
    DetailVenteBoisson.objects.bulk_create(details_a_creer)

    return rapport


# ... (Maintenant, la fonction point_des_ventes peut être définie après celle-ci)
# commandes/views.py (Fonction point_des_ventes corrigée)

def point_des_ventes(request):
    
    # Période pour l'affichage (celle que l'utilisateur veut voir)
    start_time_current, end_time_current = get_current_sales_period() 
    
    # Période pour l'archivage (celle qui est complétée)
    start_time_completed, end_time_completed = get_last_completed_sales_period() 
    
    date_str = request.GET.get('date') 
    
    rapport = None
    start_time_display = start_time_current # Initialisation par défaut
    end_time_display = end_time_current     # Initialisation par défaut
    
    # Par défaut, on calcule le rapport en temps réel
    context_data = calculer_ventes_en_temps_reel(start_time_current, end_time_current)

    
    if date_str:
        # --- CAS 1 : Recherche Historique ---
        try:
            # Assurez-vous que le format est correct (la requête GET donne YYYY-MM-DDTHH:MM)
            # Nous devons retirer le 'T' pour que datetime.strptime fonctionne, ou ajuster le format.
            date_time_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            start_time_to_check = timezone.make_aware(date_time_obj)

            # Récupérer le rapport enregistré
            rapport = RapportVenteNocturne.objects.prefetch_related('details_boissons').get(start_time=start_time_to_check)
            
            # Mise à jour des variables d'affichage pour la période HISTORIQUE trouvée
            start_time_display = rapport.start_time
            end_time_display = rapport.end_time
            
        except (RapportVenteNocturne.DoesNotExist, ValueError):
            # Si le rapport n'existe pas ou la date est mal formatée, on reste sur le rapport en cours
            # context_data conserve la valeur du rapport en temps réel
            pass
            
    else:
        # --- CAS 2 : Affichage par défaut (Rapport en Cours) ---
        
        # On s'assure que le dernier rapport COMPLÉTÉ est sauvegardé
        # Cela ne se fait que si l'utilisateur n'a pas spécifiquement demandé une date.
        calculer_et_sauvegarder_rapport(start_time_completed, end_time_completed)
        
        # context_data conserve la valeur calculée en temps réel au début de la fonction.


    
    # Si on a chargé un rapport historique (rapport est un objet), on utilise ses données
    if rapport:
        # Remplacer les données calculées en temps réel par les données figées du rapport historique
        context_data = {
            "montant_total_vente": rapport.montant_total_vente,
            "montant_total_impayees": rapport.montant_total_impayees,
            "montant_total_depenses": rapport.montant_total_depenses,
            "montant_total_avances": rapport.montant_total_avances,
            "montant_decaisse": rapport.montant_decaisse,
            "chiffre_affaire": rapport.chiffre_affaire,
            "ventes_boissons": rapport.details_boissons.all()
        }
    
    # Assemblage du context final
    context = {
        "start_time": start_time_display,
        "end_time": end_time_display,
        **context_data # Merge les données calculées ou chargées (context_data est toujours défini)
    }

    return render(request, "stats/point_des_ventes.html", context)

# ----------------------------------------------------------------------------------
# NOUVELLES FONCTIONS DE CALCUL TEMPORAIRE (pour le rapport en cours)
# ----------------------------------------------------------------------------------

def calculer_ventes_detaillees_en_temps_reel(start_time, end_time):
    """
    Calcule les agrégations de boisson en temps réel (sans créer de modèle DetailVenteBoisson).
    """
    commandes_valides_qs = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    )
    commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

    ventes_boissons_raw = CommandeItem.objects.filter(
        commande_id__in=commandes_valides_ids
    ).values(
        'boisson__id', 
        'boisson__nom', 
        'boisson__prix_unitaire'
    ).annotate(
        quantite_totale=Sum('quantite'), 
        montant_total=Sum(F('quantite') * F('boisson__prix_unitaire'))
    ).order_by('-montant_total')

    # Convertir le QuerySet annoté en une liste de pseudo-objets DetailVenteBoisson pour le template
    # (Doit avoir la même structure d'accès que les objets DetailVenteBoisson du modèle)
    ventes_boissons_list = []
    for item in ventes_boissons_raw:
        ventes_boissons_list.append({
            'boisson': type('Boisson', (object,), {'nom': item['boisson__nom']}), # Pseudo-objet boisson
            'prix_unitaire_au_moment_vente': item['boisson__prix_unitaire'],
            'quantite_totale': item['quantite_totale'],
            'montant_total': item['montant_total'],
        })
    
    return ventes_boissons_list

def calculer_ventes_en_temps_reel(start_time, end_time):
    """
    Calcule les chiffres financiers en temps réel pour la période en cours.
    """
    commandes_valides_qs = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    )
    commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

    # Ventes détaillées pour le template
    ventes_boissons = calculer_ventes_detaillees_en_temps_reel(start_time, end_time)
    
    # Montant Total Vente (pour l'agrégation globale)
    montant_total_vente_calc = CommandeItem.objects.filter(
        commande_id__in=commandes_valides_ids
    ).aggregate(
        total=Sum(F('quantite') * F('boisson__prix_unitaire'))
    )['total'] or 0

    # Autres calculs financiers
    montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
    montant_total_depenses = Depense.objects.filter(date__gte=start_time.date(), date__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0
    montant_total_avances = Avance.objects.filter(date_avance__gte=start_time.date(), date_avance__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0

    montant_decaisse = montant_total_impayees + montant_total_depenses + montant_total_avances
    chiffre_affaire = montant_total_vente_calc - montant_decaisse

    return {
        "montant_total_vente": montant_total_vente_calc,
        "montant_total_impayees": montant_total_impayees,
        "montant_total_depenses": montant_total_depenses,
        "montant_total_avances": montant_total_avances,
        "montant_decaisse": montant_decaisse,
        "chiffre_affaire": chiffre_affaire,
        "ventes_boissons": ventes_boissons
    }

# Laissez calculer_et_sauvegarder_rapport intact, il est parfait pour l'archivage.
# Il est trop long pour être inclus ici, utilisez la version complète de la réponse précédente.