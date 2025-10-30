
# ##################################

# from django.shortcuts import render, get_object_or_404, redirect
# from django.db.models import Q, Sum, F, Case, When, DecimalField
# from django.utils import timezone
# from datetime import timedelta, datetime
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.contrib import messages

# # Importations des modèles nécessaires
# from depenses.models import Depense 
# from avances.models import Avance
# from commandes.models import Commande, CommandeItem
# from personnel.models import Personnel
# from .models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne


# # ----------------------------------------------------------------------------------
# # FONCTIONS DE CALCUL TEMPS RÉEL
# # ----------------------------------------------------------------------------------

# def calculer_ventes_detaillees_en_temps_reel(start_time, end_time):
#     # Les commandes sont filtrées par la session active
#     commandes_valides_ids = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     ).values_list('id', flat=True)

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

#     ventes_boissons_list = []
#     for item in ventes_boissons_raw:
#         # Création d'un objet "boisson" factice pour compatibilité avec le template
#         boisson_obj = type('Boisson', (object,), {'nom': item['boisson__nom'], 'id': item['boisson__id']})
#         ventes_boissons_list.append({
#             'boisson': boisson_obj,
#             'prix_unitaire_au_moment_vente': item['boisson__prix_unitaire'],
#             'quantite_totale': item['quantite_totale'],
#             'montant_total': item['montant_total'],
#         })
    
#     return ventes_boissons_list


# def calculer_performance_personnel_en_temps_reel(start_time, end_time):
    
#     performance_data = {} 

#     # 1. Identifier tous les IDs du personnel concerné (vente ou avance)
#     venteurs_ids = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     ).values_list('personnel__id', flat=True)
    
#     # Avances filtrées par la session
#     avanceurs_ids = Avance.objects.filter(
#         date_avance__gte=start_time, 
#         date_avance__lt=end_time
#     ).values_list('personnel__id', flat=True)
    
#     # Utilisation correcte de 'venteurs_ids'
#     all_personnel_ids = list(set([id for id in venteurs_ids if id is not None] + [id for id in avanceurs_ids if id is not None]))
    
#     # 2. Récupérer toutes les instances Personnel en une seule requête pour le rôle
#     personnel_instances = {p.id: p for p in Personnel.objects.filter(id__in=all_personnel_ids)}

#     # 3. Initialisation des données pour chaque employé
#     for personnel_id, instance in personnel_instances.items():
#         performance_data[personnel_id] = {
#             'id': personnel_id,
#             'nom_complet': f"{instance.prenom} {instance.nom}",
#             'montant_vendu_total': 0,
#             'montant_impaye_personnel': 0,
#             'quantite_totale_boissons_vendues': 0,
#             'details_boissons_vendues': {}, 
#             'montant_total_avances_personnel': 0,
#             'personnel': instance,
#         }

#     # 4. Calcul des VENTES et IMPAYÉS
#     performance_globale_ventes = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee'],
#         personnel__id__in=all_personnel_ids
#     ).values('personnel__id').annotate(
#         montant_vendu_total=Sum(F('montant_total')),
#         montant_impaye_personnel=Sum(Case(
#             When(statut='impayee', then=F('montant_restant')),
#             default=0,
#             output_field=DecimalField(decimal_places=2)
#         )),
#     )

#     for perf in performance_globale_ventes:
#         personnel_id = perf['personnel__id']
        
#         commandes_de_ce_perso_ids = Commande.objects.filter(
#             date_validation__gte=start_time, 
#             date_validation__lt=end_time,
#             statut__in=['payer', 'impayee'],
#             personnel__id=personnel_id
#         ).values_list('id', flat=True)

#         detail_ventes_boisson = CommandeItem.objects.filter(
#             commande_id__in=commandes_de_ce_perso_ids
#         ).values('boisson__nom').annotate(quantite=Sum('quantite'))

#         details_boissons = {
#             item['boisson__nom']: item['quantite'] 
#             for item in detail_ventes_boisson
#         }
#         quantite_totale_boissons_vendues = sum(details_boissons.values())
        
#         if personnel_id in performance_data:
#             performance_data[personnel_id].update({
#                 'montant_vendu_total': perf['montant_vendu_total'] or 0,
#                 'montant_impaye_personnel': perf['montant_impaye_personnel'] or 0,
#                 'quantite_totale_boissons_vendues': quantite_totale_boissons_vendues,
#                 'details_boissons_vendues': details_boissons,
#             })
        
#     # 5. Calcul des AVANCES
#     avances_personnel = Avance.objects.filter(
#         date_avance__gte=start_time, 
#         date_avance__lt=end_time
#     ).values('personnel__id').annotate(montant_avance=Sum('montant'))
    
#     for avance in avances_personnel:
#         personnel_id = avance['personnel__id']
#         if personnel_id in performance_data:
#             performance_data[personnel_id]['montant_total_avances_personnel'] = avance['montant_avance'] or 0

#     # 6. Finalisation et Tri
#     personnel_performance_list = sorted(
#         performance_data.values(), 
#         key=lambda x: x['montant_vendu_total'], 
#         reverse=True
#     )
    
#     return personnel_performance_list


# def calculer_ventes_en_temps_reel(start_time, end_time):
    
#     commandes_valides_qs = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     )
#     commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

#     ventes_boissons = calculer_ventes_detaillees_en_temps_reel(start_time, end_time)
#     performance_personnel = calculer_performance_personnel_en_temps_reel(start_time, end_time) 
    
#     montant_total_vente_calc = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).aggregate(
#         total=Sum(F('quantite') * F('boisson__prix_unitaire'))
#     )['total'] or 0

#     montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
#     # Requêtes pour les Dépenses et Avances, filtrées par temps de session.
#     montant_total_depenses = Depense.objects.filter(date__gte=start_time, date__lt=end_time).aggregate(total=Sum('montant'))['total'] or 0
#     montant_total_avances = Avance.objects.filter(date_avance__gte=start_time, date_avance__lt=end_time).aggregate(total=Sum('montant'))['total'] or 0

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
# # FONCTION D'ARCHIVAGE 
# # ----------------------------------------------------------------------------------

# def creer_details_et_performance_pour_rapport(rapport, context_data_calc):
#     """
#     Crée les DetailVenteBoisson et PerformancePersonnelNocturne pour un rapport donné
#     à partir des données calculées.
#     """
    
#     # Étape A : Sauvegarde des détails des boissons
#     details_a_creer = []
    
#     for item in context_data_calc['ventes_boissons']:
#         boisson_id_to_use = getattr(item['boisson'], 'id', None)
        
#         if boisson_id_to_use:
#             details_a_creer.append(
#                 DetailVenteBoisson(
#                     rapport=rapport,
#                     boisson_id=boisson_id_to_use,
#                     quantite_totale=item['quantite_totale'],
#                     montant_total=item['montant_total'],
#                     prix_unitaire_au_moment_vente=item['prix_unitaire_au_moment_vente']
#                 )
#             )

#     DetailVenteBoisson.objects.bulk_create(details_a_creer)


#     # Étape B : Sauvegarde de la Performance du Personnel
#     performances_a_creer = []
#     for perf in context_data_calc['performance_personnel']:
#         performances_a_creer.append(
#             PerformancePersonnelNocturne(
#                 rapport=rapport,
#                 personnel_id=perf['id'], 
#                 montant_vendu_total=perf['montant_vendu_total'],
#                 montant_impaye_personnel=perf['montant_impaye_personnel'],
#                 quantite_totale_boissons_vendues=perf['quantite_totale_boissons_vendues'],
#                 montant_total_avances_personnel=perf['montant_total_avances_personnel'],
#                 details_boissons_vendues_archive=perf['details_boissons_vendues']
#             )
#         )
#     PerformancePersonnelNocturne.objects.bulk_create(performances_a_creer)


# # ----------------------------------------------------------------------------------
# # VUE DE GESTION DE SESSION (TOGGLE_SESSION) - CORRIGÉE
# # ----------------------------------------------------------------------------------

# @login_required
# def toggle_session(request):
#     """
#     Ouvre ou ferme la session de vente nocturne (la Boîte).
#     """
#     if request.method != 'POST':
#         return redirect('ventes:point_des_ventes')

#     action = request.POST.get('action')
#     caissier_user = request.user 
    
#     try:
#         # CORRECTION FIELD ERROR: Utilisation du champ 'user' du modèle Personnel
#         caissier_personnel = Personnel.objects.get(user=caissier_user)
#     except Personnel.DoesNotExist:
#         messages.error(request, "Erreur : Votre compte utilisateur n'est pas associé à un profil Personnel. Veuillez contacter l'administrateur.")
#         return redirect('ventes:point_des_ventes')
#     except Personnel.MultipleObjectsReturned:
#         messages.error(request, "Erreur : Plusieurs profils Personnel sont associés à votre compte utilisateur. Contactez l'administrateur.")
#         return redirect('ventes:point_des_ventes')


#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()

#     with transaction.atomic():
#         if action == 'ouvrir' and not session_active:
#             # ACTION OUVRIR (ON)
#             RapportVenteNocturne.objects.create(
#                 start_time=timezone.now(),
#                 caissier=caissier_personnel,
#                 is_active=True,
#             )
#             messages.success(request, "La boîte est ouverte ! Le rapport de vente nocturne a démarré.")
        
#         elif action == 'fermer' and session_active:
#             # ACTION FERMER (OFF)
            
#             # Vérification de sécurité : Seul le caissier qui a ouvert peut fermer
#             if session_active.caissier != caissier_personnel:
#                 messages.error(request, f"Seul le caissier qui a ouvert la session ({session_active.caissier.prenom}) peut la fermer.")
#                 return redirect('ventes:point_des_ventes')
                
#             # 1. Calculer les données finales de la session
#             end_time = timezone.now()
#             context_data_calc = calculer_ventes_en_temps_reel(session_active.start_time, end_time)

#             # 2. Mise à jour et sauvegarde du rapport principal
#             session_active.end_time = end_time
#             session_active.is_active = False # Marquer comme terminé
#             session_active.montant_total_vente = context_data_calc.get('montant_total_vente', 0)
#             session_active.montant_total_impayees = context_data_calc.get('montant_total_impayees', 0)
#             session_active.montant_total_depenses = context_data_calc.get('montant_total_depenses', 0)
#             session_active.montant_total_avances = context_data_calc.get('montant_total_avances', 0)
#             session_active.montant_decaisse = context_data_calc.get('montant_decaisse', 0)
#             session_active.chiffre_affaire = context_data_calc.get('chiffre_affaire', 0)
#             session_active.save()

#             # 3. Créer les détails archivés
#             creer_details_et_performance_pour_rapport(session_active, context_data_calc)
            
#             messages.success(request, f"La boîte est fermée ! Le rapport du {session_active.start_time.strftime('%d/%m/%Y %H:%M')} a été archivé.")

#         else:
#             messages.warning(request, "Action invalide ou l'état de la session n'a pas changé.")

#     return redirect('ventes:point_des_ventes')

# from django.shortcuts import render, get_object_or_404, redirect
# from django.db.models import Q, Sum, F, Case, When, DecimalField
# from django.utils import timezone
# from datetime import timedelta, datetime, date # Importez 'date'
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.contrib import messages
# from django.utils.dateparse import parse_date # pour analyser une date simple

# # ... (Importations des modèles et fonctions de calcul restent inchangées) ...

# # ----------------------------------------------------------------------------------
# # VUE PRINCIPALE D'AFFICHAGE (CORRIGÉE POUR LA RECHERCHE PRÉCISE)
# # ----------------------------------------------------------------------------------

# @login_required
# def point_des_ventes(request):
    
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
#     date_query_str = request.GET.get('date') 
    
#     context = {
#         "is_session_active": session_active is not None,
#         "current_session": session_active,
#         "rapports_historiques": None, 
#         "is_historical_view": False,
#     }

#     if session_active:
#         # --- CAS 1 : Session Active (Mode Temps Réel) ---
#         context["start_time"] = session_active.start_time
#         context["end_time"] = timezone.now()
#         context.update(calculer_ventes_en_temps_reel(context["start_time"], context["end_time"]))
#         return render(request, "ventes/point_des_ventes.html", context)
    
#     # --- CAS 2, 3, 4 : Session FERMÉE (Historique ou Liste Globale) ---

#     if date_query_str:
#         # Tente de parser d'abord comme DATETIME (recherche précise par heure et minute)
#         try:
#             date_time_obj = datetime.strptime(date_query_str, '%Y-%m-%dT%H:%M')
#             start_time_to_check = timezone.make_aware(date_time_obj)

#             # --- CORRECTION DE LA RECHERCHE EXACTE (PLAGE DE TEMPS) ---
            
#             # Définir le début de la minute et la fin de la minute
#             start_of_minute = start_time_to_check
#             end_of_minute = start_time_to_check + timedelta(minutes=1)

#             # Chercher le rapport qui commence DANS cette minute
#             rapports_trouves = RapportVenteNocturne.objects.prefetch_related(
#                 'details_boissons', 
#                 'performance_personnel',
#                 'performance_personnel__personnel'
#             ).filter(
#                 start_time__gte=start_of_minute, 
#                 start_time__lt=end_of_minute      
#             ).first() 

#             if rapports_trouves:
#                 rapport = rapports_trouves
#             else:
#                 # Si aucun rapport n'est trouvé dans la minute, on lève l'exception pour passer à la recherche par date simple
#                 raise ValueError("Aucun rapport trouvé dans cette minute. Tentative de recherche par date seule.") 
            
#             # --- FIN DE CORRECTION ---

#             # Affichage du rapport unique
#             context["is_historical_view"] = True
#             context["start_time"] = rapport.start_time
#             context["end_time"] = rapport.end_time
            
#             # Remplacement des données avec l'archive
#             context.update({
#                 "montant_total_vente": rapport.montant_total_vente,
#                 "montant_total_impayees": rapport.montant_total_impayees,
#                 "montant_total_depenses": rapport.montant_total_depenses,
#                 "montant_total_avances": rapport.montant_total_avances,
#                 "montant_decaisse": rapport.montant_decaisse,
#                 "chiffre_affaire": rapport.chiffre_affaire,
#                 "ventes_boissons": rapport.details_boissons.all(), 
#                 "performance_personnel": rapport.performance_personnel.all()
#             })
#             return render(request, "ventes/point_des_ventes.html", context)

#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             # Si le format DATETIME a échoué, on essaie le format DATE (AAAA-MM-JJ)
#             date_only = parse_date(date_query_str.split('T')[0]) # On prend juste la partie date si c'est un datetime invalide
#             if date_only:
#                 # Filtrer tous les rapports archivés (is_active=False) pour ce jour.
#                 rapports_du_jour = RapportVenteNocturne.objects.filter(
#                     is_active=False,
#                     start_time__date=date_only
#                 ).order_by('-start_time')
                
#                 if rapports_du_jour.count() == 1:
#                     # Si un seul rapport, l'afficher directement (logique inchangée)
#                     unique_rapport = rapports_du_jour.first()
                    
#                     context["is_historical_view"] = True
#                     context["start_time"] = unique_rapport.start_time
#                     context["end_time"] = unique_rapport.end_time
#                     # On charge les données du rapport
#                     context.update({
#                         "montant_total_vente": unique_rapport.montant_total_vente,
#                         "montant_total_impayees": unique_rapport.montant_total_impayees,
#                         "montant_total_depenses": unique_rapport.montant_total_depenses,
#                         "montant_total_avances": unique_rapport.montant_total_avances,
#                         "montant_decaisse": unique_rapport.montant_decaisse,
#                         "chiffre_affaire": unique_rapport.chiffre_affaire,
#                         "ventes_boissons": unique_rapport.details_boissons.all(), 
#                         "performance_personnel": unique_rapport.performance_personnel.all()
#                     })
#                     return render(request, "ventes/point_des_ventes.html", context)
                
#                 elif rapports_du_jour.count() > 0:
#                     # Afficher la liste des rapports pour ce jour pour sélection
#                     context["rapports_historiques"] = rapports_du_jour
#                     messages.info(request, f"{rapports_du_jour.count()} sessions trouvées pour le {date_only.strftime('%d/%m/%Y')}. Veuillez sélectionner l'heure exacte.")
#                     return render(request, "ventes/point_des_ventes.html", context)
            
#             # Si on arrive ici, la date est invalide ou non trouvée
#             messages.error(request, "Rapport historique non trouvé ou format de date invalide.")
            
#     # --- CAS 4 : Pas de session active et pas de recherche (Affichage de l'historique global) ---
    
#     # Afficher la liste des 50 derniers rapports archivés
#     context["rapports_historiques"] = RapportVenteNocturne.objects.filter(is_active=False).order_by('-start_time')[:50]
    
#     # Pour éviter l'erreur de calcul quand la session est fermée sans recherche :
#     context.update({
#         "montant_total_vente": 0,
#         "montant_total_impayees": 0,
#         "montant_total_depenses": 0,
#         "montant_total_avances": 0,
#         "montant_decaisse": 0,
#         "chiffre_affaire": 0,
#         "ventes_boissons": [], 
#         "performance_personnel": []
#     })

#     return render(request, "ventes/point_des_ventes.html", context)


# =============================================================================
# FONCTIONS DE VÉRIFICATION DES PERMISSIONS
# =============================================================================

# def _is_user_in_allowed_roles(user, allowed_roles):
#     """
#     Vérifie si un utilisateur a accès basé sur ses rôles.
    
#     Logique :
#     1. Les superutilisateurs ont toujours accès
#     2. Les utilisateurs avec un profil Personnel dont le rôle est dans la liste autorisée ont accès
    
#     Args:
#         user: L'utilisateur connecté à vérifier
#         allowed_roles: Liste des rôles autorisés pour cette action
    
#     Returns:
#         bool: True si l'utilisateur a la permission, False sinon
#     """
#     # 1. Vérification superutilisateur - Accès total
#     if user.is_superuser:
#         return True
    
#     # 2. Vérification du profil Personnel
#     if hasattr(user, 'personnel_profile'):
#         try:
#             # Récupère le rôle de l'utilisateur depuis son profil Personnel
#             user_role = user.personnel_profile.role 
#             # Vérifie si ce rôle est dans la liste des rôles autorisés
#             return user_role in allowed_roles
#         except AttributeError:
#             # Cas où l'attribut role n'existe pas
#             return False
    
#     # Cas où l'utilisateur n'a pas de profil Personnel
#     return False

# def user_can_ouvrir_session(user):
#     """
#     Vérifie si l'utilisateur peut ouvrir une session de vente.
    
#     Returns:
#         bool: True si l'utilisateur a la permission d'ouvrir une session
#     """
#     return _is_user_in_allowed_roles(user, ROLES_OUVERTURE_SESSION)

# def user_can_fermer_session(user):
#     """
#     Vérifie si l'utilisateur peut fermer une session de vente.
    
#     Returns:
#         bool: True si l'utilisateur a la permission de fermer une session
#     """
#     return _is_user_in_allowed_roles(user, ROLES_FERMETURE_SESSION)

# # =============================================================================
# # VUE POUR OUVRIR/FERMER LA SESSION
# # =============================================================================

# @login_required  # Nécessite que l'utilisateur soit connecté
# def toggle_session(request):
#     """
#     Vue principale pour ouvrir ou fermer une session de vente nocturne.
    
#     Fonctionnement :
#     - Ouvre une nouvelle session si aucune n'est active
#     - Ferme la session active si une est en cours
#     - Vérifie les permissions avant chaque action
    
#     Flow :
#     1. Vérifie que la requête est en POST
#     2. Vérifie les permissions de l'utilisateur
#     3. Récupère le profil Personnel de l'utilisateur
#     4. Exécute l'action (ouvrir/fermer) avec gestion des erreurs
#     """
    
#     # 1. VÉRIFICATION DE LA MÉTHODE HTTP
#     # On n'accepte que les requêtes POST pour cette action critique
#     if request.method != 'POST':
#         messages.error(request, "Action non autorisée. Méthode HTTP invalide.")
#         return redirect('ventes:point_des_ventes')

#     # 2. RÉCUPÉRATION DE L'ACTION ET DE L'UTILISATEUR
#     action = request.POST.get('action')  # 'ouvrir' ou 'fermer'
#     caissier_user = request.user  # L'utilisateur actuellement connecté
    
#     # 3. VÉRIFICATION DES PERMISSIONS SPÉCIFIQUES
#     # Vérifie si l'utilisateur a le droit d'ouvrir une session
#     if action == 'ouvrir' and not user_can_ouvrir_session(caissier_user):
#         messages.error(request, "❌ Accès refusé : Vous n'avez pas les permissions nécessaires pour ouvrir une session.")
#         return redirect('ventes:point_des_ventes')
    
#     # Vérifie si l'utilisateur a le droit de fermer une session
#     if action == 'fermer' and not user_can_fermer_session(caissier_user):
#         messages.error(request, "❌ Accès refusé : Vous n'avez pas les permissions nécessaires pour fermer une session.")
#         return redirect('ventes:point_des_ventes')
    
#     # # 4. RÉCUPÉRATION DU PROFIL PERSONNEL
#     # # On lie l'action à un membre du personnel (pour l'audit trail)
#     # try:
#     #     # CORRECTION : Utilise le champ 'user' du modèle Personnel pour faire le lien
#     #     caissier_personnel = Personnel.objects.get(user=caissier_user)
#     # except Personnel.DoesNotExist:
#     #     # Cas où l'utilisateur n'a pas de profil Personnel associé
#     #     messages.error(request, "❌ Erreur de profil : Votre compte utilisateur n'est pas associé à un profil Personnel. Veuillez contacter l'administrateur.")
#     #     return redirect('ventes:point_des_ventes')
#     # except Personnel.MultipleObjectsReturned:
#     #     # Cas d'erreur de base de données (plusieurs profils pour un utilisateur)
#     #     messages.error(request, "❌ Erreur de profil : Plusieurs profils Personnel sont associés à votre compte utilisateur. Contactez l'administrateur.")
#     #     return redirect('ventes:point_des_ventes')

#     # 5. VÉRIFICATION DE L'ÉTAT ACTUEL DE LA SESSION
#     # Récupère la session active s'il y en a une
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()

#     # 6. EXÉCUTION DE L'ACTION DANS UNE TRANSACTION ATOMIQUE
#     # Garantit que toutes les opérations réussissent ou échouent ensemble
#     with transaction.atomic():
        
#         # CAS A : OUVERTURE DE SESSION
#         if action == 'ouvrir' and not session_active:
#             # Création d'une nouvelle session active
#             RapportVenteNocturne.objects.create(
#                 start_time=timezone.now(),      # Heure de début = maintenant
#                 caissier=user_can_fermer_session,    # Caissier qui ouvre la session
#                 is_active=True,                 # Marque la session comme active
#             )
#             messages.success(request, "✅ La boîte est ouverte ! Le rapport de vente nocturne a démarré.")
        
#         # CAS B : FERMETURE DE SESSION  
#         elif action == 'fermer' and session_active:
            
#             # Vérification de sécurité supplémentaire :
#             # Seul le caissier qui a ouvert la session peut la fermer
#             if session_active.caissier != user_can_fermer_session:
#                 messages.error(request, f"❌ Sécurité : Seul le caissier qui a ouvert la session ({session_active.caissier.prenom}) peut la fermer.")
#                 return redirect('ventes:point_des_ventes')
                
#             # ÉTAPE 1 : CALCUL DES DONNÉES FINALES
#             # Calcule toutes les statistiques de vente pour la période
#             end_time = timezone.now()
#             context_data_calc = calculer_ventes_en_temps_reel(session_active.start_time, end_time)

#             # ÉTAPE 2 : MISE À JOUR DU RAPPORT PRINCIPAL
#             # Sauvegarde toutes les données calculées dans le rapport
#             session_active.end_time = end_time
#             session_active.is_active = False  # Marque la session comme terminée
#             session_active.montant_total_vente = context_data_calc.get('montant_total_vente', 0)
#             session_active.montant_total_impayees = context_data_calc.get('montant_total_impayees', 0)
#             session_active.montant_total_depenses = context_data_calc.get('montant_total_depenses', 0)
#             session_active.montant_total_avances = context_data_calc.get('montant_total_avances', 0)
#             session_active.montant_decaisse = context_data_calc.get('montant_decaisse', 0)
#             session_active.chiffre_affaire = context_data_calc.get('chiffre_affaire', 0)
#             session_active.save()

#             # ÉTAPE 3 : CRÉATION DES DONNÉES DÉTAILLÉES ARCHIVÉES
#             # Génère les enregistrements détaillés pour l'historique
#             creer_details_et_performance_pour_rapport(session_active, context_data_calc)
            
#             # Message de confirmation avec la date de la session
#             messages.success(request, f"✅ La boîte est fermée ! Le rapport du {session_active.start_time.strftime('%d/%m/%Y %H:%M')} a été archivé.")

#         # CAS C : ACTION INVALIDE
#         else:
#             messages.warning(request, "⚠️ Action invalide ou l'état de la session n'a pas changé.")

#     # 7. REDIRECTION VERS LA PAGE PRINCIPALE
#     return redirect('ventes:point_des_ventes')


# # =============================================================================
# # VUE PRINCIPALE D'AFFICHAGE DU POINT DES VENTES
# # =============================================================================

# @login_required  # Nécessite une connexion
# @role_required(allowed_roles=ROLES_VISITE_VENTES)
# def point_des_ventes(request):
#     """
#     Vue principale qui affiche le tableau de bord des ventes.
    
#     Gère 4 cas différents :
#     1. Session active → Mode temps réel
#     2. Recherche par date/heure précise → Détail d'un rapport historique
#     3. Recherche par date seule → Liste des rapports du jour
#     4. Aucune session, aucune recherche → Historique global
    
#     Args:
#         request: La requête HTTP avec éventuellement un paramètre 'date'
    
#     Returns:
#         HttpResponse: La page rendue avec le contexte approprié
#     """
    
#     # 1. INITIALISATION
#     # Vérifie s'il y a une session active
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
#     # Récupère le paramètre de date depuis l'URL (si présent)
#     date_query_str = request.GET.get('date') 
    
#     # 2. VÉRIFICATION DES PERMISSIONS POUR L'AFFICHAGE
#     # Ces variables seront utilisées dans le template pour afficher/masquer les boutons
#     can_ouvrir_session = user_can_ouvrir_session(request.user)
#     can_fermer_session = user_can_fermer_session(request.user)
    
#     # 3. PRÉPARATION DU CONTEXTE DE BASE
#     # Contient les données qui seront passées au template
#     context = {
#         # État de la session
#         "is_session_active": session_active is not None,
#         "current_session": session_active,
        
#         # Gestion de l'historique
#         "rapports_historiques": None, 
#         "is_historical_view": False,
        
#         # Permissions pour l'interface
#         "can_ouvrir_session": can_ouvrir_session,
#         "can_fermer_session": can_fermer_session,
#     }

#     # 4. CAS 1 : SESSION ACTIVE (MODE TEMPS RÉEL)
#     if session_active:
#         # Configure les dates de la période analysée
#         context["start_time"] = session_active.start_time
#         context["end_time"] = timezone.now()
        
#         # Calcule les données en temps réel et les ajoute au contexte
#         context.update(calculer_ventes_en_temps_reel(context["start_time"], context["end_time"]))
        
#         # Affiche la page avec les données temps réel
#         return render(request, "ventes/point_des_ventes.html", context)
    
#     # =========================================================================
#     # CAS 2, 3, 4 : SESSION FERMÉE (HISTORIQUE)
#     # =========================================================================

#     # 5. CAS 2 : RECHERCHE PAR DATE/HEURE PRÉCISE
#     if date_query_str:
#         try:
#             # Tente de parser la date avec l'heure (format: AAAA-MM-JJTHH:MM)
#             date_time_obj = datetime.strptime(date_query_str, '%Y-%m-%dT%H:%M')
#             start_time_to_check = timezone.make_aware(date_time_obj)

#             # Cherche le rapport qui commence exactement dans cette minute
#             rapports_trouves = RapportVenteNocturne.objects.prefetch_related(
#                 'details_boissons', 
#                 'performance_personnel',
#                 'performance_personnel__personnel'
#             ).filter(
#                 start_time__gte=start_time_to_check, 
#                 start_time__lt=start_time_to_check + timedelta(minutes=1)      
#             ).first() 

#             if rapports_trouves:
#                 rapport = rapports_trouves
#             else:
#                 # Si aucun rapport trouvé avec l'heure précise, on essaie avec la date seule
#                 raise ValueError("Aucun rapport trouvé dans cette minute. Tentative de recherche par date seule.") 
            
#             # AFFICHAGE D'UN RAPPORT HISTORIQUE PRÉCIS
#             context["is_historical_view"] = True
#             context["start_time"] = rapport.start_time
#             context["end_time"] = rapport.end_time
            
#             # Charge toutes les données depuis le rapport archivé
#             context.update({
#                 "montant_total_vente": rapport.montant_total_vente,
#                 "montant_total_impayees": rapport.montant_total_impayees,
#                 "montant_total_depenses": rapport.montant_total_depenses,
#                 "montant_total_avances": rapport.montant_total_avances,
#                 "montant_decaisse": rapport.montant_decaisse,
#                 "chiffre_affaire": rapport.chiffre_affaire,
#                 "ventes_produits": rapport.details_boissons.all(),
#                 "performance_personnel": rapport.performance_personnel.all()
#             })
#             return render(request, "ventes/point_des_ventes.html", context)

#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             # 6. CAS 3 : RECHERCHE PAR DATE SEULE (AAAA-MM-JJ)
#             # Extrait juste la partie date du paramètre
#             date_only = parse_date(date_query_str.split('T')[0])
            
#             if date_only:
#                 # Cherche tous les rapports archivés pour cette date
#                 rapports_du_jour = RapportVenteNocturne.objects.filter(
#                     is_active=False,  # Uniquement les rapports archivés
#                     start_time__date=date_only  # Pour la date spécifique
#                 ).order_by('-start_time')  # Du plus récent au plus ancien
                
#                 # SOUS-CAS 3A : UN SEUL RAPPORT TROUVÉ
#                 if rapports_du_jour.count() == 1:
#                     unique_rapport = rapports_du_jour.first()
                    
#                     context["is_historical_view"] = True
#                     context["start_time"] = unique_rapport.start_time
#                     context["end_time"] = unique_rapport.end_time
                    
#                     # Charge les données du rapport unique
#                     context.update({
#                         "montant_total_vente": unique_rapport.montant_total_vente,
#                         "montant_total_impayees": unique_rapport.montant_total_impayees,
#                         "montant_total_depenses": unique_rapport.montant_total_depenses,
#                         "montant_total_avances": unique_rapport.montant_total_avances,
#                         "montant_decaisse": unique_rapport.montant_decaisse,
#                         "chiffre_affaire": unique_rapport.chiffre_affaire,
#                         "ventes_produits": unique_rapport.details_boissons.all(),
#                         "performance_personnel": unique_rapport.performance_personnel.all()
#                     })
#                     return render(request, "ventes/point_des_ventes.html", context)
                
#                 # SOUS-CAS 3B : PLUSIEURS RAPPORTS TROUVÉS
#                 elif rapports_du_jour.count() > 0:
#                     # Affiche la liste pour que l'utilisateur choisisse lequel voir
#                     context["rapports_historiques"] = rapports_du_jour
#                     messages.info(request, f"📊 {rapports_du_jour.count()} sessions trouvées pour le {date_only.strftime('%d/%m/%Y')}. Veuillez sélectionner l'heure exacte.")
#                     return render(request, "ventes/point_des_ventes.html", context)
            
#             # 7. CAS D'ERREUR : DATE INVALIDE OU NON TROUVÉE
#             messages.error(request, "❌ Rapport historique non trouvé ou format de date invalide.")
            
#     # 8. CAS 4 : AUCUNE SESSION ACTIVE, AUCUNE RECHERCHE (HISTORIQUE GLOBAL)
#     # Affiche la liste des 50 derniers rapports archivés
#     context["rapports_historiques"] = RapportVenteNocturne.objects.filter(
#         is_active=False
#     ).order_by('-start_time')[:50]  # Les 50 plus récents
    
#     # 9. VALEURS PAR DÉFAUT POUR ÉVITER LES ERREURS DANS LE TEMPLATE
#     # Quand il n'y a pas de session active ni de recherche
#     context.update({
#         "montant_total_vente": 0,
#         "montant_total_impayees": 0,
#         "montant_total_depenses": 0,
#         "montant_total_avances": 0,
#         "montant_decaisse": 0,
#         "chiffre_affaire": 0,
#         "ventes_produits": [],
#         "performance_personnel": []
#     })

#     # 10. RENDU FINAL DE LA PAGE
#     return render(request, "ventes/point_des_ventes.html", context)


# =============================================================================
# FONCTIONS UTILITAIRES POUR LA GESTION DES PERMISSIONS
# =============================================================================

# def _is_user_in_allowed_roles(user, allowed_roles):
#     """
#     Vérifie si un utilisateur a accès à une fonctionnalité basée sur ses rôles.
    
#     Cette fonction implémente la logique de permission utilisée dans le système :
#     - Les superutilisateurs ont toujours accès à tout
#     - Les utilisateurs normaux doivent avoir un profil Personnel avec un rôle autorisé
    
#     Args:
#         user (User): L'utilisateur Django connecté
#         allowed_roles (list): Liste des rôles autorisés pour l'action
    
#     Returns:
#         bool: True si l'utilisateur a la permission, False sinon
#     """
#     # 1. LES SUPERUTILISATEURS ONT TOUJOURS ACCÈS
#     if user.is_superuser:
#         return True
    
#     # 2. VÉRIFICATION DU PROFIL PERSONNEL POUR LES UTILISATEURS NORMAUX
#     if hasattr(user, 'personnel_profile'):
#         try:
#             # Récupère le rôle depuis le profil Personnel associé
#             user_role = user.personnel_profile.role 
#             # Vérifie si ce rôle est dans la liste des rôles autorisés
#             return user_role in allowed_roles
#         except AttributeError:
#             # Cas où l'attribut 'role' n'existe pas sur le profil
#             return False
    
#     # 3. CAS PAR DÉFAUT : AUCUN ACCÈS
#     return False


# def user_can_ouvrir_session(user):
#     """
#     Vérifie si un utilisateur peut ouvrir une session de vente.
    
#     Returns:
#         bool: True si l'utilisateur a la permission d'ouvrir une session
#     """
#     return _is_user_in_allowed_roles(user, ROLES_OUVERTURE_SESSION)


# def user_can_fermer_session(user):
#     """
#     Vérifie si un utilisateur peut fermer une session de vente.
    
#     Returns:
#         bool: True si l'utilisateur a la permission de fermer une session
#     """
#     return _is_user_in_allowed_roles(user, ROLES_FERMETURE_SESSION)


# def get_user_display_name(user):
#     """
#     Retourne le nom d'affichage approprié pour un utilisateur.
    
#     Hiérarchie de priorité :
#     1. Prénom + Nom du profil Personnel (si disponible)
#     2. Full name de l'utilisateur Django
#     3. Username de l'utilisateur Django
    
#     Args:
#         user (User): L'utilisateur Django
    
#     Returns:
#         str: Le nom d'affichage formaté
#     """
#     # 1. ESSAIE D'UTILISER LE PROFIL PERSONNEL
#     if hasattr(user, 'personnel_profile'):
#         try:
#             personnel = user.personnel_profile
#             return f"{personnel.prenom} {personnel.nom}"
#         except (AttributeError, ObjectDoesNotExist):
#             # Continue si le profil est incomplet ou inaccessible
#             pass
    
#     # 2. ESSAIE LE FULL NAME DE L'UTILISATEUR DJANGO
#     full_name = user.get_full_name()
#     if full_name.strip():
#         return full_name
    
#     # 3. UTILISE LE USERNAME COMME SOLUTION DE SECOURS
#     return user.username


# # =============================================================================
# # VUE PRINCIPALE POUR L'OUVERTURE/FERMETURE DES SESSIONS
# # =============================================================================

# @login_required
# def toggle_session(request):
#     """
#     Vue pour ouvrir ou fermer une session de vente nocturne.
    
#     Cette vue gère le cycle de vie complet d'une session :
#     - Ouverture : Crée une nouvelle session active
#     - Fermeture : Archive la session active et calcule les statistiques finales
    
#     Flow de sécurité :
#     1. Vérifie que la requête est en POST
#     2. Vérifie les permissions de l'utilisateur
#     3. Récupère optionnellement le profil Personnel
#     4. Exécute l'action dans une transaction atomique
    
#     Args:
#         request (HttpRequest): La requête HTTP contenant l'action
    
#     Returns:
#         HttpResponseRedirect: Redirection vers la page du point des ventes
#     """
    
#     # === ÉTAPE 1 : VÉRIFICATION DE LA MÉTHODE HTTP ===
#     # Cette action critique ne doit être accessible que via POST pour éviter les CSRF
#     if request.method != 'POST':
#         messages.error(request, "❌ Erreur : Action non autorisée. Méthode HTTP invalide.")
#         return redirect('ventes:point_des_ventes')

#     # === ÉTAPE 2 : RÉCUPÉRATION DES DONNÉES DE LA REQUÊTE ===
#     action = request.POST.get('action')  # 'ouvrir' ou 'fermer'
#     user = request.user  # L'utilisateur actuellement connecté
    
#     # === ÉTAPE 3 : VÉRIFICATION DES PERMISSIONS ===
#     # Vérifie si l'utilisateur a le droit d'effectuer l'action demandée
#     if action == 'ouvrir' and not user_can_ouvrir_session(user):
#         messages.error(request, "❌ Accès refusé : Vous n'avez pas les permissions nécessaires pour ouvrir une session.")
#         return redirect('ventes:point_des_ventes')
    
#     if action == 'fermer' and not user_can_fermer_session(user):
#         messages.error(request, "❌ Accès refusé : Vous n'avez pas les permissions nécessaires pour fermer une session.")
#         return redirect('ventes:point_des_ventes')

#     # === ÉTAPE 4 : RÉCUPÉRATION OPTIONNELLE DU PROFIL PERSONNEL ===
#     # Le profil Personnel est optionnel - utilisé pour l'audit si disponible
#     caissier_personnel = None
#     try:
#         # Tente de récupérer le profil Personnel associé à l'utilisateur
#         caissier_personnel = Personnel.objects.get(user=user)
#     except Personnel.DoesNotExist:
#         # CAS NORMAL : L'utilisateur n'a pas de profil Personnel
#         # On continue quand même car les permissions sont déjà vérifiées par les rôles
#         pass
#     except Personnel.MultipleObjectsReturned:
#         # CAS D'ERREUR : Plusieurs profils pour le même utilisateur
#         # On prend le premier pour éviter de bloquer l'action
#         caissier_personnel = Personnel.objects.filter(user=user).first()

#     # === ÉTAPE 5 : VÉRIFICATION DE L'ÉTAT ACTUEL DE LA SESSION ===
#     # Récupère la session active s'il y en a une
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()

#     # === ÉTAPE 6 : EXÉCUTION DE L'ACTION DANS UNE TRANSACTION ATOMIQUE ===
#     # Garantit que toutes les opérations de base de données réussissent ou échouent ensemble
#     with transaction.atomic():
        
#         # === SOUS-CAS A : OUVERTURE D'UNE NOUVELLE SESSION ===
#         if action == 'ouvrir' and not session_active:
#             # Création d'une nouvelle session de vente
#             nouvelle_session = RapportVenteNocturne.objects.create(
#                 start_time=timezone.now(),      # Heure de début = maintenant
#                 caissier=caissier_personnel,    # Profil Personnel (peut être None)
#                 is_active=True,                 # Marque la session comme active
#             )
            
#             # Message de succès avec le nom de l'utilisateur
#             nom_affiche = get_user_display_name(user)
#             messages.success(request, f"✅ La boîte est ouverte par {nom_affiche} ! La session de vente nocturne a démarré.")
        
#         # === SOUS-CAS B : FERMETURE DE LA SESSION ACTIVE ===
#         elif action == 'fermer' and session_active:
            
#             # VÉRIFICATION DE SÉCURITÉ SUPPLÉMENTAIRE
#             # Empêche un utilisateur de fermer une session qu'il n'a pas ouverte
#             if (session_active.caissier and session_active.caissier.user != user) and not user.is_superuser:
#                 messages.error(request, "❌ Erreur de sécurité : Seul le caissier qui a ouvert la session peut la fermer.")
#                 return redirect('ventes:point_des_ventes')
                
#             # === PROCESSUS COMPLET DE FERMETURE ===
            
#             # Étape B1 : CALCUL DES STATISTIQUES FINALES
#             end_time = timezone.now()
#             context_data_calc = calculer_ventes_en_temps_reel(session_active.start_time, end_time)

#             # Étape B2 : MISE À JOUR DU RAPPORT PRINCIPAL
#             session_active.end_time = end_time
#             session_active.is_active = False  # Marque la session comme terminée
            
#             # Sauvegarde de toutes les statistiques financières
#             session_active.montant_total_vente = context_data_calc.get('montant_total_vente', 0)
#             session_active.montant_total_impayees = context_data_calc.get('montant_total_impayees', 0)
#             session_active.montant_total_depenses = context_data_calc.get('montant_total_depenses', 0)
#             session_active.montant_total_avances = context_data_calc.get('montant_total_avances', 0)
#             session_active.montant_decaisse = context_data_calc.get('montant_decaisse', 0)
#             session_active.chiffre_affaire = context_data_calc.get('chiffre_affaire', 0)
            
#             session_active.save()

#             # Étape B3 : CRÉATION DES DONNÉES DÉTAILLÉES POUR L'HISTORIQUE
#             creer_details_et_performance_pour_rapport(session_active, context_data_calc)
            
#             # Message de confirmation avec la date de la session
#             messages.success(request, f"✅ La boîte est fermée ! Le rapport du {session_active.start_time.strftime('%d/%m/%Y %H:%M')} a été archivé avec succès.")

#         # === SOUS-CAS C : ACTION INVALIDE OU ÉTAT INCOHÉRENT ===
#         else:
#             messages.warning(request, "⚠️ Action invalide ou l'état de la session n'a pas changé.")

#     # === ÉTAPE 7 : REDIRECTION VERS LA PAGE PRINCIPALE ===
#     return redirect('ventes:point_des_ventes')


# # =============================================================================
# # VUE PRINCIPALE D'AFFICHAGE DU TABLEAU DE BORD DES VENTES
# # =============================================================================

# @login_required
# def point_des_ventes(request):
#     """
#     Vue principale qui affiche le tableau de bord des ventes nocturnes.
    
#     Cette vue gère 4 cas d'utilisation différents :
    
#     CAS 1 : Session active → Affichage en temps réel
#     CAS 2 : Recherche par date/heure précise → Détail d'un rapport historique spécifique
#     CAS 3 : Recherche par date seule → Liste des rapports d'une journée
#     CAS 4 : Aucune session active, aucune recherche → Historique global des 50 derniers rapports
    
#     Args:
#         request (HttpRequest): La requête HTTP, peut contenir un paramètre 'date'
    
#     Returns:
#         HttpResponse: La page rendue avec le contexte approprié
#     """
    
#     # === INITIALISATION ET PRÉPARATION DU CONTEXTE ===
    
#     # Vérifie s'il existe une session active
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
    
#     # Récupère le paramètre de date depuis l'URL (format: YYYY-MM-DD ou YYYY-MM-DDTHH:MM)
#     date_query_str = request.GET.get('date') 
    
#     # Préparation du contexte de base qui sera passé au template
#     context = {
#         # État de la session
#         "is_session_active": session_active is not None,
#         "current_session": session_active,
        
#         # Gestion de l'historique
#         "rapports_historiques": None, 
#         "is_historical_view": False,
        
#         # Permissions pour l'interface utilisateur
#         "can_ouvrir_session": user_can_ouvrir_session(request.user),
#         "can_fermer_session": user_can_fermer_session(request.user),
#     }

#     # === CAS 1 : SESSION ACTIVE - MODE TEMPS RÉEL ===
#     if session_active:
#         # Configuration de la période analysée
#         context["start_time"] = session_active.start_time
#         context["end_time"] = timezone.now()
        
#         # Calcul des données en temps réel et ajout au contexte
#         context.update(calculer_ventes_en_temps_reel(context["start_time"], context["end_time"]))
        
#         # Affichage de la page avec les données temps réel
#         return render(request, "ventes/point_des_ventes.html", context)
    
#     # =========================================================================
#     # CAS 2, 3, 4 : SESSION FERMÉE - CONSULTATION DE L'HISTORIQUE
#     # =========================================================================

#     # === CAS 2 : RECHERCHE PAR DATE ET HEURE PRÉCISE ===
#     if date_query_str:
#         try:
#             # Tente de parser la date avec l'heure (format: AAAA-MM-JJTHH:MM)
#             date_time_obj = datetime.strptime(date_query_str, '%Y-%m-%dT%H:%M')
#             start_time_to_check = timezone.make_aware(date_time_obj)

#             # Recherche le rapport qui commence exactement dans cette minute
#             rapport = RapportVenteNocturne.objects.prefetch_related(
#                 'details_boissons',           # Données des produits vendus
#                 'performance_personnel',      # Performances du personnel
#                 'performance_personnel__personnel'  # Informations du personnel
#             ).filter(
#                 # Recherche dans une fenêtre d'une minute pour la précision
#                 start_time__gte=start_time_to_check, 
#                 start_time__lt=start_time_to_check + timedelta(minutes=1)      
#             ).first()  # Prend le premier rapport trouvé

#             if rapport:
#                 # === SOUS-CAS 2A : RAPPORT TROUVÉ - AFFICHAGE DES DÉTAILS ===
#                 context["is_historical_view"] = True
#                 context["start_time"] = rapport.start_time
#                 context["end_time"] = rapport.end_time
                
#                 # Chargement de toutes les données depuis le rapport archivé
#                 context.update({
#                     "montant_total_vente": rapport.montant_total_vente,
#                     "montant_total_impayees": rapport.montant_total_impayees,
#                     "montant_total_depenses": rapport.montant_total_depenses,
#                     "montant_total_avances": rapport.montant_total_avances,
#                     "montant_decaisse": rapport.montant_decaisse,
#                     "chiffre_affaire": rapport.chiffre_affaire,
#                     "ventes_produits": rapport.details_boissons.all(),
#                     "performance_personnel": rapport.performance_personnel.all()
#                 })
#                 return render(request, "ventes/point_des_ventes.html", context)
#             else:
#                 # Aucun rapport trouvé avec l'heure précise
#                 raise ValueError("Aucun rapport trouvé pour cette date et heure.")

#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             # === CAS 3 : RECHERCHE PAR DATE SEULE (SANS HEURE) ===
            
#             # Extrait la partie date du paramètre (ignore l'heure si présente)
#             date_only = parse_date(date_query_str.split('T')[0])
            
#             if date_only:
#                 # Recherche tous les rapports archivés pour cette date
#                 rapports_du_jour = RapportVenteNocturne.objects.filter(
#                     is_active=False,           # Uniquement les rapports archivés
#                     start_time__date=date_only # Pour la date spécifique
#                 ).order_by('-start_time')      # Tri du plus récent au plus ancien
                
#                 # === SOUS-CAS 3A : UN SEUL RAPPORT TROUVÉ ===
#                 if rapports_du_jour.count() == 1:
#                     unique_rapport = rapports_du_jour.first()
                    
#                     context["is_historical_view"] = True
#                     context["start_time"] = unique_rapport.start_time
#                     context["end_time"] = unique_rapport.end_time
                    
#                     # Chargement des données du rapport unique
#                     context.update({
#                         "montant_total_vente": unique_rapport.montant_total_vente,
#                         "montant_total_impayees": unique_rapport.montant_total_impayees,
#                         "montant_total_depenses": unique_rapport.montant_total_depenses,
#                         "montant_total_avances": unique_rapport.montant_total_avances,
#                         "montant_decaisse": unique_rapport.montant_decaisse,
#                         "chiffre_affaire": unique_rapport.chiffre_affaire,
#                         "ventes_produits": unique_rapport.details_boissons.all(),
#                         "performance_personnel": unique_rapport.performance_personnel.all()
#                     })
#                     return render(request, "ventes/point_des_ventes.html", context)
                
#                 # === SOUS-CAS 3B : PLUSIEURS RAPPORTS TROUVÉS ===
#                 elif rapports_du_jour.count() > 0:
#                     # Affiche la liste pour que l'utilisateur choisisse lequel consulter
#                     context["rapports_historiques"] = rapports_du_jour
#                     messages.info(request, 
#                         f"📊 {rapports_du_jour.count()} sessions trouvées pour le {date_only.strftime('%d/%m/%Y')}. "
#                         f"Veuillez sélectionner une session spécifique."
#                     )
#                     return render(request, "ventes/point_des_ventes.html", context)
            
#             # === CAS D'ERREUR : DATE INVALIDE OU AUCUN RAPPORT TROUVÉ ===
#             messages.error(request, "❌ Aucun rapport historique trouvé pour la date spécifiée.")

#     # === CAS 4 : AUCUNE SESSION ACTIVE, AUCUNE RECHERCHE - HISTORIQUE GLOBAL ===
    
#     # Affichage des 50 derniers rapports archivés pour consultation
#     context["rapports_historiques"] = RapportVenteNocturne.objects.filter(
#         is_active=False  # Uniquement les sessions terminées
#     ).order_by('-start_time')[:50]  # Les 50 plus récents
    
#     # === VALEURS PAR DÉFAUT POUR ÉVITER LES ERREURS ===
#     # Fournit des valeurs par défaut quand il n'y a pas de données à afficher
#     context.update({
#         "montant_total_vente": 0,
#         "montant_total_impayees": 0,
#         "montant_total_depenses": 0,
#         "montant_total_avances": 0,
#         "montant_decaisse": 0,
#         "chiffre_affaire": 0,
#         "ventes_produits": [],
#         "performance_personnel": []
#     })

#     # === RENDU FINAL DE LA PAGE ===
#     return render(request, "ventes/point_des_ventes.html", context)




# ----------------------------------------------------------------------------------
# VUE DE GESTION DE SESSION (TOGGLE_SESSION)
# ----------------------------------------------------------------------------------

# @login_required
# def toggle_session(request):
#     """
#     Ouvre ou ferme la session de vente nocturne (la Boîte).
#     """
#     if request.method != 'POST':
#         return redirect('ventes:point_des_ventes')

#     action = request.POST.get('action')
#     caissier_user = request.user 
    
#     try:
#         # CORRECTION FIELD ERROR: Utilisation du champ 'user' du modèle Personnel
#         caissier_personnel = Personnel.objects.get(user=caissier_user)
#     except Personnel.DoesNotExist:
#         messages.error(request, "Erreur : Votre compte utilisateur n'est pas associé à un profil Personnel. Veuillez contacter l'administrateur.")
#         return redirect('ventes:point_des_ventes')
#     except Personnel.MultipleObjectsReturned:
#         messages.error(request, "Erreur : Plusieurs profils Personnel sont associés à votre compte utilisateur. Contactez l'administrateur.")
#         return redirect('ventes:point_des_ventes')

#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()

#     with transaction.atomic():
#         if action == 'ouvrir' and not session_active:
#             # ACTION OUVRIR (ON)
#             RapportVenteNocturne.objects.create(
#                 start_time=timezone.now(),
#                 caissier=caissier_personnel,
#                 is_active=True,
#             )
#             messages.success(request, "La boîte est ouverte ! Le rapport de vente nocturne a démarré.")
        
#         elif action == 'fermer' and session_active:
#             # ACTION FERMER (OFF)
            
#             # Vérification de sécurité : Seul le caissier qui a ouvert peut fermer
#             if session_active.caissier != caissier_personnel:
#                 messages.error(request, f"Seul le caissier qui a ouvert la session ({session_active.caissier.prenom}) peut la fermer.")
#                 return redirect('ventes:point_des_ventes')
                
#             # 1. Calculer les données finales de la session
#             end_time = timezone.now()
#             context_data_calc = calculer_ventes_en_temps_reel(session_active.start_time, end_time)

#             # 2. Mise à jour et sauvegarde du rapport principal
#             session_active.end_time = end_time
#             session_active.is_active = False # Marquer comme terminé
#             session_active.montant_total_vente = context_data_calc.get('montant_total_vente', 0)
#             session_active.montant_total_impayees = context_data_calc.get('montant_total_impayees', 0)
#             session_active.montant_total_depenses = context_data_calc.get('montant_total_depenses', 0)
#             session_active.montant_total_avances = context_data_calc.get('montant_total_avances', 0)
#             session_active.montant_decaisse = context_data_calc.get('montant_decaisse', 0)
#             session_active.chiffre_affaire = context_data_calc.get('chiffre_affaire', 0)
#             session_active.save()

#             # 3. Créer les détails archivés
#             creer_details_et_performance_pour_rapport(session_active, context_data_calc)
            
#             messages.success(request, f"La boîte est fermée ! Le rapport du {session_active.start_time.strftime('%d/%m/%Y %H:%M')} a été archivé.")

#         else:
#             messages.warning(request, "Action invalide ou l'état de la session n'a pas changé.")

#     return redirect('ventes:point_des_ventes')


# # ----------------------------------------------------------------------------------
# # VUE PRINCIPALE D'AFFICHAGE
# # ----------------------------------------------------------------------------------

# @login_required
# def point_des_ventes(request):
    
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
#     date_query_str = request.GET.get('date') 
    
#     context = {
#         "is_session_active": session_active is not None,
#         "current_session": session_active,
#         "rapports_historiques": None, 
#         "is_historical_view": False,
#     }

#     if session_active:
#         # --- CAS 1 : Session Active (Mode Temps Réel) ---
#         context["start_time"] = session_active.start_time
#         context["end_time"] = timezone.now()
#         context.update(calculer_ventes_en_temps_reel(context["start_time"], context["end_time"]))
#         return render(request, "ventes/point_des_ventes.html", context)
    
#     # --- CAS 2, 3, 4 : Session FERMÉE (Historique ou Liste Globale) ---

#     if date_query_str:
#         # Tente de parser d'abord comme DATETIME (recherche précise par heure et minute)
#         try:
#             date_time_obj = datetime.strptime(date_query_str, '%Y-%m-%dT%H:%M')
#             start_time_to_check = timezone.make_aware(date_time_obj)

#             # Chercher le rapport qui commence DANS cette minute
#             rapports_trouves = RapportVenteNocturne.objects.prefetch_related(
#                 'details_boissons', 
#                 'performance_personnel',
#                 'performance_personnel__personnel'
#             ).filter(
#                 start_time__gte=start_time_to_check, 
#                 start_time__lt=start_time_to_check + timedelta(minutes=1)      
#             ).first() 

#             if rapports_trouves:
#                 rapport = rapports_trouves
#             else:
#                 raise ValueError("Aucun rapport trouvé dans cette minute. Tentative de recherche par date seule.") 
            
#             # Affichage du rapport unique
#             context["is_historical_view"] = True
#             context["start_time"] = rapport.start_time
#             context["end_time"] = rapport.end_time
            
#             # CORRIGÉ : Utilisation des données du rapport
#             context.update({
#                 "montant_total_vente": rapport.montant_total_vente,
#                 "montant_total_impayees": rapport.montant_total_impayees,
#                 "montant_total_depenses": rapport.montant_total_depenses,
#                 "montant_total_avances": rapport.montant_total_avances,
#                 "montant_decaisse": rapport.montant_decaisse,
#                 "chiffre_affaire": rapport.chiffre_affaire,
#                 "ventes_produits": rapport.details_boissons.all(),
#                 "performance_personnel": rapport.performance_personnel.all()
#             })
#             return render(request, "ventes/point_des_ventes.html", context)

#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             # Si le format DATETIME a échoué, on essaie le format DATE (AAAA-MM-JJ)
#             date_only = parse_date(date_query_str.split('T')[0])
#             if date_only:
#                 # Filtrer tous les rapports archivés (is_active=False) pour ce jour.
#                 rapports_du_jour = RapportVenteNocturne.objects.filter(
#                     is_active=False,
#                     start_time__date=date_only
#                 ).order_by('-start_time')
                
#                 if rapports_du_jour.count() == 1:
#                     # Si un seul rapport, l'afficher directement
#                     unique_rapport = rapports_du_jour.first()
                    
#                     context["is_historical_view"] = True
#                     context["start_time"] = unique_rapport.start_time
#                     context["end_time"] = unique_rapport.end_time
#                     # On charge les données du rapport
#                     context.update({
#                         "montant_total_vente": unique_rapport.montant_total_vente,
#                         "montant_total_impayees": unique_rapport.montant_total_impayees,
#                         "montant_total_depenses": unique_rapport.montant_total_depenses,
#                         "montant_total_avances": unique_rapport.montant_total_avances,
#                         "montant_decaisse": unique_rapport.montant_decaisse,
#                         "chiffre_affaire": unique_rapport.chiffre_affaire,
#                         "ventes_produits": unique_rapport.details_boissons.all(),
#                         "performance_personnel": unique_rapport.performance_personnel.all()
#                     })
#                     return render(request, "ventes/point_des_ventes.html", context)
                
#                 elif rapports_du_jour.count() > 0:
#                     # Afficher la liste des rapports pour ce jour pour sélection
#                     context["rapports_historiques"] = rapports_du_jour
#                     messages.info(request, f"{rapports_du_jour.count()} sessions trouvées pour le {date_only.strftime('%d/%m/%Y')}. Veuillez sélectionner l'heure exacte.")
#                     return render(request, "ventes/point_des_ventes.html", context)
            
#             # Si on arrive ici, la date est invalide ou non trouvée
#             messages.error(request, "Rapport historique non trouvé ou format de date invalide.")
            
#     # --- CAS 4 : Pas de session active et pas de recherche (Affichage de l'historique global) ---
    
#     # Afficher la liste des 50 derniers rapports archivés
#     context["rapports_historiques"] = RapportVenteNocturne.objects.filter(is_active=False).order_by('-start_time')[:50]
    
#     # Pour éviter l'erreur de calcul quand la session est fermée sans recherche :
#     context.update({
#         "montant_total_vente": 0,
#         "montant_total_impayees": 0,
#         "montant_total_depenses": 0,
#         "montant_total_avances": 0,
#         "montant_decaisse": 0,
#         "chiffre_affaire": 0,
#         "ventes_produits": [],
#         "performance_personnel": []
#     })

#     return render(request, "ventes/point_des_ventes.html", context)


################










# ################  28 -10- 2025 ############

# from django.shortcuts import render, get_object_or_404, redirect
# from django.db.models import Q, Sum, F, Case, When, DecimalField
# from django.utils import timezone
# from datetime import timedelta, datetime, date
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.contrib import messages
# from django.utils.dateparse import parse_date

# # Importations des modèles nécessaires
# from depenses.models import Depense 
# from avances.models import Avance
# from commandes.models import Commande, CommandeItem
# from personnel.models import Personnel
# from .models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne


# # ----------------------------------------------------------------------------------
# # FONCTIONS DE CALCUL TEMPS RÉEL
# # ----------------------------------------------------------------------------------

# def calculer_ventes_detaillees_en_temps_reel(start_time, end_time):
#     # Les commandes sont filtrées par la session active
#     commandes_valides_ids = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     ).values_list('id', flat=True)

#     # CORRECTION : Utilisation de 'produit' au lieu de 'boisson'
#     ventes_produits_raw = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).values(
#         'produit__id',
#         'produit__nom', 
#         'produit__prix_vente'
#     ).annotate(
#         quantite_totale=Sum('quantite'), 
#         montant_total=Sum(F('quantite') * F('produit__prix_vente'))
#     ).order_by('-montant_total')

#     ventes_produits_list = []
#     for item in ventes_produits_raw:
#         # Création d'un objet "produit" factice pour compatibilité avec le template
#         produit_obj = type('Produit', (object,), {
#             'nom': item['produit__nom'], 
#             'id': item['produit__id']
#         })
#         ventes_produits_list.append({
#             'produit': produit_obj,
#             'prix_unitaire_au_moment_vente': item['produit__prix_vente'],
#             'quantite_totale': item['quantite_totale'],
#             'montant_total': item['montant_total'],
#         })
    
#     return ventes_produits_list


# def calculer_performance_personnel_en_temps_reel(start_time, end_time):
    
#     performance_data = {} 

#     # 1. Identifier tous les IDs du personnel concerné (vente ou avance)
#     venteurs_ids = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     ).values_list('personnel__id', flat=True)
    
#     # Avances filtrées par la session
#     avanceurs_ids = Avance.objects.filter(
#         date_avance__gte=start_time, 
#         date_avance__lt=end_time
#     ).values_list('personnel__id', flat=True)
    
#     # Utilisation correcte de 'venteurs_ids'
#     all_personnel_ids = list(set([id for id in venteurs_ids if id is not None] + [id for id in avanceurs_ids if id is not None]))
    
#     # 2. Récupérer toutes les instances Personnel en une seule requête pour le rôle
#     personnel_instances = {p.id: p for p in Personnel.objects.filter(id__in=all_personnel_ids)}

#     # 3. Initialisation des données pour chaque employé
#     for personnel_id, instance in personnel_instances.items():
#         performance_data[personnel_id] = {
#             'id': personnel_id,
#             'nom_complet': f"{instance.prenom} {instance.nom}",
#             'montant_vendu_total': 0,
#             'montant_impaye_personnel': 0,
#             'quantite_totale_produits_vendus': 0,
#             'details_produits_vendus': {},
#             'montant_total_avances_personnel': 0,
#             'personnel': instance,
#         }

#     # 4. Calcul des VENTES et IMPAYÉS
#     performance_globale_ventes = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee'],
#         personnel__id__in=all_personnel_ids
#     ).values('personnel__id').annotate(
#         montant_vendu_total=Sum(F('montant_total')),
#         montant_impaye_personnel=Sum(Case(
#             When(statut='impayee', then=F('montant_restant')),
#             default=0,
#             output_field=DecimalField(decimal_places=2)
#         )),
#     )

#     for perf in performance_globale_ventes:
#         personnel_id = perf['personnel__id']
        
#         commandes_de_ce_perso_ids = Commande.objects.filter(
#             date_validation__gte=start_time, 
#             date_validation__lt=end_time,
#             statut__in=['payer', 'impayee'],
#             personnel__id=personnel_id
#         ).values_list('id', flat=True)

#         # CORRIGÉ : 'produit__nom' au lieu de 'boisson__nom'
#         detail_ventes_produit = CommandeItem.objects.filter(
#             commande_id__in=commandes_de_ce_perso_ids
#         ).values('produit__nom').annotate(quantite=Sum('quantite'))

#         # CORRIGÉ : details_produits_vendus
#         details_produits = {
#             item['produit__nom']: item['quantite'] 
#             for item in detail_ventes_produit
#         }
#         quantite_totale_produits_vendus = sum(details_produits.values())
        
#         if personnel_id in performance_data:
#             performance_data[personnel_id].update({
#                 'montant_vendu_total': perf['montant_vendu_total'] or 0,
#                 'montant_impaye_personnel': perf['montant_impaye_personnel'] or 0,
#                 'quantite_totale_produits_vendus': quantite_totale_produits_vendus,
#                 'details_produits_vendus': details_produits,
#             })
        
#     # 5. Calcul des AVANCES
#     avances_personnel = Avance.objects.filter(
#         date_avance__gte=start_time, 
#         date_avance__lt=end_time
#     ).values('personnel__id').annotate(montant_avance=Sum('montant'))
    
#     for avance in avances_personnel:
#         personnel_id = avance['personnel__id']
#         if personnel_id in performance_data:
#             performance_data[personnel_id]['montant_total_avances_personnel'] = avance['montant_avance'] or 0

#     # 6. Finalisation et Tri
#     personnel_performance_list = sorted(
#         performance_data.values(), 
#         key=lambda x: x['montant_vendu_total'], 
#         reverse=True
#     )
    
#     return personnel_performance_list


# def calculer_ventes_en_temps_reel(start_time, end_time):
    
#     commandes_valides_qs = Commande.objects.filter(
#         date_validation__gte=start_time, 
#         date_validation__lt=end_time,
#         statut__in=['payer', 'impayee']
#     )
#     commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

#     # CORRIGÉ : ventes_produits au lieu de ventes_boissons
#     ventes_produits = calculer_ventes_detaillees_en_temps_reel(start_time, end_time)
#     performance_personnel = calculer_performance_personnel_en_temps_reel(start_time, end_time) 
    
#     # CORRIGÉ : 'produit__prix_vente' au lieu de 'boisson__prix_unitaire'
#     montant_total_vente_calc = CommandeItem.objects.filter(
#         commande_id__in=commandes_valides_ids
#     ).aggregate(
#         total=Sum(F('quantite') * F('produit__prix_vente'))
#     )['total'] or 0

#     montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
#     # Requêtes pour les Dépenses et Avances, filtrées par temps de session.
#     montant_total_depenses = Depense.objects.filter(date__gte=start_time, date__lt=end_time).aggregate(total=Sum('montant'))['total'] or 0
#     montant_total_avances = Avance.objects.filter(date_avance__gte=start_time, date_avance__lt=end_time).aggregate(total=Sum('montant'))['total'] or 0

#     montant_decaisse = montant_total_impayees + montant_total_depenses + montant_total_avances
#     chiffre_affaire = montant_total_vente_calc - montant_decaisse

#     return {
#         "montant_total_vente": montant_total_vente_calc,
#         "montant_total_impayees": montant_total_impayees,
#         "montant_total_depenses": montant_total_depenses,
#         "montant_total_avances": montant_total_avances,
#         "montant_decaisse": montant_decaisse,
#         "chiffre_affaire": chiffre_affaire,
#         "ventes_produits": ventes_produits,
#         "performance_personnel": performance_personnel, 
#     }


# # ----------------------------------------------------------------------------------
# # FONCTION D'ARCHIVAGE 
# # ----------------------------------------------------------------------------------

# def creer_details_et_performance_pour_rapport(rapport, context_data_calc):
#     """
#     Crée les DetailVenteBoisson et PerformancePersonnelNocturne pour un rapport donné
#     à partir des données calculées.
#     """
    
#     # Étape A : Sauvegarde des détails des produits
#     details_a_creer = []
    
#     # CORRIGÉ : context_data_calc['ventes_produits'] au lieu de ['ventes_boissons']
#     for item in context_data_calc['ventes_produits']:
#         produit_id_to_use = getattr(item['produit'], 'id', None)
        
#         if produit_id_to_use:
#             details_a_creer.append(
#                 DetailVenteBoisson(
#                     rapport=rapport,
#                     boisson_id=produit_id_to_use,
#                     quantite_totale=item['quantite_totale'],
#                     montant_total=item['montant_total'],
#                     prix_unitaire_au_moment_vente=item['prix_unitaire_au_moment_vente']
#                 )
#             )

#     DetailVenteBoisson.objects.bulk_create(details_a_creer)

#     # Étape B : Sauvegarde de la Performance du Personnel
#     performances_a_creer = []
#     for perf in context_data_calc['performance_personnel']:
#         performances_a_creer.append(
#             PerformancePersonnelNocturne(
#                 rapport=rapport,
#                 personnel_id=perf['id'], 
#                 montant_vendu_total=perf['montant_vendu_total'],
#                 montant_impaye_personnel=perf['montant_impaye_personnel'],
#                 # CORRIGÉ : quantite_totale_produits_vendus
#                 quantite_totale_boissons_vendues=perf['quantite_totale_produits_vendus'],
#                 montant_total_avances_personnel=perf['montant_total_avances_personnel'],
#                 # CORRIGÉ : details_produits_vendus
#                 details_boissons_vendues_archive=perf['details_produits_vendus']
#             )
#         )
#     PerformancePersonnelNocturne.objects.bulk_create(performances_a_creer)


# from personnel.decorators import role_required

# # =============================================================================
# # DÉFINITION DES RÔLES AUTORISÉS
# # =============================================================================

# # Rôles qui peuvent ouvrir une session de vente
# ROLES_OUVERTURE_SESSION = ['boss', 'secretaire', 'caissier', 'admin']

# # Rôles qui peuvent fermer une session de vente 
# # (Peut être différent de l'ouverture si besoin)
# ROLES_FERMETURE_SESSION = ['boss', 'secretaire', 'caissier', 'admin']

# ROLES_VISITE_VENTES = ['boss', 'secretaire', 'caissier']




# # =============================================================================
# # FONCTIONS UTILITAIRES POUR LA GESTION DES PERMISSIONS
# # =============================================================================

# def _is_user_in_allowed_roles(user, allowed_roles):
#     """
#     Vérifie si un utilisateur a accès basé sur ses rôles.
#     """
#     if user.is_superuser:
#         return True
    
#     if hasattr(user, 'personnel_profile'):
#         try:
#             user_role = user.personnel_profile.role 
#             return user_role in allowed_roles
#         except AttributeError:
#             return False
#     return False

# def user_can_ouvrir_session(user):
#     """Vérifie si l'utilisateur peut ouvrir une session de vente."""
#     return _is_user_in_allowed_roles(user, ROLES_OUVERTURE_SESSION)

# def user_can_fermer_session(user):
#     """Vérifie si l'utilisateur peut fermer une session de vente."""
#     return _is_user_in_allowed_roles(user, ROLES_FERMETURE_SESSION)

# def get_user_display_name(user):
#     """
#     Retourne le nom d'affichage de l'utilisateur.
#     """
#     if hasattr(user, 'personnel_profile'):
#         try:
#             personnel = user.personnel_profile
#             return f"{personnel.prenom} {personnel.nom}"
#         except (AttributeError, ObjectDoesNotExist):
#             pass
    
#     return user.get_full_name() or user.username

# def user_owns_active_session(user):
#     """
#     Vérifie si l'utilisateur est le propriétaire de la session active.
    
#     RÈGLE DE SÉCURITÉ ABSOLUE :
#     - Seul le propriétaire de la session peut la fermer
#     - Même les superutilisateurs ne peuvent pas fermer une session qu'ils n'ont pas ouverte
#     - Garantit une traçabilité et responsabilité complètes
#     """
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
#     if not session_active:
#         return False
    
#     try:
#         user_personnel = Personnel.objects.get(user=user)
#         return session_active.caissier == user_personnel
#     except Personnel.DoesNotExist:
#         return False

# # =============================================================================
# # VUE POUR OUVRIR/FERMER LA SESSION - SÉCURITÉ ABSOLUE
# # =============================================================================

# @login_required
# def toggle_session(request):
#     """
#     Ouvre ou ferme une session de vente avec sécurité absolue.
    
#     RÈGLES DE SÉCURITÉ ABSOLUES :
#     1. Seul l'utilisateur qui a ouvert une session peut la fermer
#     2. Cette règle s'applique à TOUT LE MONDE, y compris les superutilisateurs
#     3. Aucune exception n'est permise pour garantir la traçabilité
#     4. Un profil Personnel est obligatoire pour toute action
    
#     Principe : "Celui qui ouvre, ferme"
#     """
    
#     # === VÉRIFICATION DE LA MÉTHODE HTTP ===
#     if request.method != 'POST':
#         messages.error(request, "❌ Erreur : Action non autorisée.")
#         return redirect('ventes:point_des_ventes')

#     action = request.POST.get('action')
#     user = request.user
    
#     # === VÉRIFICATION OBLIGATOIRE DU PROFIL PERSONNEL ===
#     # Sans profil Personnel, aucune action n'est permise (sécurité absolue)
#     try:
#         caissier_personnel = Personnel.objects.get(user=user)
#     except Personnel.DoesNotExist:
#         messages.error(request, 
#             "❌ Erreur de sécurité : Votre compte utilisateur n'est pas associé à un profil Personnel. "
#             "Cette association est obligatoire pour ouvrir ou fermer une session. "
#             "Veuillez contacter l'administrateur système."
#         )
#         return redirect('ventes:point_des_ventes')
#     except Personnel.MultipleObjectsReturned:
#         # Cas d'erreur - on prend le premier profil
#         caissier_personnel = Personnel.objects.filter(user=user).first()
#         messages.warning(request, "⚠️ Attention : Plusieurs profils trouvés. Utilisation du premier profil.")

#     # === VÉRIFICATION DES PERMISSIONS GÉNÉRIQUES ===
#     if action == 'ouvrir' and not user_can_ouvrir_session(user):
#         messages.error(request, "❌ Accès refusé : Permissions insuffisantes pour ouvrir une session.")
#         return redirect('ventes:point_des_ventes')
    
#     if action == 'fermer' and not user_can_fermer_session(user):
#         messages.error(request, "❌ Accès refusé : Permissions insuffisantes pour fermer une session.")
#         return redirect('ventes:point_des_ventes')

#     # === VÉRIFICATION DE L'ÉTAT DE LA SESSION ===
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()

#     with transaction.atomic():
#         # === CAS 1 : OUVERTURE D'UNE NOUVELLE SESSION ===
#         if action == 'ouvrir' and not session_active:
#             # CRÉATION DE LA SESSION AVEC RESPONSABILITÉ ABSOLUE
#             nouvelle_session = RapportVenteNocturne.objects.create(
#                 start_time=timezone.now(),
#                 caissier=caissier_personnel,  # CRITIQUE : Stocke le responsable unique
#                 is_active=True,
#             )
            
#             nom_affiche = get_user_display_name(user)
#             messages.success(request, 
#                 f"✅ SESSION OUVERTE avec succès par {nom_affiche} !\n"
#                 f"🔒 RÈGLE DE SÉCURITÉ : Seul {nom_affiche} pourra fermer cette session.\n"
#                 f"⏰ Début : {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
#             )
        
#         # === CAS 2 : FERMETURE DE SESSION - SÉCURITÉ ABSOLUE ===
#         elif action == 'fermer' and session_active:
            
#             # === VÉRIFICATION CRITIQUE DE PROPRIÉTÉ ===
#             # RÈGLE ABSOLUE : Seul le propriétaire peut fermer, sans exception
#             if session_active.caissier != caissier_personnel:
#                 # Récupère les informations pour le message d'erreur
#                 proprietaire_nom = get_user_display_name(session_active.caissier.user) if session_active.caissier else "Profil inconnu"
#                 utilisateur_actuel = get_user_display_name(user)
#                 debut_session = session_active.start_time.strftime('%d/%m/%Y à %H:%M')
                
#                 messages.error(request, 
#                     f"🚨 VIOLATION DE SÉCURITÉ DÉTECTÉE !\n"
#                     f"• Session ouverte par : {proprietaire_nom}\n"
#                     f"• Date d'ouverture : {debut_session}\n"
#                     f"• Vous êtes connecté en tant que : {utilisateur_actuel}\n"
#                     f"🔒 RÈGLE ABSOLUE : Seul {proprietaire_nom} peut fermer cette session.\n"
#                     f"📞 Contactez {proprietaire_nom} pour fermer la session."
#                 )
#                 return redirect('ventes:point_des_ventes')
                
#             # === PROCESSUS DE FERMETURE AUTORISÉ ===
#             # Seulement si l'utilisateur est le propriétaire de la session
#             end_time = timezone.now()
#             duree_session = end_time - session_active.start_time
#             heures, reste = divmod(duree_session.total_seconds(), 3600)
#             minutes, secondes = divmod(reste, 60)
            
#             context_data_calc = calculer_ventes_en_temps_reel(session_active.start_time, end_time)

#             # Mise à jour du rapport
#             session_active.end_time = end_time
#             session_active.is_active = False
#             session_active.montant_total_vente = context_data_calc.get('montant_total_vente', 0)
#             session_active.montant_total_impayees = context_data_calc.get('montant_total_impayees', 0)
#             session_active.montant_total_depenses = context_data_calc.get('montant_total_depenses', 0)
#             session_active.montant_total_avances = context_data_calc.get('montant_total_avances', 0)
#             session_active.montant_decaisse = context_data_calc.get('montant_decaisse', 0)
#             session_active.chiffre_affaire = context_data_calc.get('chiffre_affaire', 0)
#             session_active.save()

#             # Création des détails archivés
#             creer_details_et_performance_pour_rapport(session_active, context_data_calc)
            
#             messages.success(request, 
#                 f"✅ SESSION FERMÉE avec succès !\n"
#                 f"• Période : {session_active.start_time.strftime('%d/%m/%Y %H:%M')} → {end_time.strftime('%d/%m/%Y %H:%M')}\n"
#                 f"• Durée : {int(heures)}h {int(minutes)}min\n"
#                 f"• Chiffre d'affaire : {session_active.chiffre_affaire|floatformat:0} F\n"
#                 f"📊 Rapport archivé et sécurisé."
#             )

#         # === CAS 3 : ACTIONS INVALIDES ===
#         else:
#             messages.warning(request, "⚠️ Action impossible : État de session incohérent ou action non valide.")

#     return redirect('ventes:point_des_ventes')


# # =============================================================================
# # VUE PRINCIPALE D'AFFICHAGE - AVEC INDICATIONS DE SÉCURITÉ RENFORCÉES
# # =============================================================================

# @login_required
# def point_des_ventes(request):
#     """
#     Vue principale du point des ventes avec sécurité absolue.
#     """
#     session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
#     date_query_str = request.GET.get('date') 
#     user = request.user
    
#     # === VÉRIFICATION DES PERMISSIONS AVEC SÉCURITÉ ABSOLUE ===
    
#     # Permission d'ouverture : droits génériques + profil Personnel
#     can_ouvrir_session = False
#     try:
#         Personnel.objects.get(user=user)
#         can_ouvrir_session = user_can_ouvrir_session(user)
#     except Personnel.DoesNotExist:
#         can_ouvrir_session = False
    
#     # Permission de fermeture : doit être le propriétaire de la session active
#     can_fermer_session = user_owns_active_session(user)
    
#     # Vérification si l'utilisateur a un profil Personnel
#     user_has_personnel_profile = hasattr(user, 'personnel_profile')
    
#     # Récupération du nom du propriétaire de la session pour l'affichage
#     session_owner_name = None
#     if session_active and session_active.caissier:
#         session_owner_name = get_user_display_name(session_active.caissier.user)

#     context = {
#         "is_session_active": session_active is not None,
#         "current_session": session_active,
#         "rapports_historiques": None, 
#         "is_historical_view": False,
#         "can_ouvrir_session": can_ouvrir_session,
#         "can_fermer_session": can_fermer_session,
#         "user_has_personnel_profile": user_has_personnel_profile,
#         "session_owner_name": session_owner_name,
#         "current_user_name": get_user_display_name(user),
#     }

#     # CAS 1 : SESSION ACTIVE
#     if session_active:
#         context["start_time"] = session_active.start_time
#         context["end_time"] = timezone.now()
#         context.update(calculer_ventes_en_temps_reel(context["start_time"], context["end_time"]))
#         return render(request, "ventes/point_des_ventes.html", context)
    
#     # CAS 2, 3, 4 : SESSION FERMÉE - HISTORIQUE
#     if date_query_str:
#         try:
#             date_time_obj = datetime.strptime(date_query_str, '%Y-%m-%dT%H:%M')
#             start_time_to_check = timezone.make_aware(date_time_obj)

#             rapport = RapportVenteNocturne.objects.prefetch_related(
#                 'details_boissons', 
#                 'performance_personnel',
#                 'performance_personnel__personnel'
#             ).filter(
#                 start_time__gte=start_time_to_check, 
#                 start_time__lt=start_time_to_check + timedelta(minutes=1)      
#             ).first() 

#             if rapport:
#                 context.update({
#                     "is_historical_view": True,
#                     "start_time": rapport.start_time,
#                     "end_time": rapport.end_time,
#                     "montant_total_vente": rapport.montant_total_vente,
#                     "montant_total_impayees": rapport.montant_total_impayees,
#                     "montant_total_depenses": rapport.montant_total_depenses,
#                     "montant_total_avances": rapport.montant_total_avances,
#                     "montant_decaisse": rapport.montant_decaisse,
#                     "chiffre_affaire": rapport.chiffre_affaire,
#                     "ventes_produits": rapport.details_boissons.all(),
#                     "performance_personnel": rapport.performance_personnel.all()
#                 })
#                 return render(request, "ventes/point_des_ventes.html", context)
#             else:
#                 raise ValueError("Aucun rapport trouvé.")

#         except (RapportVenteNocturne.DoesNotExist, ValueError):
#             date_only = parse_date(date_query_str.split('T')[0])
#             if date_only:
#                 rapports_du_jour = RapportVenteNocturne.objects.filter(
#                     is_active=False,
#                     start_time__date=date_only
#                 ).order_by('-start_time')
                
#                 if rapports_du_jour.count() == 1:
#                     unique_rapport = rapports_du_jour.first()
#                     context.update({
#                         "is_historical_view": True,
#                         "start_time": unique_rapport.start_time,
#                         "end_time": unique_rapport.end_time,
#                         "montant_total_vente": unique_rapport.montant_total_vente,
#                         "montant_total_impayees": unique_rapport.montant_total_impayees,
#                         "montant_total_depenses": unique_rapport.montant_total_depenses,
#                         "montant_total_avances": unique_rapport.montant_total_avances,
#                         "montant_decaisse": unique_rapport.montant_decaisse,
#                         "chiffre_affaire": unique_rapport.chiffre_affaire,
#                         "ventes_produits": unique_rapport.details_boissons.all(),
#                         "performance_personnel": unique_rapport.performance_personnel.all()
#                     })
#                     return render(request, "ventes/point_des_ventes.html", context)
                
#                 elif rapports_du_jour.count() > 0:
#                     context["rapports_historiques"] = rapports_du_jour
#                     messages.info(request, f"{rapports_du_jour.count()} sessions trouvées pour le {date_only.strftime('%d/%m/%Y')}.")
#                     return render(request, "ventes/point_des_ventes.html", context)
            
#             messages.error(request, "❌ Rapport historique non trouvé.")
            
#     # CAS 4 : HISTORIQUE GLOBAL
#     context["rapports_historiques"] = RapportVenteNocturne.objects.filter(
#         is_active=False
#     ).order_by('-start_time')[:50]
    
#     # Valeurs par défaut
#     context.update({
#         "montant_total_vente": 0,
#         "montant_total_impayees": 0,
#         "montant_total_depenses": 0,
#         "montant_total_avances": 0,
#         "montant_decaisse": 0,
#         "chiffre_affaire": 0,
#         "ventes_produits": [],
#         "performance_personnel": []
#     })

#     return render(request, "ventes/point_des_ventes.html", context)


############## Ajout des marges


from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Sum, F, Case, When, DecimalField
from django.utils import timezone
from datetime import timedelta, datetime, date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.core.exceptions import ObjectDoesNotExist

# Importations des modèles nécessaires
from depenses.models import Depense 
from avances.models import Avance
from commandes.models import Commande, CommandeItem
from personnel.models import Personnel
from produits.models import Produit
from .models import RapportVenteNocturne, DetailVenteProduit, PerformancePersonnelNocturne


# ----------------------------------------------------------------------------------
# FONCTIONS DE CALCUL TEMPS RÉEL AVEC MARGES
# ----------------------------------------------------------------------------------

def calculer_ventes_detaillees_en_temps_reel(start_time, end_time):
    # Les commandes sont filtrées par la session active
    commandes_valides_ids = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    ).values_list('id', flat=True)

    # Calcul des ventes avec marges
    ventes_produits_raw = CommandeItem.objects.filter(
        commande_id__in=commandes_valides_ids
    ).values(
        'produit__id',
        'produit__nom', 
        'produit__prix_vente',
        'produit__prix_achat',
        'produit__marge'
    ).annotate(
        quantite_totale=Sum('quantite'), 
        montant_total=Sum(F('quantite') * F('produit__prix_vente')),
        marge_totale=Sum(F('quantite') * F('produit__marge'))
    ).order_by('-montant_total')

    ventes_produits_list = []
    for item in ventes_produits_raw:
        # Création d'un objet "produit" factice pour compatibilité avec le template
        produit_obj = type('Produit', (object,), {
            'nom': item['produit__nom'], 
            'id': item['produit__id'],
            'prix_vente': item['produit__prix_vente'],
            'prix_achat': item['produit__prix_achat'],
            'marge': item['produit__marge']
        })
        ventes_produits_list.append({
            'produit': produit_obj,
            'prix_unitaire_au_moment_vente': item['produit__prix_vente'],
            'quantite_totale': item['quantite_totale'],
            'montant_total': item['montant_total'],
            'marge_totale_produit': item['marge_totale'],
            'marge_unitaire_au_moment_vente': item['produit__marge'],
        })
    
    return ventes_produits_list


def calculer_performance_personnel_en_temps_reel(start_time, end_time):
    
    performance_data = {} 

    # 1. Identifier tous les IDs du personnel concerné (vente ou avance)
    venteurs_ids = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    ).values_list('personnel__id', flat=True)
    
    # Avances filtrées par la session
    avanceurs_ids = Avance.objects.filter(
        date_avance__gte=start_time, 
        date_avance__lt=end_time
    ).values_list('personnel__id', flat=True)
    
    # Utilisation correcte de 'venteurs_ids'
    all_personnel_ids = list(set([id for id in venteurs_ids if id is not None] + [id for id in avanceurs_ids if id is not None]))
    
    # 2. Récupérer toutes les instances Personnel en une seule requête pour le rôle
    personnel_instances = {p.id: p for p in Personnel.objects.filter(id__in=all_personnel_ids)}

    # 3. Initialisation des données pour chaque employé
    for personnel_id, instance in personnel_instances.items():
        performance_data[personnel_id] = {
            'id': personnel_id,
            'nom_complet': f"{instance.prenom} {instance.nom}",
            'montant_vendu_total': 0,
            'montant_impaye_personnel': 0,
            'quantite_totale_produits_vendus': 0,
            'details_produits_vendus': {},
            'montant_total_avances_personnel': 0,
            'personnel': instance,
        }

    # 4. Calcul des VENTES et IMPAYÉS
    performance_globale_ventes = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee'],
        personnel__id__in=all_personnel_ids
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
        
        commandes_de_ce_perso_ids = Commande.objects.filter(
            date_validation__gte=start_time, 
            date_validation__lt=end_time,
            statut__in=['payer', 'impayee'],
            personnel__id=personnel_id
        ).values_list('id', flat=True)

        detail_ventes_produit = CommandeItem.objects.filter(
            commande_id__in=commandes_de_ce_perso_ids
        ).values('produit__nom').annotate(quantite=Sum('quantite'))

        details_produits = {
            item['produit__nom']: item['quantite'] 
            for item in detail_ventes_produit
        }
        quantite_totale_produits_vendus = sum(details_produits.values())
        
        if personnel_id in performance_data:
            performance_data[personnel_id].update({
                'montant_vendu_total': perf['montant_vendu_total'] or 0,
                'montant_impaye_personnel': perf['montant_impaye_personnel'] or 0,
                'quantite_totale_produits_vendus': quantite_totale_produits_vendus,
                'details_produits_vendus': details_produits,
            })
        
    # 5. Calcul des AVANCES
    avances_personnel = Avance.objects.filter(
        date_avance__gte=start_time, 
        date_avance__lt=end_time
    ).values('personnel__id').annotate(montant_avance=Sum('montant'))
    
    for avance in avances_personnel:
        personnel_id = avance['personnel__id']
        if personnel_id in performance_data:
            performance_data[personnel_id]['montant_total_avances_personnel'] = avance['montant_avance'] or 0

    # 6. Finalisation et Tri
    personnel_performance_list = sorted(
        performance_data.values(), 
        key=lambda x: x['montant_vendu_total'], 
        reverse=True
    )
    
    return personnel_performance_list


def calculer_ventes_en_temps_reel(start_time, end_time):
    
    commandes_valides_qs = Commande.objects.filter(
        date_validation__gte=start_time, 
        date_validation__lt=end_time,
        statut__in=['payer', 'impayee']
    )
    commandes_valides_ids = commandes_valides_qs.values_list('id', flat=True)

    ventes_produits = calculer_ventes_detaillees_en_temps_reel(start_time, end_time)
    performance_personnel = calculer_performance_personnel_en_temps_reel(start_time, end_time) 
    
    # Calcul du chiffre d'affaire (total des ventes)
    chiffre_affaire_calc = CommandeItem.objects.filter(
        commande_id__in=commandes_valides_ids
    ).aggregate(
        total=Sum(F('quantite') * F('produit__prix_vente'))
    )['total'] or 0

    # Calcul de la marge totale
    marge_totale_calc = CommandeItem.objects.filter(
        commande_id__in=commandes_valides_ids
    ).aggregate(
        total=Sum(F('quantite') * F('produit__marge'))
    )['total'] or 0

    montant_total_impayees = commandes_valides_qs.filter(statut='impayee').aggregate(total=Sum('montant_restant'))['total'] or 0
    
    # Requêtes pour les Dépenses et Avances, filtrées par temps de session.
    montant_total_depenses = Depense.objects.filter(date__gte=start_time, date__lt=end_time).aggregate(total=Sum('montant'))['total'] or 0
    montant_total_avances = Avance.objects.filter(date_avance__gte=start_time, date_avance__lt=end_time).aggregate(total=Sum('montant'))['total'] or 0

    # NOUVELLE LOGIQUE : montant_decaisse = Dépenses + Avances (sans impayés)
    montant_decaisse = montant_total_depenses + montant_total_avances
    
    # NOUVELLE LOGIQUE : benefice_net = Marge Totale - Dépenses
    benefice_net = marge_totale_calc - montant_total_depenses

    return {
        # NOUVELLE TERMINOLOGIE
        "chiffre_affaire": chiffre_affaire_calc,
        "marge_totale": marge_totale_calc,
        "benefice_net": benefice_net,
        
        # CONSERVÉS
        "montant_total_impayees": montant_total_impayees,
        "montant_total_depenses": montant_total_depenses,
        "montant_total_avances": montant_total_avances,
        "montant_decaisse": montant_decaisse,
        
        # Données détaillées
        "ventes_produits": ventes_produits,
        "performance_personnel": performance_personnel, 
    }


# ----------------------------------------------------------------------------------
# FONCTION D'ARCHIVAGE AVEC MARGES
# ----------------------------------------------------------------------------------

def creer_details_et_performance_pour_rapport(rapport, context_data_calc):
    """
    Crée les DetailVenteProduit et PerformancePersonnelNocturne pour un rapport donné
    à partir des données calculées avec les marges.
    """
    
    # Étape A : Sauvegarde des détails des produits avec marges
    details_a_creer = []
    
    for item in context_data_calc['ventes_produits']:
        produit_id_to_use = getattr(item['produit'], 'id', None)
        
        if produit_id_to_use:
            details_a_creer.append(
                DetailVenteProduit(
                    rapport=rapport,
                    produit_id=produit_id_to_use,
                    quantite_totale=item['quantite_totale'],
                    montant_total=item['montant_total'],
                    marge_totale_produit=item['marge_totale_produit'],
                    prix_unitaire_au_moment_vente=item['prix_unitaire_au_moment_vente'],
                    marge_unitaire_au_moment_vente=item['marge_unitaire_au_moment_vente']
                )
            )

    DetailVenteProduit.objects.bulk_create(details_a_creer)

    # Étape B : Sauvegarde de la Performance du Personnel
    performances_a_creer = []
    for perf in context_data_calc['performance_personnel']:
        performances_a_creer.append(
            PerformancePersonnelNocturne(
                rapport=rapport,
                personnel_id=perf['id'], 
                montant_vendu_total=perf['montant_vendu_total'],
                montant_impaye_personnel=perf['montant_impaye_personnel'],
                quantite_totale_produits_vendus=perf['quantite_totale_produits_vendus'],
                montant_total_avances_personnel=perf['montant_total_avances_personnel'],
                details_produits_vendus_archive=perf['details_produits_vendus']
            )
        )
    PerformancePersonnelNocturne.objects.bulk_create(performances_a_creer)


# =============================================================================
# DÉFINITION DES RÔLES AUTORISÉS
# =============================================================================

ROLES_OUVERTURE_SESSION = ['boss', 'secretaire', 'caissier', 'admin']
ROLES_FERMETURE_SESSION = ['boss', 'secretaire', 'caissier', 'admin']
ROLES_VISITE_VENTES = ['boss', 'secretaire', 'caissier']

# =============================================================================
# FONCTIONS UTILITAIRES POUR LA GESTION DES PERMISSIONS
# =============================================================================

def _is_user_in_allowed_roles(user, allowed_roles):
    """
    Vérifie si un utilisateur a accès basé sur ses rôles.
    """
    if user.is_superuser:
        return True
    
    if hasattr(user, 'personnel_profile'):
        try:
            user_role = user.personnel_profile.role 
            return user_role in allowed_roles
        except AttributeError:
            return False
    return False

def user_can_ouvrir_session(user):
    """Vérifie si l'utilisateur peut ouvrir une session de vente."""
    return _is_user_in_allowed_roles(user, ROLES_OUVERTURE_SESSION)

def user_can_fermer_session(user):
    """Vérifie si l'utilisateur peut fermer une session de vente."""
    return _is_user_in_allowed_roles(user, ROLES_FERMETURE_SESSION)

def get_user_display_name(user):
    """
    Retourne le nom d'affichage de l'utilisateur.
    """
    if hasattr(user, 'personnel_profile'):
        try:
            personnel = user.personnel_profile
            return f"{personnel.prenom} {personnel.nom}"
        except (AttributeError, ObjectDoesNotExist):
            pass
    
    return user.get_full_name() or user.username

def user_owns_active_session(user):
    """
    Vérifie si l'utilisateur est le propriétaire de la session active.
    """
    session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
    if not session_active:
        return False
    
    try:
        user_personnel = Personnel.objects.get(user=user)
        return session_active.caissier == user_personnel
    except Personnel.DoesNotExist:
        return False

# =============================================================================
# VUE POUR OUVRIR/FERMER LA SESSION - SÉCURITÉ ABSOLUE
# =============================================================================
@login_required
def toggle_session(request):
    """
    Ouvre ou ferme une session de vente avec sécurité absolue.
    """
    
    if request.method != 'POST':
        messages.error(request, "❌ Erreur : Action non autorisée.")
        return redirect('ventes:point_des_ventes')

    action = request.POST.get('action')
    user = request.user
    
    try:
        caissier_personnel = Personnel.objects.get(user=user)
    except Personnel.DoesNotExist:
        messages.error(request, 
            "❌ Erreur de sécurité : Votre compte utilisateur n'est pas associé à un profil Personnel. "
            "Cette association est obligatoire pour ouvrir ou fermer une session. "
            "Veuillez contacter l'administrateur système."
        )
        return redirect('ventes:point_des_ventes')
    except Personnel.MultipleObjectsReturned:
        caissier_personnel = Personnel.objects.filter(user=user).first()
        messages.warning(request, "⚠️ Attention : Plusieurs profils trouvés. Utilisation du premier profil.")

    if action == 'ouvrir' and not user_can_ouvrir_session(user):
        messages.error(request, "❌ Accès refusé : Permissions insuffisantes pour ouvrir une session.")
        return redirect('ventes:point_des_ventes')
    
    if action == 'fermer' and not user_can_fermer_session(user):
        messages.error(request, "❌ Accès refusé : Permissions insuffisantes pour fermer une session.")
        return redirect('ventes:point_des_ventes')

    session_active = RapportVenteNocturne.objects.filter(is_active=True).first()

    with transaction.atomic():
        if action == 'ouvrir' and not session_active:
            nouvelle_session = RapportVenteNocturne.objects.create(
                start_time=timezone.now(),
                caissier=caissier_personnel,
                is_active=True,
            )
            
            nom_affiche = get_user_display_name(user)
            messages.success(request, 
                f"✅ SESSION OUVERTE avec succès par {nom_affiche} !\n"
                f"🔒 RÈGLE DE SÉCURITÉ : Seul {nom_affiche} pourra fermer cette session.\n"
                f"⏰ Début : {timezone.now().strftime('%d/%m/%Y à %H:%M')}"
            )
        
        elif action == 'fermer' and session_active:
            if session_active.caissier != caissier_personnel:
                proprietaire_nom = get_user_display_name(session_active.caissier.user) if session_active.caissier else "Profil inconnu"
                utilisateur_actuel = get_user_display_name(user)
                debut_session = session_active.start_time.strftime('%d/%m/%Y à %H:%M')
                
                messages.error(request, 
                    f"🚨 VIOLATION DE SÉCURITÉ DÉTECTÉE !\n"
                    f"• Session ouverte par : {proprietaire_nom}\n"
                    f"• Date d'ouverture : {debut_session}\n"
                    f"• Vous êtes connecté en tant que : {utilisateur_actuel}\n"
                    f"🔒 RÈGLE ABSOLUE : Seul {proprietaire_nom} peut fermer cette session.\n"
                    f"📞 Contactez {proprietaire_nom} pour fermer la session."
                )
                return redirect('ventes:point_des_ventes')
                
            end_time = timezone.now()
            duree_session = end_time - session_active.start_time
            heures, reste = divmod(duree_session.total_seconds(), 3600)
            minutes, secondes = divmod(reste, 60)
            
            context_data_calc = calculer_ventes_en_temps_reel(session_active.start_time, end_time)

            # Mise à jour avec la nouvelle terminologie
            session_active.end_time = end_time
            session_active.is_active = False
            session_active.chiffre_affaire = context_data_calc.get('chiffre_affaire', 0)
            session_active.marge_totale = context_data_calc.get('marge_totale', 0)
            session_active.montant_total_impayees = context_data_calc.get('montant_total_impayees', 0)
            session_active.montant_total_depenses = context_data_calc.get('montant_total_depenses', 0)
            session_active.montant_total_avances = context_data_calc.get('montant_total_avances', 0)
            session_active.montant_decaisse = context_data_calc.get('montant_decaisse', 0)
            session_active.benefice_net = context_data_calc.get('benefice_net', 0)
            session_active.save()

            creer_details_et_performance_pour_rapport(session_active, context_data_calc)
            
            # CORRECTION : Utiliser format Python au lieu du filtre Django floatformat
            messages.success(request, 
                f"✅ SESSION FERMÉE avec succès !\n"
                f"• Période : {session_active.start_time.strftime('%d/%m/%Y %H:%M')} → {end_time.strftime('%d/%m/%Y %H:%M')}\n"
                f"• Durée : {int(heures)}h {int(minutes)}min\n"
                f"• Chiffre d'affaire : {float(session_active.chiffre_affaire):.0f} F\n"
                f"📊 Rapport archivé et sécurisé."
            )

        else:
            messages.warning(request, "⚠️ Action impossible : État de session incohérent ou action non valide.")

    return redirect('ventes:point_des_ventes')

# =============================================================================
# VUE PRINCIPALE D'AFFICHAGE
# =============================================================================

@login_required
def point_des_ventes(request):
    """
    Vue principale du point des ventes avec sécurité absolue.
    """
    session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
    date_query_str = request.GET.get('date') 
    user = request.user
    
    can_ouvrir_session = False
    try:
        Personnel.objects.get(user=user)
        can_ouvrir_session = user_can_ouvrir_session(user)
    except Personnel.DoesNotExist:
        can_ouvrir_session = False
    
    can_fermer_session = user_owns_active_session(user)
    user_has_personnel_profile = hasattr(user, 'personnel_profile')
    
    session_owner_name = None
    if session_active and session_active.caissier:
        session_owner_name = get_user_display_name(session_active.caissier.user)

    context = {
        "is_session_active": session_active is not None,
        "current_session": session_active,
        "rapports_historiques": None, 
        "is_historical_view": False,
        "can_ouvrir_session": can_ouvrir_session,
        "can_fermer_session": can_fermer_session,
        "user_has_personnel_profile": user_has_personnel_profile,
        "session_owner_name": session_owner_name,
        "current_user_name": get_user_display_name(user),
    }

    if session_active:
        context["start_time"] = session_active.start_time
        context["end_time"] = timezone.now()
        context.update(calculer_ventes_en_temps_reel(context["start_time"], context["end_time"]))
        return render(request, "ventes/point_des_ventes.html", context)
    
    if date_query_str:
        try:
            date_time_obj = datetime.strptime(date_query_str, '%Y-%m-%dT%H:%M')
            start_time_to_check = timezone.make_aware(date_time_obj)

            rapport = RapportVenteNocturne.objects.prefetch_related(
                'details_produits', 
                'performance_personnel',
                'performance_personnel__personnel'
            ).filter(
                start_time__gte=start_time_to_check, 
                start_time__lt=start_time_to_check + timedelta(minutes=1)      
            ).first() 

            if rapport:
                context.update({
                    "is_historical_view": True,
                    "start_time": rapport.start_time,
                    "end_time": rapport.end_time,
                    "chiffre_affaire": rapport.chiffre_affaire,
                    "marge_totale": rapport.marge_totale,
                    "montant_total_impayees": rapport.montant_total_impayees,
                    "montant_total_depenses": rapport.montant_total_depenses,
                    "montant_total_avances": rapport.montant_total_avances,
                    "montant_decaisse": rapport.montant_decaisse,
                    "benefice_net": rapport.benefice_net,
                    "ventes_produits": rapport.details_produits.all(),
                    "performance_personnel": rapport.performance_personnel.all()
                })
                return render(request, "ventes/point_des_ventes.html", context)
            else:
                raise ValueError("Aucun rapport trouvé.")

        except (RapportVenteNocturne.DoesNotExist, ValueError):
            date_only = parse_date(date_query_str.split('T')[0])
            if date_only:
                rapports_du_jour = RapportVenteNocturne.objects.filter(
                    is_active=False,
                    start_time__date=date_only
                ).order_by('-start_time')
                
                if rapports_du_jour.count() == 1:
                    unique_rapport = rapports_du_jour.first()
                    context.update({
                        "is_historical_view": True,
                        "start_time": unique_rapport.start_time,
                        "end_time": unique_rapport.end_time,
                        "chiffre_affaire": unique_rapport.chiffre_affaire,
                        "marge_totale": unique_rapport.marge_totale,
                        "montant_total_impayees": unique_rapport.montant_total_impayees,
                        "montant_total_depenses": unique_rapport.montant_total_depenses,
                        "montant_total_avances": unique_rapport.montant_total_avances,
                        "montant_decaisse": unique_rapport.montant_decaisse,
                        "benefice_net": unique_rapport.benefice_net,
                        "ventes_produits": unique_rapport.details_produits.all(),
                        "performance_personnel": unique_rapport.performance_personnel.all()
                    })
                    return render(request, "ventes/point_des_ventes.html", context)
                
                elif rapports_du_jour.count() > 0:
                    context["rapports_historiques"] = rapports_du_jour
                    messages.info(request, f"{rapports_du_jour.count()} sessions trouvées pour le {date_only.strftime('%d/%m/%Y')}.")
                    return render(request, "ventes/point_des_ventes.html", context)
            
            messages.error(request, "❌ Rapport historique non trouvé.")
            
    context["rapports_historiques"] = RapportVenteNocturne.objects.filter(
        is_active=False
    ).order_by('-start_time')[:50]
    
    context.update({
        "chiffre_affaire": 0,
        "marge_totale": 0,
        "benefice_net": 0,
        "montant_total_impayees": 0,
        "montant_total_depenses": 0,
        "montant_total_avances": 0,
        "montant_decaisse": 0,
        "ventes_produits": [],
        "performance_personnel": []
    })

    return render(request, "ventes/point_des_ventes.html", context)