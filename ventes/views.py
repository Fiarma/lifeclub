# from django.shortcuts import render

# # Create your views here.

# ##################### Details

# from depenses.models import Depense 
# from avances.models import Avance
# from .models import RapportVenteNocturne, DetailVenteBoisson # Modèles du rapport

# from commandes.models import Commande, CommandeItem, Avoir
# from  commandes.forms import CommandeForm
# from boissons.models import Boisson
# from personnel.models import Personnel
# from datetime import timedelta, datetime
# from django.utils import timezone
# from django.shortcuts import render, get_object_or_404
# from django.db.models import Q, Sum, F
# from django.utils import timezone
# from datetime import timedelta, datetime

# # Variables pour le créneau de test 7h00 -> 1h00 du matin suivant (18 heures)
# END_HOUR = 1 
# PERIOD_DURATION_HOURS = 18

# def get_last_completed_sales_period(now=None):
#     """
#     [UTILISÉE POUR L'ARCHIVAGE] Détermine la période de vente qui vient d'être achevée.
#     """
#     if now is None:
#         now = timezone.now()
    
#     if now.hour < END_HOUR:
#         end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0) - timedelta(days=1)
#     else:
#         end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
        
#     start_time = end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
#     return start_time, end_time

# def get_current_sales_period(now=None):
#     """
#     [UTILISÉE POUR L'AFFICHAGE PAR DÉFAUT] Détermine la période de vente EN COURS.
#     """
#     if now is None:
#         now = timezone.now()
    
#     # 1. Déterminer la prochaine fois que la période doit se terminer (01h00 demain)
#     next_end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
    
#     # Si cette heure de fin (01h00 aujourd'hui) est déjà passée, on passe à demain.
#     if next_end_time <= now:
#         next_end_time += timedelta(days=1)
        
#     # 2. Déterminer l'heure de début (18 heures avant)
#     start_time = next_end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
#     return start_time, next_end_time


# # commandes/views.py

# # ... (Après les fonctions get_current_sales_period et calculer_ventes_en_temps_reel)

# def calculer_et_sauvegarder_rapport(start_time, end_time):
#     """
#     Effectue les calculs, sauvegarde le rapport principal et les détails des ventes 
#     (quantité par boisson) s'ils n'existent pas.
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


# # ... (Maintenant, la fonction point_des_ventes peut être définie après celle-ci)
# # commandes/views.py (Fonction point_des_ventes corrigée)

# def point_des_ventes(request):
    
#     # Période pour l'affichage (celle que l'utilisateur veut voir)
#     start_time_current, end_time_current = get_current_sales_period() 
    
#     # Période pour l'archivage (celle qui est complétée)
#     start_time_completed, end_time_completed = get_last_completed_sales_period() 
    
#     date_str = request.GET.get('date') 
    
#     rapport = None
#     start_time_display = start_time_current # Initialisation par défaut
#     end_time_display = end_time_current     # Initialisation par défaut
    
#     # Par défaut, on calcule le rapport en temps réel
#     context_data = calculer_ventes_en_temps_reel(start_time_current, end_time_current)

    
#     if date_str:
#         # --- CAS 1 : Recherche Historique ---
#         try:
#             # Assurez-vous que le format est correct (la requête GET donne YYYY-MM-DDTHH:MM)
#             # Nous devons retirer le 'T' pour que datetime.strptime fonctionne, ou ajuster le format.
#             date_time_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
#             start_time_to_check = timezone.make_aware(date_time_obj)

#             # Récupérer le rapport enregistré
#             rapport = RapportVenteNocturne.objects.prefetch_related('details_boissons').get(start_time=start_time_to_check)
            
#             # Mise à jour des variables d'affichage pour la période HISTORIQUE trouvée
#             start_time_display = rapport.start_time
#             end_time_display = rapport.end_time
            
#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             # Si le rapport n'existe pas ou la date est mal formatée, on reste sur le rapport en cours
#             # context_data conserve la valeur du rapport en temps réel
#             pass
            
#     else:
#         # --- CAS 2 : Affichage par défaut (Rapport en Cours) ---
        
#         # On s'assure que le dernier rapport COMPLÉTÉ est sauvegardé
#         # Cela ne se fait que si l'utilisateur n'a pas spécifiquement demandé une date.
#         calculer_et_sauvegarder_rapport(start_time_completed, end_time_completed)
        
#         # context_data conserve la valeur calculée en temps réel au début de la fonction.


    
#     # Si on a chargé un rapport historique (rapport est un objet), on utilise ses données
#     if rapport:
#         # Remplacer les données calculées en temps réel par les données figées du rapport historique
#         context_data = {
#             "montant_total_vente": rapport.montant_total_vente,
#             "montant_total_impayees": rapport.montant_total_impayees,
#             "montant_total_depenses": rapport.montant_total_depenses,
#             "montant_total_avances": rapport.montant_total_avances,
#             "montant_decaisse": rapport.montant_decaisse,
#             "chiffre_affaire": rapport.chiffre_affaire,
#             "ventes_boissons": rapport.details_boissons.all()
#         }
    
#     # Assemblage du context final
#     context = {
#         "start_time": start_time_display,
#         "end_time": end_time_display,
#         **context_data # Merge les données calculées ou chargées (context_data est toujours défini)
#     }

#     return render(request, "ventes/point_des_ventes.html", context)

# # ----------------------------------------------------------------------------------
# # NOUVELLES FONCTIONS DE CALCUL TEMPORAIRE (pour le rapport en cours)
# # ----------------------------------------------------------------------------------

# def calculer_ventes_detaillees_en_temps_reel(start_time, end_time):
#     """
#     Calcule les agrégations de boisson en temps réel (sans créer de modèle DetailVenteBoisson).
#     """
#     commandes_valides_qs = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     )
#     commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

#     ventes_boissons_raw = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).values(
#         'boisson__id', 
#         'boisson__nom', 
#         'boisson__prix_unitaire'
#     ).annotate(
#         quantite_totale=Sum('quantite'), 
#         montant_total=Sum(F('quantite') * F('boisson__prix_unitaire'))
#     ).order_by('-montant_total')

#     # Convertir le QuerySet annoté en une liste de pseudo-objets DetailVenteBoisson pour le template
#     # (Doit avoir la même structure d'accès que les objets DetailVenteBoisson du modèle)
#     ventes_boissons_list = []
#     for item in ventes_boissons_raw:
#         ventes_boissons_list.append({
#             'boisson': type('Boisson', (object,), {'nom': item['boisson__nom']}), # Pseudo-objet boisson
#             'prix_unitaire_au_moment_vente': item['boisson__prix_unitaire'],
#             'quantite_totale': item['quantite_totale'],
#             'montant_total': item['montant_total'],
#         })
    
#     return ventes_boissons_list

# def calculer_ventes_en_temps_reel(start_time, end_time):
#     """
#     Calcule les chiffres financiers en temps réel pour la période en cours.
#     """
#     commandes_valides_qs = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     )
#     commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

#     # Ventes détaillées pour le template
#     ventes_boissons = calculer_ventes_detaillees_en_temps_reel(start_time, end_time)
    
#     # Montant Total Vente (pour l'agrégation globale)
#     montant_total_vente_calc = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).aggregate(
#         total=Sum(F('quantite') * F('boisson__prix_unitaire'))
#     )['total'] or 0

#     # Autres calculs financiers
#     montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
#     montant_total_depenses = Depense.objects.filter(date__gte=start_time.date(), date__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0
#     montant_total_avances = Avance.objects.filter(date_avance__gte=start_time.date(), date_avance__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0

#     montant_decaisse = montant_total_impayees + montant_total_depenses + montant_total_avances
#     chiffre_affaire = montant_total_vente_calc - montant_decaisse

#     return {
#         "montant_total_vente": montant_total_vente_calc,
#         "montant_total_impayees": montant_total_impayees,
#         "montant_total_depenses": montant_total_depenses,
#         "montant_total_avances": montant_total_avances,
#         "montant_decaisse": montant_decaisse,
#         "chiffre_affaire": chiffre_affaire,
#         "ventes_boissons": ventes_boissons
#     }

# #################################### 03 -10- 2025 #############

# from django.shortcuts import render, get_object_or_404
# from django.db.models import Q, Sum, F, Case, When, DecimalField
# from django.utils import timezone
# from datetime import timedelta, datetime
# from django.shortcuts import render

# # Importations des modèles nécessaires
# from depenses.models import Depense 
# from avances.models import Avance
# from commandes.models import Commande, CommandeItem
# from personnel.models import Personnel
# from .models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne # Tous les modèles du rapport

# # Variables de configuration des périodes
# END_HOUR = 1 
# PERIOD_DURATION_HOURS = 18

# # ----------------------------------------------------------------------------------
# # FONCTIONS DE PÉRIODE
# # ----------------------------------------------------------------------------------

# def get_last_completed_sales_period(now=None):
#     """
#     [UTILISÉE POUR L'ARCHIVAGE] Détermine la période de vente qui vient d'être achevée.
#     """
#     if now is None:
#         now = timezone.now()
    
#     # Si l'heure actuelle est avant l'heure de fin (END_HOUR), le rapport complété était celui d'hier.
#     if now.hour < END_HOUR:
#         end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0) - timedelta(days=1)
#     # Sinon, le rapport complété s'est terminé à END_HOUR aujourd'hui.
#     else:
#         end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
        
#     # Le début est la fin moins la durée de la période
#     start_time = end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
#     return start_time, end_time

# def get_current_sales_period(now=None):
#     """
#     [UTILISÉE POUR L'AFFICHAGE PAR DÉFAUT] Détermine la période de vente EN COURS.
#     """
#     if now is None:
#         now = timezone.now()
    
#     # On détermine la prochaine fois que la période doit se terminer (END_HOUR aujourd'hui ou demain).
#     next_end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
    
#     # Si cette heure de fin est déjà passée, on décale à demain.
#     if next_end_time <= now:
#         next_end_time += timedelta(days=1)
        
#     # L'heure de début est 18 heures avant (PERIOD_DURATION_HOURS)
#     start_time = next_end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
#     return start_time, next_end_time


# # ----------------------------------------------------------------------------------
# # FONCTIONS DE CALCUL TEMPS RÉEL (pour le rapport en cours et pour l'initialisation de l'archive)
# # ----------------------------------------------------------------------------------

# def calculer_ventes_detaillees_en_temps_reel(start_time, end_time):
#     """
#     Calcule les agrégations de boisson en temps réel et prépare les données pour le template.
#     """
#     # Filtre les commandes validées ('payer' ou 'impayee') dans la période
#     commandes_valides_ids = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     ).values_list('id', flat=True)

#     # Agrégation des CommandesItem par boisson
#     ventes_boissons_raw = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).values(
#         'boisson__id', 
#         'boisson__nom', 
#         'boisson__prix_unitaire'
#     ).annotate(
#         quantite_totale=Sum('quantite'), 
#         montant_total=Sum(F('quantite') * F('boisson__prix_unitaire'))
#     ).order_by('-montant_total')

#     # Conversion en liste de pseudo-objets pour une compatibilité facile avec le template (mode historique)
#     ventes_boissons_list = []
#     for item in ventes_boissons_raw:
#         ventes_boissons_list.append({
#             'boisson': type('Boisson', (object,), {'nom': item['boisson__nom']}), # Création d'un faux objet boisson
#             'prix_unitaire_au_moment_vente': item['boisson__prix_unitaire'],
#             'quantite_totale': item['quantite_totale'],
#             'montant_total': item['montant_total'],
#         })
    
#     return ventes_boissons_list

# def calculer_performance_personnel_en_temps_reel(start_time, end_time):
#     """
#     Calcule la performance détaillée des employés pour la période en cours.
#     """
    
#     # 1. Requête principale pour les ventes et impayés agrégés par personnel
#     performance_globale = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     ).values(
#         'personnel__id', 
#         'personnel__nom', 
#         'personnel__prenom' # Noms pour l'affichage en temps réel
#     ).annotate(
#         montant_vendu_total=Sum(F('montant_total')), # Total vendu par cet employé
#         montant_impaye_personnel=Sum(Case(
#             When(statut='impayee', then=F('montant_restant')),
#             default=0,
#             output_field=DecimalField(decimal_places=2)
#         )), # Impayés à son nom
#     ).order_by('-montant_vendu_total')

#     personnel_performance_list = []
    
#     for perf in performance_globale:
#         personnel_id = perf['personnel__id']
        
#         # Filtre secondaire pour obtenir les IDs des commandes spécifiques à cet employé et cette période
#         commandes_de_ce_perso_ids = Commande.objects.filter(
#             date_validation__gte=start_time, 
#             date_validation__lt=end_time,
#             statut__in=['payer', 'impayee'],
#             personnel__id=personnel_id
#         ).values_list('id', flat=True)

#         # 2. Calcul de la quantité totale de toutes les boissons vendues par cet employé
#         quantite_totale_boissons_vendues = CommandeItem.objects.filter(
#             commande_id__in=commandes_de_ce_perso_ids
#         ).aggregate(
#             total_quantite=Sum('quantite')
#         )['total_quantite'] or 0

#         # 3. Détail de chaque boisson vendue (pour l'affichage en temps réel uniquement)
#         detail_ventes_boisson = CommandeItem.objects.filter(
#             commande_id__in=commandes_de_ce_perso_ids
#         ).values(
#             'boisson__nom',
#         ).annotate(
#             quantite=Sum('quantite')
#         ).order_by('boisson__nom')

#         # Formatage des détails de boisson (dictionnaire)
#         details_boissons = {
#             item['boisson__nom']: item['quantite'] 
#             for item in detail_ventes_boisson
#         }
        
#         personnel_performance_list.append({
#             'id': personnel_id,
#             'nom_complet': f"{perf['personnel__prenom']} {perf['personnel__nom']}",
#             'montant_vendu_total': perf['montant_vendu_total'] or 0,
#             'montant_impaye_personnel': perf['montant_impaye_personnel'] or 0,
#             'quantite_totale_boissons_vendues': quantite_totale_boissons_vendues,
#             'details_boissons_vendues': details_boissons, # Utilisé seulement en temps réel
#         })
        
#     return personnel_performance_list


# def calculer_ventes_en_temps_reel(start_time, end_time):
#     """
#     Calcule tous les chiffres financiers et les performances en temps réel pour la période en cours.
#     """
#     # Filtre de base pour les commandes valides
#     commandes_valides_qs = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     )
#     commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

#     # 1. Calculs Détaillés (Boissons et Personnel)
#     ventes_boissons = calculer_ventes_detaillees_en_temps_reel(start_time, end_time)
#     performance_personnel = calculer_performance_personnel_en_temps_reel(start_time, end_time)
    
#     # 2. Calculs Financiers
    
#     # Montant Total Vente (basé sur le total théorique des CommandesItem)
#     montant_total_vente_calc = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).aggregate(
#         total=Sum(F('quantite') * F('boisson__prix_unitaire'))
#     )['total'] or 0

#     montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
#     # Dépenses et Avances sont filtrées par date simple, car les modèles ne contiennent pas d'heure
#     montant_total_depenses = Depense.objects.filter(date__gte=start_time.date(), date__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0
#     montant_total_avances = Avance.objects.filter(date_avance__gte=start_time.date(), date_avance__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0

#     montant_decaisse = montant_total_impayees + montant_total_depenses + montant_total_avances
#     chiffre_affaire = montant_total_vente_calc - montant_decaisse

#     return {
#         "montant_total_vente": montant_total_vente_calc,
#         "montant_total_impayees": montant_total_impayees,
#         "montant_total_depenses": montant_total_depenses,
#         "montant_total_avances": montant_total_avances,
#         "montant_decaisse": montant_decaisse,
#         "chiffre_affaire": chiffre_affaire,
#         "ventes_boissons": ventes_boissons,
#         "performance_personnel": performance_personnel, # Inclus pour la vue
#     }


# # ----------------------------------------------------------------------------------
# # FONCTION D'ARCHIVAGE ET DE SAUVEGARDE
# # ----------------------------------------------------------------------------------

# def calculer_et_sauvegarder_rapport(start_time, end_time):
#     """
#     Effectue les calculs, sauvegarde le rapport principal et les détails associés.
#     """
#     # 1. Tenter de récupérer le rapport existant pour éviter les doublons
#     try:
#         rapport = RapportVenteNocturne.objects.prefetch_related(
#             'details_boissons', 
#             'performance_personnel' 
#         ).get(start_time=start_time)
#         return rapport
#     except RapportVenteNocturne.DoesNotExist:
#         pass # Continuer pour calculer et enregistrer

#     # --- Précalcul : Utiliser le calcul en temps réel pour obtenir tous les chiffres ---
#     # Cela permet de ne pas dupliquer la logique complexe de calculs QuerySet
#     context_data_calc = calculer_ventes_en_temps_reel(start_time, end_time)

#     # --- Étape A : Sauvegarde du rapport principal (RapportVenteNocturne) ---
#     rapport = RapportVenteNocturne.objects.create(
#         start_time=start_time,
#         end_time=end_time,
#         montant_total_vente=context_data_calc['montant_total_vente'],
#         montant_total_impayees=context_data_calc['montant_total_impayees'],
#         montant_total_depenses=context_data_calc['montant_total_depenses'],
#         montant_total_avances=context_data_calc['montant_total_avances'],
#         montant_decaisse=context_data_calc['montant_decaisse'],
#         chiffre_affaire=context_data_calc['chiffre_affaire'],
#     )
    
#     # --- Étape B : Sauvegarde des détails des boissons (DetailVenteBoisson) ---
#     details_a_creer = []
#     for item in context_data_calc['ventes_boissons']:
#         details_a_creer.append(
#             DetailVenteBoisson(
#                 rapport=rapport,
#                 # Le pseudo-objet 'boisson' en temps réel n'a pas l'ID, il faut le retrouver
#                 # NOTE: Cela suppose que la boisson existe toujours et son ID est la clé du dictionnaire temporaire
#                 boisson_id=CommandeItem.objects.filter(
#                     commande__date_validation__gte=start_time,
#                     commande__date_validation__lt=end_time,
#                     boisson__nom=item['boisson'].nom # Filtrer par nom pour retrouver l'ID (moins optimal mais fonctionnel)
#                 ).first().boisson_id if CommandeItem.objects.filter(
#                     commande__date_validation__gte=start_time,
#                     commande__date_validation__lt=end_time,
#                     boisson__nom=item['boisson'].nom
#                 ).exists() else None,
#                 quantite_totale=item['quantite_totale'],
#                 montant_total=item['montant_total'],
#                 prix_unitaire_au_moment_vente=item['prix_unitaire_au_moment_vente']
#             )
#         )
#     # Filtrer les détails qui n'ont pas d'ID (si une boisson a été supprimée entre-temps)
#     details_a_creer = [d for d in details_a_creer if d.boisson_id is not None]
#     DetailVenteBoisson.objects.bulk_create(details_a_creer)

#     # --- Étape C : Sauvegarde de la Performance du Personnel (PerformancePersonnelNocturne) ---
#     performances_a_creer = []
#     for perf in context_data_calc['performance_personnel']:
#         # Seuls les totaux sont archivés
#         performances_a_creer.append(
#             PerformancePersonnelNocturne(
#                 rapport=rapport,
#                 personnel_id=perf['id'], 
#                 montant_vendu_total=perf['montant_vendu_total'],
#                 montant_impaye_personnel=perf['montant_impaye_personnel'],
#                 quantite_totale_boissons_vendues=perf['quantite_totale_boissons_vendues']
#             )
#         )
#     PerformancePersonnelNocturne.objects.bulk_create(performances_a_creer)

#     return rapport


# # ----------------------------------------------------------------------------------
# # VUE PRINCIPALE
# # ----------------------------------------------------------------------------------

# def point_des_ventes(request):
    
#     # Détermination des périodes
#     start_time_current, end_time_current = get_current_sales_period() # Période en cours
#     start_time_completed, end_time_completed = get_last_completed_sales_period() # Période complétée
    
#     date_str = request.GET.get('date') 
    
#     rapport = None
#     start_time_display = start_time_current # Affichage par défaut: période en cours
#     end_time_display = end_time_current     # Affichage par défaut: période en cours
    
#     # Par défaut, on calcule le rapport en temps réel
#     context_data = calculer_ventes_en_temps_reel(start_time_current, end_time_current)

    
#     if date_str:
#         # --- CAS 1 : Recherche Historique (avec paramètre 'date') ---
#         try:
#             # Conversion de la chaîne de date du formulaire (ex: 2025-10-02T19:00)
#             date_time_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
#             start_time_to_check = timezone.make_aware(date_time_obj)

#             # Tenter de charger le rapport enregistré (inclut les données de performance)
#             rapport = RapportVenteNocturne.objects.prefetch_related(
#                 'details_boissons', 
#                 'performance_personnel'
#             ).get(start_time=start_time_to_check)
            
#             # Mise à jour des variables d'affichage pour la période HISTORIQUE
#             start_time_display = rapport.start_time
#             end_time_display = rapport.end_time
            
#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             # Si rapport non trouvé ou format incorrect, un message d'erreur pourrait être ajouté ici
#             # Mais par défaut, on reste sur les données du rapport en temps réel déjà calculées.
#             pass
            
#     else:
#         # --- CAS 2 : Affichage par défaut (Temps Réel) ---
        
#         # On déclenche l'archivage du dernier rapport COMPLÉTÉ
#         calculer_et_sauvegarder_rapport(start_time_completed, end_time_completed)
        
#         # context_data reste le calcul en temps réel fait au début de la fonction.


#     # Si un rapport historique a été chargé, on écrase les données du temps réel
#     if rapport:
#         # Remplacer les données calculées en temps réel par les données figées du rapport historique
#         context_data = {
#             "montant_total_vente": rapport.montant_total_vente,
#             "montant_total_impayees": rapport.montant_total_impayees,
#             "montant_total_depenses": rapport.montant_total_depenses,
#             "montant_total_avances": rapport.montant_total_avances,
#             "montant_decaisse": rapport.montant_decaisse,
#             "chiffre_affaire": rapport.chiffre_affaire,
#             "ventes_boissons": rapport.details_boissons.all(),
#             "performance_personnel": rapport.performance_personnel.all() # Données archivées
#         }
    
#     # Assemblage du context final
#     context = {
#         "start_time": start_time_display,
#         "end_time": end_time_display,
#         **context_data # Fusionne les données financières/performances
#     }

#     # Assurez-vous que le chemin du template est correct
#     return render(request, "ventes/point_des_ventes.html", context)

############################# Apres ajout du  champ pour prendre en compte les avances du  personnel ###########

# from django.shortcuts import render, get_object_or_404
# from django.db.models import Q, Sum, F, Case, When, DecimalField
# from django.utils import timezone
# from datetime import timedelta, datetime
# from django.shortcuts import render

# # Importations des modèles nécessaires
# from depenses.models import Depense 
# from avances.models import Avance # Nécessaire pour les avances
# from commandes.models import Commande, CommandeItem
# from personnel.models import Personnel
# from .models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne # Tous les modèles du rapport

# # Variables de configuration des périodes
# END_HOUR = 1 
# PERIOD_DURATION_HOURS = 18

# # ----------------------------------------------------------------------------------
# # FONCTIONS DE PÉRIODE (Inchangées)
# # ----------------------------------------------------------------------------------

# def get_last_completed_sales_period(now=None):
#     """
#     [UTILISÉE POUR L'ARCHIVAGE] Détermine la période de vente qui vient d'être achevée.
#     """
#     if now is None:
#         now = timezone.now()
    
#     # Logique de détermination de l'heure de fin
#     if now.hour < END_HOUR:
#         end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0) - timedelta(days=1)
#     else:
#         end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
        
#     # Calcul de l'heure de début
#     start_time = end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
#     return start_time, end_time

# def get_current_sales_period(now=None):
#     """
#     [UTILISÉE POUR L'AFFICHAGE PAR DÉFAUT] Détermine la période de vente EN COURS.
#     """
#     if now is None:
#         now = timezone.now()
    
#     # Détermination de la prochaine heure de fin (END_HOUR)
#     next_end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
    
#     # Si déjà passée, on décale à demain
#     if next_end_time <= now:
#         next_end_time += timedelta(days=1)
        
#     # Calcul de l'heure de début
#     start_time = next_end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
#     return start_time, next_end_time


# # ----------------------------------------------------------------------------------
# # FONCTIONS DE CALCUL TEMPS RÉEL
# # ----------------------------------------------------------------------------------

# def calculer_ventes_detaillees_en_temps_reel(start_time, end_time):
#     """
#     Calcule les agrégations de boisson en temps réel et prépare les données pour le template.
#     """
#     # Filtre des commandes validées dans la période
#     commandes_valides_ids = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     ).values_list('id', flat=True)

#     # Agrégation des CommandesItem par boisson
#     ventes_boissons_raw = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).values(
#         'boisson__id', 
#         'boisson__nom', 
#         'boisson__prix_unitaire'
#     ).annotate(
#         quantite_totale=Sum('quantite'), 
#         montant_total=Sum(F('quantite') * F('boisson__prix_unitaire'))
#     ).order_by('-montant_total')

#     # Conversion en liste de pseudo-objets pour le template
#     ventes_boissons_list = []
#     for item in ventes_boissons_raw:
#         ventes_boissons_list.append({
#             'boisson': type('Boisson', (object,), {'nom': item['boisson__nom']}), # Faux objet pour compatibilité
#             'prix_unitaire_au_moment_vente': item['boisson__prix_unitaire'],
#             'quantite_totale': item['quantite_totale'],
#             'montant_total': item['montant_total'],
#         })
    
#     return ventes_boissons_list

# def calculer_performance_personnel_en_temps_reel(start_time, end_time):
#     """
#     Calcule la performance détaillée des employés, y compris les avances prises, pour la période en cours.
#     """
    
#     # Dictionnaire pour stocker toutes les performances et avances, clé = personnel_id
#     performance_data = {} 

#     # --- ÉTAPE 1 : Calcul des VENTES et IMPAYÉS (Uniquement pour ceux qui ont vendu) ---
    
#     # Requête pour les totaux de vente et d'impayés
#     performance_globale_ventes = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     ).values(
#         'personnel__id', 
#         'personnel__nom', 
#         'personnel__prenom' 
#     ).annotate(
#         montant_vendu_total=Sum(F('montant_total')),
#         montant_impaye_personnel=Sum(Case(
#             When(statut='impayee', then=F('montant_restant')),
#             default=0,
#             output_field=DecimalField(decimal_places=2)
#         )),
#     )

#     # Remplissage initial du dictionnaire avec les données de vente
#     for perf in performance_globale_ventes:
#         personnel_id = perf['personnel__id']
        
#         # Filtre secondaire pour calculer la quantité totale de boissons vendues par cet employé
#         commandes_de_ce_perso_ids = Commande.objects.filter(
#             date_validation__gte=start_time, 
#             date_validation__lt=end_time,
#             statut__in=['payer', 'impayee'],
#             personnel__id=personnel_id
#         ).values_list('id', flat=True)

#         quantite_totale_boissons_vendues = CommandeItem.objects.filter(
#             commande_id__in=commandes_de_ce_perso_ids
#         ).aggregate(
#             total_quantite=Sum('quantite')
#         )['total_quantite'] or 0

#         # Détail de chaque boisson vendue (pour l'affichage en temps réel uniquement)
#         detail_ventes_boisson = CommandeItem.objects.filter(
#             commande_id__in=commandes_de_ce_perso_ids
#         ).values('boisson__nom').annotate(quantite=Sum('quantite'))

#         details_boissons = {
#             item['boisson__nom']: item['quantite'] 
#             for item in detail_ventes_boisson
#         }
        
#         performance_data[personnel_id] = {
#             'id': personnel_id,
#             'nom_complet': f"{perf['personnel__prenom']} {perf['personnel__nom']}",
#             'montant_vendu_total': perf['montant_vendu_total'] or 0,
#             'montant_impaye_personnel': perf['montant_impaye_personnel'] or 0,
#             'quantite_totale_boissons_vendues': quantite_totale_boissons_vendues,
#             'details_boissons_vendues': details_boissons,
#             'montant_total_avances_personnel': 0, # Initialisation de l'avance à zéro
#         }
        
#     # --- ÉTAPE 2 : Calcul des AVANCES (Pour tout le personnel ayant pris une avance) ---
    
#     # Requête pour la somme des avances filtrée par date simple
#     avances_personnel = Avance.objects.filter(
#         date_avance__gte=start_time.date(), 
#         date_avance__lte=end_time.date() 
#     ).values(
#         'personnel__id', 
#         'personnel__nom', 
#         'personnel__prenom' # On récupère les noms pour les employés sans vente
#     ).annotate(
#         montant_avance=Sum('montant')
#     )
    
#     # Fusion des données d'avance dans le dictionnaire
#     for avance in avances_personnel:
#         personnel_id = avance['personnel__id']
#         montant_total_avances = avance['montant_avance'] or 0
        
#         if personnel_id in performance_data:
#             # Le personnel a vendu -> mise à jour de l'avance
#             performance_data[personnel_id]['montant_total_avances_personnel'] = montant_total_avances
#         else:
#             # Le personnel n'a PAS vendu (ex: DJ), mais a pris une avance -> création de l'entrée
#             performance_data[personnel_id] = {
#                 'id': personnel_id,
#                 'nom_complet': f"{avance['personnel__prenom']} {avance['personnel__nom']}",
#                 'montant_vendu_total': 0,
#                 'montant_impaye_personnel': 0,
#                 'quantite_totale_boissons_vendues': 0,
#                 'details_boissons_vendues': {},
#                 'montant_total_avances_personnel': montant_total_avances,
#             }

#     # --- ÉTAPE 3 : Finalisation et Tri ---
    
#     # Conversion du dictionnaire en liste et tri par montant de vente (pour l'affichage)
#     personnel_performance_list = sorted(
#         performance_data.values(), 
#         key=lambda x: x['montant_vendu_total'], 
#         reverse=True
#     )
    
#     return personnel_performance_list




# def calculer_ventes_en_temps_reel(start_time, end_time):
#     """
#     Calcule tous les chiffres financiers et les performances en temps réel pour la période en cours.
#     """
#     # Filtre de base pour les commandes valides
#     commandes_valides_qs = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     )
#     commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

#     # 1. Calculs Détaillés (Boissons et Personnel)
#     ventes_boissons = calculer_ventes_detaillees_en_temps_reel(start_time, end_time)
#     performance_personnel = calculer_performance_personnel_en_temps_reel(start_time, end_time) # MAINTENANT INCLUT LES AVANCES
    
#     # 2. Calculs Financiers (agrégations globales)
    
#     # Montant Total Vente
#     montant_total_vente_calc = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).aggregate(
#         total=Sum(F('quantite') * F('boisson__prix_unitaire'))
#     )['total'] or 0

#     # Montant total des impayés
#     montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
#     # Dépenses et Avances (globales) filtrées par date
#     montant_total_depenses = Depense.objects.filter(date__gte=start_time.date(), date__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0
#     montant_total_avances = Avance.objects.filter(date_avance__gte=start_time.date(), date_avance__lte=end_time.date()).aggregate(total=Sum('montant'))['total'] or 0

#     # Calcul du décaissement et du chiffre d'affaires
#     montant_decaisse = montant_total_impayees + montant_total_depenses + montant_total_avances
#     chiffre_affaire = montant_total_vente_calc - montant_decaisse

#     return {
#         "montant_total_vente": montant_total_vente_calc,
#         "montant_total_impayees": montant_total_impayees,
#         "montant_total_depenses": montant_total_depenses,
#         "montant_total_avances": montant_total_avances,
#         "montant_decaisse": montant_decaisse,
#         "chiffre_affaire": chiffre_affaire,
#         "ventes_boissons": ventes_boissons,
#         "performance_personnel": performance_personnel, 
#     }


# # ----------------------------------------------------------------------------------
# # FONCTION D'ARCHIVAGE ET DE SAUVEGARDE
# # ----------------------------------------------------------------------------------

# def calculer_et_sauvegarder_rapport(start_time, end_time):
#     """
#     Effectue les calculs, sauvegarde le rapport principal et les détails associés.
#     """
#     # 1. Tenter de récupérer le rapport existant pour éviter les doublons
#     try:
#         rapport = RapportVenteNocturne.objects.prefetch_related(
#             'details_boissons', 
#             'performance_personnel' 
#         ).get(start_time=start_time)
#         return rapport
#     except RapportVenteNocturne.DoesNotExist:
#         pass # Continuer pour calculer et enregistrer

#     # Précalcul des données en temps réel (incluant les performances et les avances)
#     context_data_calc = calculer_ventes_en_temps_reel(start_time, end_time)

#     # --- Étape A : Sauvegarde du rapport principal (RapportVenteNocturne) ---
#     rapport = RapportVenteNocturne.objects.create(
#         start_time=start_time,
#         end_time=end_time,
#         montant_total_vente=context_data_calc['montant_total_vente'],
#         montant_total_impayees=context_data_calc['montant_total_impayees'],
#         montant_total_depenses=context_data_calc['montant_total_depenses'],
#         montant_total_avances=context_data_calc['montant_total_avances'],
#         montant_decaisse=context_data_calc['montant_decaisse'],
#         chiffre_affaire=context_data_calc['chiffre_affaire'],
#     )
    
#     # --- Étape B : Sauvegarde des détails des boissons (DetailVenteBoisson) ---
#     details_a_creer = []
#     for item in context_data_calc['ventes_boissons']:
#         # Trouver l'ID de la boisson dans la BD (simplification/contournement de l'objet temporaire)
#         boisson_id_to_use = None
#         commande_item = CommandeItem.objects.filter(
#             commande__date_validation__gte=start_time,
#             commande__date_validation__lt=end_time,
#             boisson__nom=item['boisson'].nom
#         ).first()
#         if commande_item:
#             boisson_id_to_use = commande_item.boisson_id
            
#         details_a_creer.append(
#             DetailVenteBoisson(
#                 rapport=rapport,
#                 boisson_id=boisson_id_to_use,
#                 quantite_totale=item['quantite_totale'],
#                 montant_total=item['montant_total'],
#                 prix_unitaire_au_moment_vente=item['prix_unitaire_au_moment_vente']
#             )
#         )
#     # Filtrer et créer les détails
#     details_a_creer = [d for d in details_a_creer if d.boisson_id is not None]
#     DetailVenteBoisson.objects.bulk_create(details_a_creer)

#     # --- Étape C : Sauvegarde de la Performance du Personnel (PerformancePersonnelNocturne) ---
#     performances_a_creer = []
#     for perf in context_data_calc['performance_personnel']:
#         # Archivage, y compris le nouveau champ d'avance
#         performances_a_creer.append(
#             PerformancePersonnelNocturne(
#                 rapport=rapport,
#                 personnel_id=perf['id'], 
#                 montant_vendu_total=perf['montant_vendu_total'],
#                 montant_impaye_personnel=perf['montant_impaye_personnel'],
#                 quantite_totale_boissons_vendues=perf['quantite_totale_boissons_vendues'],
#                 montant_total_avances_personnel=perf['montant_total_avances_personnel'] # ENREGISTREMENT DE L'AVANCE
#             )
#         )
#     PerformancePersonnelNocturne.objects.bulk_create(performances_a_creer)

#     return rapport


# # ----------------------------------------------------------------------------------
# # VUE PRINCIPALE
# # ----------------------------------------------------------------------------------

# def point_des_ventes(request):
    
#     # Détermination des périodes
#     start_time_current, end_time_current = get_current_sales_period() 
#     start_time_completed, end_time_completed = get_last_completed_sales_period() 
    
#     date_str = request.GET.get('date') 
    
#     rapport = None
#     start_time_display = start_time_current 
#     end_time_display = end_time_current     
    
#     # Calcul par défaut en temps réel
#     context_data = calculer_ventes_en_temps_reel(start_time_current, end_time_current)

    
#     if date_str:
#         # --- CAS 1 : Recherche Historique ---
#         try:
#             # Conversion et ajustement du fuseau horaire
#             date_time_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
#             start_time_to_check = timezone.make_aware(date_time_obj)

#             # Charger le rapport archivé
#             rapport = RapportVenteNocturne.objects.prefetch_related(
#                 'details_boissons', 
#                 'performance_personnel'
#             ).get(start_time=start_time_to_check)
            
#             # Mise à jour des variables d'affichage
#             start_time_display = rapport.start_time
#             end_time_display = rapport.end_time
            
#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             pass # Reste sur les données en temps réel si historique non trouvé
            
#     else:
#         # --- CAS 2 : Affichage par défaut (Temps Réel) ---
        
#         # Déclenchement de l'archivage du dernier rapport complété
#         calculer_et_sauvegarder_rapport(start_time_completed, end_time_completed)
        
#         # context_data est déjà le calcul en temps réel.


#     # Si un rapport historique est chargé, on remplace les données temps réel par l'archive
#     if rapport:
#         # Remplacement des données avec l'archive
#         context_data = {
#             "montant_total_vente": rapport.montant_total_vente,
#             "montant_total_impayees": rapport.montant_total_impayees,
#             "montant_total_depenses": rapport.montant_total_depenses,
#             "montant_total_avances": rapport.montant_total_avances,
#             "montant_decaisse": rapport.montant_decaisse,
#             "chiffre_affaire": rapport.chiffre_affaire,
#             "ventes_boissons": rapport.details_boissons.all(),
#             "performance_personnel": rapport.performance_personnel.all() # Données archivées
#         }
    
#     # Assemblage du context final
#     context = {
#         "start_time": start_time_display,
#         "end_time": end_time_display,
#         **context_data 
#     }

#     return render(request, "ventes/point_des_ventes.html", context)



################# 04 -10- 2025 ##################

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Sum, F, Case, When, DecimalField
from django.utils import timezone
from datetime import timedelta, datetime
from django.shortcuts import render

# Importations des modèles nécessaires
from depenses.models import Depense 
from avances.models import Avance # Nécessaire pour les avances
from commandes.models import Commande, CommandeItem
from personnel.models import Personnel
from .models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne # Tous les modèles du rapport

# Variables de configuration des périodes
END_HOUR = 1 
PERIOD_DURATION_HOURS = 18

# ----------------------------------------------------------------------------------
# FONCTIONS DE PÉRIODE (Inchangées)
# ----------------------------------------------------------------------------------

def get_last_completed_sales_period(now=None):
    # ... (inchangé)
    if now is None:
        now = timezone.now()
    
    if now.hour < END_HOUR:
        end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
        
    start_time = end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
    return start_time, end_time

def get_current_sales_period(now=None):
    # ... (inchangé)
    if now is None:
        now = timezone.now()
    
    next_end_time = now.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
    
    if next_end_time <= now:
        next_end_time += timedelta(days=1)
        
    start_time = next_end_time - timedelta(hours=PERIOD_DURATION_HOURS)
    
    return start_time, next_end_time


# ----------------------------------------------------------------------------------
# FONCTIONS DE CALCUL TEMPS RÉEL
# ----------------------------------------------------------------------------------

def calculer_ventes_detaillees_en_temps_reel(start_time, end_time):
    # ... (inchangé)
    commandes_valides_ids = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    ).values_list('id', flat=True)

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

    ventes_boissons_list = []
    for item in ventes_boissons_raw:
        ventes_boissons_list.append({
            'boisson': type('Boisson', (object,), {'nom': item['boisson__nom']}),
            'prix_unitaire_au_moment_vente': item['boisson__prix_unitaire'],
            'quantite_totale': item['quantite_totale'],
            'montant_total': item['montant_total'],
        })
    
    return ventes_boissons_list

def calculer_performance_personnel_en_temps_reel(start_time, end_time):
    """
    CORRIGÉ : Assure que l'objet Personnel est toujours attaché pour l'affichage du rôle.
    """
    
    performance_data = {} 

    # 1. Identifier tous les IDs du personnel concerné (vente ou avance)
    venteurs_ids = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    ).values_list('personnel__id', flat=True)
    
    avanceurs_ids = Avance.objects.filter(
        date_avance__gte=start_time.date(), 
        date_avance__lte=end_time.date() 
    ).values_list('personnel__id', flat=True)
    
    all_personnel_ids = list(set(list(venteurs_ids) + list(avanceurs_ids)))
    
    # 2. Récupérer toutes les instances Personnel en une seule requête pour le rôle
    personnel_instances = {p.id: p for p in Personnel.objects.filter(id__in=all_personnel_ids)}

    # 3. Initialisation des données pour chaque employé
    for personnel_id, instance in personnel_instances.items():
        performance_data[personnel_id] = {
            'id': personnel_id,
            'nom_complet': f"{instance.prenom} {instance.nom}",
            'montant_vendu_total': 0,
            'montant_impaye_personnel': 0,
            'quantite_totale_boissons_vendues': 0,
            'details_boissons_vendues': {}, # Détail pour le temps réel
            'montant_total_avances_personnel': 0,
            'personnel': instance, # <--- AJOUT DE L'INSTANCE PERSONNEL
        }

    # 4. Calcul des VENTES et IMPAYÉS (Mise à jour des entrées)
    performance_globale_ventes = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    ).values('personnel__id').annotate(
        montant_vendu_total=Sum(F('montant_total')),
        montant_impaye_personnel=Sum(Case(
            When(statut='impayee', then=F('montant_restant')),
            default=0,
            output_field=DecimalField(decimal_places=2)
        )),
    )

    for perf in performance_globale_ventes:
        personnel_id = perf['personnel__id']
        
        # Calcul du détail des ventes par boisson
        commandes_de_ce_perso_ids = Commande.objects.filter(
            date_validation__gte=start_time, 
            date_validation__lt=end_time,
            statut__in=['payer', 'impayee'],
            personnel__id=personnel_id
        ).values_list('id', flat=True)

        detail_ventes_boisson = CommandeItem.objects.filter(
            commande_id__in=commandes_de_ce_perso_ids
        ).values('boisson__nom').annotate(quantite=Sum('quantite'))

        details_boissons = {
            item['boisson__nom']: item['quantite'] 
            for item in detail_ventes_boisson
        }
        quantite_totale_boissons_vendues = sum(details_boissons.values())
        
        if personnel_id in performance_data:
            performance_data[personnel_id].update({
                'montant_vendu_total': perf['montant_vendu_total'] or 0,
                'montant_impaye_personnel': perf['montant_impaye_personnel'] or 0,
                'quantite_totale_boissons_vendues': quantite_totale_boissons_vendues,
                'details_boissons_vendues': details_boissons,
            })
        
    # 5. Calcul des AVANCES (Mise à jour des entrées)
    avances_personnel = Avance.objects.filter(
        date_avance__gte=start_time.date(), 
        date_avance__lte=end_time.date() 
    ).values('personnel__id').annotate(montant_avance=Sum('montant'))
    
    for avance in avances_personnel:
        personnel_id = avance['personnel__id']
        if personnel_id in performance_data:
            performance_data[personnel_id]['montant_total_avances_personnel'] = avance['montant_avance'] or 0

    # 6. Finalisation et Tri (filtrage de ceux qui ont une activité)
    personnel_performance_list = sorted(
        [p for p in performance_data.values() if p['montant_vendu_total'] > 0 or p['montant_total_avances_personnel'] > 0], 
        key=lambda x: x['montant_vendu_total'], 
        reverse=True
    )
    
    return personnel_performance_list


def calculer_ventes_en_temps_reel(start_time, end_time):
    # ... (inchangé, sauf l'appel à la fonction de performance) ...
    commandes_valides_qs = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    )
    commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

    ventes_boissons = calculer_ventes_detaillees_en_temps_reel(start_time, end_time)
    performance_personnel = calculer_performance_personnel_en_temps_reel(start_time, end_time) 
    
    montant_total_vente_calc = CommandeItem.objects.filter(
        commande_id__in=commandes_valides_ids
    ).aggregate(
        total=Sum(F('quantite') * F('boisson__prix_unitaire'))
    )['total'] or 0

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
        "ventes_boissons": ventes_boissons,
        "performance_personnel": performance_personnel, 
    }


# ----------------------------------------------------------------------------------
# FONCTION D'ARCHIVAGE ET DE SAUVEGARDE
# ----------------------------------------------------------------------------------

def calculer_et_sauvegarder_rapport(start_time, end_time):
    """
    CORRIGÉ : Sauvegarde le détail des boissons dans le champ 'details_boissons_vendues_archive'.
    """
    try:
        rapport = RapportVenteNocturne.objects.prefetch_related(
            'details_boissons', 
            'performance_personnel' 
        ).get(start_time=start_time)
        return rapport
    except RapportVenteNocturne.DoesNotExist:
        pass 

    context_data_calc = calculer_ventes_en_temps_reel(start_time, end_time)

    # --- Étape A : Sauvegarde du rapport principal ---
    rapport = RapportVenteNocturne.objects.create(
        start_time=start_time,
        end_time=end_time,
        montant_total_vente=context_data_calc['montant_total_vente'],
        montant_total_impayees=context_data_calc['montant_total_impayees'],
        montant_total_depenses=context_data_calc['montant_total_depenses'],
        montant_total_avances=context_data_calc['montant_total_avances'],
        montant_decaisse=context_data_calc['montant_decaisse'],
        chiffre_affaire=context_data_calc['chiffre_affaire'],
    )
    
    # ... (Étape B : Sauvegarde des détails des boissons) ...
    # (Le code est omis ici pour la concision mais il est supposé être fonctionnel)
    details_a_creer = []
    for item in context_data_calc['ventes_boissons']:
        boisson_id_to_use = None
        commande_item = CommandeItem.objects.filter(
            commande__date_validation__gte=start_time,
            commande__date_validation__lt=end_time,
            boisson__nom=item['boisson'].nom
        ).first()
        if commande_item:
            boisson_id_to_use = commande_item.boisson_id
            
        details_a_creer.append(
            DetailVenteBoisson(
                rapport=rapport,
                boisson_id=boisson_id_to_use,
                quantite_totale=item['quantite_totale'],
                montant_total=item['montant_total'],
                prix_unitaire_au_moment_vente=item['prix_unitaire_au_moment_vente']
            )
        )
    details_a_creer = [d for d in details_a_creer if d.boisson_id is not None]
    DetailVenteBoisson.objects.bulk_create(details_a_creer)


    # --- Étape C : Sauvegarde de la Performance du Personnel (MISE À JOUR) ---
    performances_a_creer = []
    for perf in context_data_calc['performance_personnel']:
        performances_a_creer.append(
            PerformancePersonnelNocturne(
                rapport=rapport,
                personnel_id=perf['id'], 
                montant_vendu_total=perf['montant_vendu_total'],
                montant_impaye_personnel=perf['montant_impaye_personnel'],
                quantite_totale_boissons_vendues=perf['quantite_totale_boissons_vendues'],
                montant_total_avances_personnel=perf['montant_total_avances_personnel'],
                # NOUVEAU : Sauvegarde du détail des ventes (JSONField)
                details_boissons_vendues_archive=perf['details_boissons_vendues']
            )
        )
    PerformancePersonnelNocturne.objects.bulk_create(performances_a_creer)

    return rapport


# ----------------------------------------------------------------------------------
# VUE PRINCIPALE
# ----------------------------------------------------------------------------------

def point_des_ventes(request):
    
    # ... (Détermination des périodes inchangée) ...
    start_time_current, end_time_current = get_current_sales_period() 
    start_time_completed, end_time_completed = get_last_completed_sales_period() 
    
    date_str = request.GET.get('date') 
    rapport = None
    start_time_display = start_time_current 
    end_time_display = end_time_current     
    
    context_data = calculer_ventes_en_temps_reel(start_time_current, end_time_current)
    
    if date_str:
        # --- CAS 1 : Recherche Historique ---
        try:
            date_time_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            start_time_to_check = timezone.make_aware(date_time_obj)

            # Ajout du prefetch_related pour personnel pour le rôle
            rapport = RapportVenteNocturne.objects.prefetch_related(
                'details_boissons', 
                'performance_personnel',
                'performance_personnel__personnel' # AJOUTÉ : Charge l'objet Personnel pour le rôle
            ).get(start_time=start_time_to_check)
            
            start_time_display = rapport.start_time
            end_time_display = rapport.end_time
            
        except (RapportVenteNocturne.DoesNotExist, ValueError):
            pass 
            
    else:
        # --- CAS 2 : Affichage par défaut (Temps Réel) ---
        calculer_et_sauvegarder_rapport(start_time_completed, end_time_completed)


    if rapport:
        # Remplacement des données avec l'archive
        context_data = {
            "montant_total_vente": rapport.montant_total_vente,
            "montant_total_impayees": rapport.montant_total_impayees,
            "montant_total_depenses": rapport.montant_total_depenses,
            "montant_total_avances": rapport.montant_total_avances,
            "montant_decaisse": rapport.montant_decaisse,
            "chiffre_affaire": rapport.chiffre_affaire,
            "ventes_boissons": rapport.details_boissons.all(),
            "performance_personnel": rapport.performance_personnel.all() # Données archivées
        }
    
    context = {
        "start_time": start_time_display,
        "end_time": end_time_display,
        **context_data 
    }

    return render(request, "ventes/point_des_ventes.html", context)