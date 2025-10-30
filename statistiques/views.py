# # from django.shortcuts import render
# # from django.db import models
# # from django.db.models import Sum, F, DecimalField
# # from django.utils import timezone
# # from datetime import timedelta, datetime
# # from collections import defaultdict
# # import calendar
# # import json 

# # # Import des fonctions d'agrégation spécifiques
# # from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate 

# # # ----------------------------------------------------
# # # Import de vos modèles
# # # ----------------------------------------------------
# # from commandes.models import Commande, CommandeItem, Boisson 
# # from avances.models import Avance 
# # from depenses.models import Depense 
# # from personnel.models import Personnel

# # def statistiques_dashboard(request):
# #     period = request.GET.get('period', 'mensuel')
# #     selected_year = request.GET.get('year')
# #     selected_month = request.GET.get('month')
# #     selected_date = request.GET.get('date')

# #     today = timezone.localdate()

# #     # 1. Préparation de l'année et des filtres de temps
    
# #     all_years_qs = Commande.objects.filter(date_validation__isnull=False).values_list('date_validation__year', flat=True).distinct()
# #     available_years = sorted(list(set(all_years_qs)), reverse=True)
    
# #     if not selected_year and available_years:
# #         current_year = available_years[0]
# #     else:
# #         current_year = int(selected_year) if selected_year and selected_year.isdigit() else today.year
    
# #     current_month = int(selected_month) if selected_month and selected_month.isdigit() else today.month
# #     current_date = selected_date if selected_date else today.strftime('%Y-%m-%d')
    
# #     group_by_func = TruncDate
# #     date_format = '%Y-%m-%d'
# #     base_filter = {}
    
# #     if period == 'annuel':
# #         group_by_func = TruncYear
# #         date_format = '%Y'
        
# #     elif period == 'trimestriel':
# #         group_by_func = TruncQuarter
# #         base_filter = {'__year': current_year}
        
# #     elif period == 'mensuel':
# #         group_by_func = TruncMonth
# #         base_filter = {'__year': current_year}

# #     elif period == 'hebdomadaire':
# #         group_by_func = TruncWeek
# #         base_filter = {'__year': current_year, '__month': current_month}
        
# #     elif period == 'journalier':
# #         group_by_func = TruncDate
# #         try:
# #             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
# #             base_filter = {'__date': date_obj}
# #         except ValueError:
# #             pass 

# #     context = {
# #         'period': period,
# #         'available_years': available_years,
# #         'selected_year': current_year,
# #         'selected_month': current_month,
# #         'selected_date': current_date,
# #         'months': [ (i, calendar.month_name[i]) for i in range(1, 13) ],
# #     }
    
    
# #     # ----------------------------------------------------
# #     # FONCTION D'AGRÉGATION (CA / DÉPENSES / AVANCES / IMPAYÉS)
# #     # ----------------------------------------------------
# #     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
# #         qs = model.objects.all()
        
# #         filter_dict = {}
# #         for k, v in base_filter.items():
# #             filter_dict[f'{date_field}{k}'] = v

# #         if extra_filter:
# #             qs = qs.filter(**extra_filter)

# #         qs = qs.filter(**filter_dict)

# #         data = defaultdict(lambda: 0)
        
# #         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
# #             total=Sum(amount_field)
# #         ).order_by('date_group')
        
# #         for item in qs:
# #             if item['date_group']:
# #                 # Formattage du label de l'axe X selon la période
# #                 if period == 'trimestriel':
# #                     q_num = (item['date_group'].month - 1) // 3 + 1
# #                     label = f"T{q_num}/{item['date_group'].year}"
# #                 elif period == 'hebdomadaire':
# #                     # Utilise ISO week number pour la compatibilité (Semaine %V)
# #                     label = item['date_group'].strftime('Semaine %V (%Y)') 
# #                 elif period == 'annuel':
# #                     label = item['date_group'].strftime('%Y')
# #                 elif period == 'mensuel':
# #                     label = item['date_group'].strftime('%Y-%m')
# #                 else: # Journalier
# #                     label = item['date_group'].strftime('%Y-%m-%d')

# #                 data[label] = float(item['total'] or 0)
# #         return data


# #     # ----------------------------------------------------
# #     # 1. ÉVOLUTION DES FLUX FINANCIERS
# #     # ----------------------------------------------------

# #     # Récupération des données CA (commandes payées)
# #     data_ca = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'payer'})
    
# #     # Récupération des données des impayés
# #     data_impayes = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'impaye'})
    
# #     # Récupération des dépenses
# #     data_depenses = get_aggregated_data(Depense, 'date', 'montant')
    
# #     # Récupération des avances
# #     data_avances = get_aggregated_data(Avance, 'date_avance', 'montant')
        
# #     # Déterminer toutes les labels uniques pour l'axe X
# #     all_labels = sorted(list(
# #         set(data_ca.keys()) | 
# #         set(data_impayes.keys()) | 
# #         set(data_depenses.keys()) | 
# #         set(data_avances.keys())
# #     ))

# #     # Sérialisation dans le contexte
# #     context['ca_labels'] = json.dumps(all_labels)
# #     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels])
# #     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
# #     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
# #     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])

    
# #     # ----------------------------------------------------
# #     # 2. 3. 4. 5. AUTRES GRAPHIQUES (Ventes, Clients, Personnel)
# #     # ----------------------------------------------------

# #     commande_filter = {'statut': 'payer'}
# #     for k, v in base_filter.items():
# #         commande_filter[f'date_validation{k}'] = v
        
# #     items_qs = CommandeItem.objects.filter(
# #         **{f'commande__{k}': v for k, v in commande_filter.items()} 
# #     ).select_related('boisson', 'commande__personnel__user')

# #     # 2. Quantité totale de boissons
# #     boissons_quantite = items_qs.values('boisson__nom').annotate(total_quantite=Sum('quantite')).order_by('-total_quantite')
# #     context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])
# #     context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])

# #     # 3. & 4. Ventes par personnel (par boisson et total)
# #     personnel_sales_data = defaultdict(lambda: defaultdict(lambda: 0))
# #     personnel_total_sales = defaultdict(lambda: 0)
    
# #     for item in items_qs:
# #         personnel_profile = item.commande.personnel
# #         personnel_name = personnel_profile.nom_complet if personnel_profile else f"Personnel Inconnu {item.commande.personnel_id}"
# #         boisson_name = item.boisson.nom
# #         personnel_sales_data[personnel_name][boisson_name] += item.quantite
# #         personnel_total_sales[personnel_name] += item.quantite

# #     all_boissons = sorted(list(set(item.boisson.nom for item in items_qs)))
# #     personnel_names = sorted(list(personnel_sales_data.keys()))
    
# #     context['personnel_boisson_labels'] = json.dumps(all_boissons)
# #     personnel_boisson_datasets = []
# #     for name in personnel_names:
# #         # Utilisation de .get(b_name, 0) pour garantir des zéros
# #         data_set = {'label': name, 'data': [personnel_sales_data[name].get(b_name, 0) for b_name in all_boissons]}
# #         personnel_boisson_datasets.append(data_set)
# #     context['personnel_boisson_datasets'] = json.dumps(personnel_boisson_datasets)

# #     personnel_total_sorted = sorted(personnel_total_sales.items(), key=lambda item: item[1], reverse=True)
# #     context['personnel_total_labels'] = json.dumps([item[0] for item in personnel_total_sorted])
# #     context['personnel_total_data'] = json.dumps([item[1] for item in personnel_total_sorted])

# #     # 5. Top Clients
# #     top_clients_qs = Commande.objects.filter(numero_telephone__isnull=False, **commande_filter)
# #     top_clients_qs = top_clients_qs.values('numero_telephone', 'client_nom', 'client_prenom').annotate(
# #         total_depense=Sum('montant_total', output_field=DecimalField())
# #     ).order_by('-total_depense')[:10]
    
# #     top_clients_labels = []
# #     top_clients_data = []
    
# #     for client in top_clients_qs:
# #         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
# #         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
# #         top_clients_labels.append(client_display)
# #         top_clients_data.append(float(client['total_depense'] or 0))
        
# #     context['top_clients_labels'] = json.dumps(top_clients_labels)
# #     context['top_clients_data'] = json.dumps(top_clients_data)

# #     # Debug - afficher les données dans la console Django
# #     print(f"Période: {period}")
# #     print(f"CA total: {sum(data_ca.values())}")
# #     print(f"Impayés total: {sum(data_impayes.values())}")
# #     print(f"Dépenses total: {sum(data_depenses.values())}")
# #     print(f"Avances total: {sum(data_avances.values())}")

# #     return render(request, 'statistiques/dashboard.html', context)


# # from django.shortcuts import render
# # from django.db import models
# # from django.db.models import Sum, F, DecimalField
# # from django.utils import timezone
# # from datetime import timedelta, datetime
# # from collections import defaultdict
# # import calendar
# # import json 

# # # Import des fonctions d'agrégation spécifiques
# # from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate 

# # # ----------------------------------------------------
# # # Import de vos modèles
# # # ----------------------------------------------------
# # from commandes.models import Commande, CommandeItem, Boisson 
# # from avances.models import Avance 
# # from depenses.models import Depense 
# # from personnel.models import Personnel

# # def statistiques_dashboard(request):
# #     period = request.GET.get('period', 'mensuel')
# #     selected_year = request.GET.get('year')
# #     selected_month = request.GET.get('month')
# #     selected_date = request.GET.get('date')
# #     current_graph = request.GET.get('graph', 'financial')  # Graphique courant

# #     today = timezone.localdate()

# #     # 1. Préparation de l'année et des filtres de temps
    
# #     all_years_qs = Commande.objects.filter(date_validation__isnull=False).values_list('date_validation__year', flat=True).distinct()
# #     available_years = sorted(list(set(all_years_qs)), reverse=True)
    
# #     if not selected_year and available_years:
# #         current_year = available_years[0]
# #     else:
# #         current_year = int(selected_year) if selected_year and selected_year.isdigit() else today.year
    
# #     current_month = int(selected_month) if selected_month and selected_month.isdigit() else today.month
# #     current_date = selected_date if selected_date else today.strftime('%Y-%m-%d')
    
# #     group_by_func = TruncDate
# #     date_format = '%Y-%m-%d'
# #     base_filter = {}
    
# #     if period == 'annuel':
# #         group_by_func = TruncYear
# #         date_format = '%Y'
        
# #     elif period == 'trimestriel':
# #         group_by_func = TruncQuarter
# #         base_filter = {'__year': current_year}
        
# #     elif period == 'mensuel':
# #         group_by_func = TruncMonth
# #         base_filter = {'__year': current_year}

# #     elif period == 'hebdomadaire':
# #         group_by_func = TruncWeek
# #         base_filter = {'__year': current_year, '__month': current_month}
        
# #     elif period == 'journalier':
# #         group_by_func = TruncDate
# #         try:
# #             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
# #             base_filter = {'__date': date_obj}
# #         except ValueError:
# #             pass 

# #     context = {
# #         'period': period,
# #         'available_years': available_years,
# #         'selected_year': current_year,
# #         'selected_month': current_month,
# #         'selected_date': current_date,
# #         'months': [ (i, calendar.month_name[i]) for i in range(1, 13) ],
# #         'current_graph': current_graph,  # Graphique courant
# #     }
    
    
# #     # ----------------------------------------------------
# #     # FONCTION D'AGRÉGATION (CA / DÉPENSES / AVANCES / IMPAYÉS)
# #     # ----------------------------------------------------
# #     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
# #         qs = model.objects.all()
        
# #         filter_dict = {}
# #         for k, v in base_filter.items():
# #             filter_dict[f'{date_field}{k}'] = v

# #         if extra_filter:
# #             qs = qs.filter(**extra_filter)

# #         qs = qs.filter(**filter_dict)

# #         data = defaultdict(lambda: 0)
        
# #         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
# #             total=Sum(amount_field)
# #         ).order_by('date_group')
        
# #         for item in qs:
# #             if item['date_group']:
# #                 # Formattage du label de l'axe X selon la période
# #                 if period == 'trimestriel':
# #                     q_num = (item['date_group'].month - 1) // 3 + 1
# #                     label = f"T{q_num}/{item['date_group'].year}"
# #                 elif period == 'hebdomadaire':
# #                     # Utilise ISO week number pour la compatibilité (Semaine %V)
# #                     label = item['date_group'].strftime('Semaine %V (%Y)') 
# #                 elif period == 'annuel':
# #                     label = item['date_group'].strftime('%Y')
# #                 elif period == 'mensuel':
# #                     label = item['date_group'].strftime('%Y-%m')
# #                 else: # Journalier
# #                     label = item['date_group'].strftime('%Y-%m-%d')

# #                 data[label] = float(item['total'] or 0)
# #         return data


# #     # ----------------------------------------------------
# #     # 1. ÉVOLUTION DES FLUX FINANCIERS
# #     # ----------------------------------------------------

# #     # Récupération des données CA (commandes payées)
# #     data_ca = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'payer'})
    
# #     # Récupération des données des impayés
# #     data_impayes = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'impaye'})
    
# #     # Récupération des dépenses
# #     data_depenses = get_aggregated_data(Depense, 'date', 'montant')
    
# #     # Récupération des avances
# #     data_avances = get_aggregated_data(Avance, 'date_avance', 'montant')
        
# #     # Déterminer toutes les labels uniques pour l'axe X
# #     all_labels = sorted(list(
# #         set(data_ca.keys()) | 
# #         set(data_impayes.keys()) | 
# #         set(data_depenses.keys()) | 
# #         set(data_avances.keys())
# #     ))

# #     # Sérialisation dans le contexte
# #     context['ca_labels'] = json.dumps(all_labels)
# #     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels])
# #     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
# #     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
# #     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])

    
# #     # ----------------------------------------------------
# #     # 2. 3. 4. 5. AUTRES GRAPHIQUES (Ventes, Clients, Personnel)
# #     # ----------------------------------------------------

# #     commande_filter = {'statut': 'payer'}
# #     for k, v in base_filter.items():
# #         commande_filter[f'date_validation{k}'] = v
        
# #     items_qs = CommandeItem.objects.filter(
# #         **{f'commande__{k}': v for k, v in commande_filter.items()} 
# #     ).select_related('boisson', 'commande__personnel__user')

# #     # 2. Quantité totale de boissons
# #     boissons_quantite = items_qs.values('boisson__nom').annotate(total_quantite=Sum('quantite')).order_by('-total_quantite')
# #     context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])
# #     context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])

# #     # 3. & 4. Ventes par personnel (par boisson et total)
# #     personnel_sales_data = defaultdict(lambda: defaultdict(lambda: 0))
# #     personnel_total_sales = defaultdict(lambda: 0)
    
# #     for item in items_qs:
# #         personnel_profile = item.commande.personnel
# #         personnel_name = personnel_profile.nom_complet if personnel_profile else f"Personnel Inconnu {item.commande.personnel_id}"
# #         boisson_name = item.boisson.nom
# #         personnel_sales_data[personnel_name][boisson_name] += item.quantite
# #         personnel_total_sales[personnel_name] += item.quantite

# #     all_boissons = sorted(list(set(item.boisson.nom for item in items_qs)))
# #     personnel_names = sorted(list(personnel_sales_data.keys()))
    
# #     context['personnel_boisson_labels'] = json.dumps(all_boissons)
# #     personnel_boisson_datasets = []
# #     for name in personnel_names:
# #         # Utilisation de .get(b_name, 0) pour garantir des zéros
# #         data_set = {'label': name, 'data': [personnel_sales_data[name].get(b_name, 0) for b_name in all_boissons]}
# #         personnel_boisson_datasets.append(data_set)
# #     context['personnel_boisson_datasets'] = json.dumps(personnel_boisson_datasets)

# #     personnel_total_sorted = sorted(personnel_total_sales.items(), key=lambda item: item[1], reverse=True)
# #     context['personnel_total_labels'] = json.dumps([item[0] for item in personnel_total_sorted])
# #     context['personnel_total_data'] = json.dumps([item[1] for item in personnel_total_sorted])

# #     # 5. Top Clients
# #     top_clients_qs = Commande.objects.filter(numero_telephone__isnull=False, **commande_filter)
# #     top_clients_qs = top_clients_qs.values('numero_telephone', 'client_nom', 'client_prenom').annotate(
# #         total_depense=Sum('montant_total', output_field=DecimalField())
# #     ).order_by('-total_depense')[:10]
    
# #     top_clients_labels = []
# #     top_clients_data = []
    
# #     for client in top_clients_qs:
# #         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
# #         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
# #         top_clients_labels.append(client_display)
# #         top_clients_data.append(float(client['total_depense'] or 0))
        
# #     context['top_clients_labels'] = json.dumps(top_clients_labels)
# #     context['top_clients_data'] = json.dumps(top_clients_data)

# #     return render(request, 'statistiques/dashboard.html', context)


# ############## 08 -08- 2025 ##################
# from django.shortcuts import render
# from django.db import models
# from django.db.models import Sum, F, DecimalField, Q
# from django.utils import timezone
# from datetime import timedelta, datetime, date
# from collections import defaultdict
# import calendar
# import json 

# # Import des fonctions d'agrégation spécifiques
# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate 

# # ----------------------------------------------------
# # Import de vos modèles
# # ----------------------------------------------------
# from commandes.models import Commande, CommandeItem, Boisson 
# from avances.models import Avance 
# from depenses.models import Depense 
# from personnel.models import Personnel


# def statistiques_dashboard(request):
#     period = request.GET.get('period', 'mensuel')
#     selected_year = request.GET.get('year')
#     selected_month = request.GET.get('month')
#     selected_date = request.GET.get('date')
#     current_graph = request.GET.get('graph', 'financial')

#     today = timezone.localdate()

#     # 1. Préparation de l'année et des filtres de temps
    
#     # Utiliser date_commande au lieu de start_time
#     all_years_qs = Commande.objects.filter(date_commande__isnull=False).values_list('date_commande__year', flat=True).distinct()
#     available_years = sorted(list(set(all_years_qs)), reverse=True)
    
#     if not selected_year and available_years:
#         current_year = available_years[0]
#     else:
#         current_year = int(selected_year) if selected_year and selected_year.isdigit() else today.year
    
#     current_month = int(selected_month) if selected_month and selected_month.isdigit() else today.month
#     current_date = selected_date if selected_date else today.strftime('%Y-%m-%d')
    
#     # Déterminer les plages de dates basées sur date_commande
#     start_date = None
#     end_date = None
    
#     if period == 'journalier':
#         try:
#             start_date = datetime.strptime(current_date, '%Y-%m-%d').date()
#             end_date = start_date
#         except ValueError:
#             start_date = today
#             end_date = today
            
#     elif period == 'hebdomadaire':
#         # Premier jour (lundi) et dernier jour (dimanche) de la semaine
#         start_date = date(current_year, current_month, 1)
#         # Trouver le premier lundi du mois
#         while start_date.weekday() != 0:  # 0 = lundi
#             start_date += timedelta(days=1)
#         end_date = start_date + timedelta(days=6)
        
#     elif period == 'mensuel':
#         start_date = date(current_year, current_month, 1)
#         # Dernier jour du mois
#         if current_month == 12:
#             end_date = date(current_year, 12, 31)
#         else:
#             end_date = date(current_year, current_month + 1, 1) - timedelta(days=1)
            
#     elif period == 'trimestriel':
#         # Déterminer le trimestre
#         quarter = (current_month - 1) // 3 + 1
#         start_month = (quarter - 1) * 3 + 1
#         end_month = start_month + 2
#         start_date = date(current_year, start_month, 1)
#         if end_month == 12:
#             end_date = date(current_year, 12, 31)
#         else:
#             end_date = date(current_year, end_month + 1, 1) - timedelta(days=1)
            
#     elif period == 'annuel':
#         start_date = date(current_year, 1, 1)
#         end_date = date(current_year, 12, 31)

#     context = {
#         'period': period,
#         'available_years': available_years,
#         'selected_year': current_year,
#         'selected_month': current_month,
#         'selected_date': current_date,
#         'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
#         'current_graph': current_graph,
#     }
    
    
#     # ----------------------------------------------------
#     # FONCTION D'AGRÉGATION BASÉE SUR date_commande
#     # ----------------------------------------------------
#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
#         qs = model.objects.all()
        
#         # Filtre basé sur date_commande pour les Commandes, date normale pour les autres
#         if start_date and end_date:
#             if model == Commande:  # Pour les Commandes
#                 qs = qs.filter(date_commande__date__gte=start_date, date_commande__date__lte=end_date)
#             else:  # Pour les autres modèles (Depense, Avance)
#                 qs = qs.filter(**{f'{date_field}__date__gte': start_date, f'{date_field}__date__lte': end_date})

#         if extra_filter:
#             qs = qs.filter(**extra_filter)

#         data = defaultdict(lambda: 0)
        
#         # Déterminer la fonction d'agrégation selon la période
#         if period == 'annuel':
#             group_by_func = TruncYear
#             date_format = '%Y'
#         elif period == 'trimestriel':
#             group_by_func = TruncQuarter
#             date_format = 'T%q/%Y'
#         elif period == 'mensuel':
#             group_by_func = TruncMonth
#             date_format = '%Y-%m'
#         elif period == 'hebdomadaire':
#             group_by_func = TruncWeek
#             date_format = 'Semaine %V (%Y)'
#         else:  # journalier
#             group_by_func = TruncDate
#             date_format = '%Y-%m-%d'

#         # Agrégation selon le modèle
#         if model == Commande:  # Commandes - utiliser date_commande
#             qs = qs.annotate(date_group=group_by_func('date_commande')).values('date_group').annotate(
#                 total=Sum(amount_field)
#             ).order_by('date_group')
#         else:  # Dépenses et Avances
#             qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
#                 total=Sum(amount_field)
#             ).order_by('date_group')
        
#         for item in qs:
#             if item['date_group']:
#                 # Formattage du label de l'axe X selon la période
#                 if period == 'trimestriel':
#                     q_num = (item['date_group'].month - 1) // 3 + 1
#                     label = f"T{q_num}/{item['date_group'].year}"
#                 elif period == 'hebdomadaire':
#                     label = item['date_group'].strftime('Semaine %V (%Y)') 
#                 elif period == 'annuel':
#                     label = item['date_group'].strftime('%Y')
#                 elif period == 'mensuel':
#                     label = item['date_group'].strftime('%Y-%m')
#                 else:  # Journalier
#                     label = item['date_group'].strftime('%Y-%m-%d')

#                 data[label] = float(item['total'] or 0)
#         return data


#     # ----------------------------------------------------
#     # 1. ÉVOLUTION DES FLUX FINANCIERS
#     # ----------------------------------------------------

#     # Récupération des données CA (commandes payées) - basé sur date_commande
#     data_ca = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'payer'})
    
#     # Récupération des données des impayés - basé sur date_commande
#     data_impayes = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'impaye'})
    
#     # Récupération des dépenses - basé sur la date normale
#     data_depenses = get_aggregated_data(Depense, 'date', 'montant')
    
#     # Récupération des avances - basé sur la date normale
#     data_avances = get_aggregated_data(Avance, 'date_avance', 'montant')
        
#     # Déterminer toutes les labels uniques pour l'axe X
#     all_labels = sorted(list(
#         set(data_ca.keys()) | 
#         set(data_impayes.keys()) | 
#         set(data_depenses.keys()) | 
#         set(data_avances.keys())
#     ))

#     # Sérialisation dans le contexte
#     context['ca_labels'] = json.dumps(all_labels)
#     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels])
#     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
#     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
#     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])

    
#     # ----------------------------------------------------
#     # 2. 3. 4. 5. AUTRES GRAPHIQUES (Ventes, Clients, Personnel)
#     # ----------------------------------------------------

#     # Filtre basé sur date_commande pour les commandes
#     commande_filter = {'statut': 'payer'}
#     if start_date and end_date:
#         commande_filter['commande__date_commande__date__gte'] = start_date
#         commande_filter['commande__date_commande__date__lte'] = end_date
        
#     items_qs = CommandeItem.objects.filter(
#         commande__date_commande__date__gte=start_date,
#         commande__date_commande__date__lte=end_date,
#         commande__statut='payer'
#     ).select_related('boisson', 'commande__personnel__user')

#     # 2. Quantité totale de boissons
#     boissons_quantite = items_qs.values('boisson__nom').annotate(total_quantite=Sum('quantite')).order_by('-total_quantite')
#     context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])
#     context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])

#     # 3. & 4. Ventes par personnel (par boisson et total)
#     personnel_sales_data = defaultdict(lambda: defaultdict(lambda: 0))
#     personnel_total_sales = defaultdict(lambda: 0)
    
#     for item in items_qs:
#         personnel_profile = item.commande.personnel
#         personnel_name = personnel_profile.nom_complet if personnel_profile else f"Personnel Inconnu {item.commande.personnel_id}"
#         boisson_name = item.boisson.nom
#         personnel_sales_data[personnel_name][boisson_name] += item.quantite
#         personnel_total_sales[personnel_name] += item.quantite

#     all_boissons = sorted(list(set(item.boisson.nom for item in items_qs)))
#     personnel_names = sorted(list(personnel_sales_data.keys()))
    
#     context['personnel_boisson_labels'] = json.dumps(all_boissons)
#     personnel_boisson_datasets = []
#     for name in personnel_names:
#         data_set = {'label': name, 'data': [personnel_sales_data[name].get(b_name, 0) for b_name in all_boissons]}
#         personnel_boisson_datasets.append(data_set)
#     context['personnel_boisson_datasets'] = json.dumps(personnel_boisson_datasets)

#     personnel_total_sorted = sorted(personnel_total_sales.items(), key=lambda item: item[1], reverse=True)
#     context['personnel_total_labels'] = json.dumps([item[0] for item in personnel_total_sorted])
#     context['personnel_total_data'] = json.dumps([item[1] for item in personnel_total_sorted])

#     # 5. Top Clients
#     top_clients_qs = Commande.objects.filter(
#         numero_telephone__isnull=False,
#         date_commande__date__gte=start_date,
#         date_commande__date__lte=end_date,
#         statut='payer'
#     )
#     top_clients_qs = top_clients_qs.values('numero_telephone', 'client_nom', 'client_prenom').annotate(
#         total_depense=Sum('montant_total', output_field=DecimalField())
#     ).order_by('-total_depense')[:10]
    
#     top_clients_labels = []
#     top_clients_data = []
    
#     for client in top_clients_qs:
#         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
#         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
#         top_clients_labels.append(client_display)
#         top_clients_data.append(float(client['total_depense'] or 0))
        
#     context['top_clients_labels'] = json.dumps(top_clients_labels)
#     context['top_clients_data'] = json.dumps(top_clients_data)

#     # Debug info
#     print(f"Période: {period}")
#     print(f"Start Date: {start_date}")
#     print(f"End Date: {end_date}")
#     print(f"CA total: {sum(data_ca.values())}")
#     print(f"Impayés total: {sum(data_impayes.values())}")

#     return render(request, 'statistiques/dashboard.html', context)


##########################

# from django.shortcuts import render
# from django.db import models
# from django.db.models import Sum, F, DecimalField
# from django.utils import timezone
# from datetime import timedelta, datetime
# from collections import defaultdict
# import calendar
# import json
# from django.db.models import Q 
# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate

# # Import de vos modèles
# from commandes.models import Commande, CommandeItem, Boisson
# from avances.models import Avance
# from depenses.models import Depense
# from personnel.models import Personnel

# # ----------------------------------------------------
# # FONCTION : DÉTERMINER LES BORNES TEMPORELLES
# # ----------------------------------------------------
# def get_time_range_filter(period, current_year, current_month, current_date, start_date_param=None, end_date_param=None):
#     """Calcule les bornes (datetime) pour la période donnée, basé sur le début de la transaction."""

#     now = timezone.now()
#     today = timezone.localdate()
    
#     start_date = None
#     end_date = None
#     group_by_func = TruncDate
    
#     if period == 'aujourdhui':
#         # Aujourd'hui : de 00:00:00 du jour J à la dernière seconde du jour J.
#         start_date = datetime.combine(today, datetime.min.time())
#         end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate
        
#     elif period == 'journalier':
#         # Journalier (date choisie) : de 00:00:00 du jour choisi à la dernière seconde du jour choisi.
#         try:
#             # FIX DE L'ERREUR : current_date est garanti d'être une chaîne (ou la date du jour par défaut)
#             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
#             start_date = datetime.combine(date_obj, datetime.min.time())
#             end_date = datetime.combine(date_obj, datetime.max.time())
#         except ValueError:
#             # Fallback à aujourd'hui si la date n'est pas valide
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate

#     elif period == 'hebdomadaire':
#         # Semaine en cours : du lundi 00:00:00 au dimanche 23:59:59 de la semaine courante.
#         start_of_week = today - timedelta(days=today.weekday()) # Lundi
#         start_date = datetime.combine(start_of_week, datetime.min.time())
#         end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())
#         group_by_func = TruncWeek
        
#     elif period == 'mensuel':
#         # Mois en cours : du 1er jour 00:00:00 au dernier jour 23:59:59 du mois courant.
#         start_date = datetime(today.year, today.month, 1)
        
#         # Trouver le 1er jour du mois suivant
#         if today.month == 12:
#             end_date = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)
#         group_by_func = TruncMonth
    
#     elif period == 'trimestriel':
#         # Trimestre en cours
#         q = (today.month - 1) // 3 + 1
#         start_month = 3 * q - 2
        
#         start_date = datetime(today.year, start_month, 1)
        
#         # Calculer le début du trimestre suivant
#         next_month_start = start_month + 3
#         if next_month_start > 12:
#             end_date = datetime(today.year + 1, next_month_start % 12, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, next_month_start, 1) - timedelta(seconds=1)
#         group_by_func = TruncQuarter


#     elif period == 'annuel':
#         # Année en cours : du 1er janv 00:00:00 au 31 déc 23:59:59 de l'année courante.
#         start_date = datetime(current_year, 1, 1)
#         end_date = datetime(current_year, 12, 31, 23, 59, 59)
#         group_by_func = TruncYear

#     elif period == 'autre':
#         # Plage personnalisée : du premier start_time de la date_debut au dernier start_time de la date_fin.
#         try:
#             start_date_obj = datetime.strptime(start_date_param, '%Y-%m-%d')
#             end_date_obj = datetime.strptime(end_date_param, '%Y-%m-%d')
            
#             start_date = datetime.combine(start_date_obj.date(), datetime.min.time())
#             end_date = datetime.combine(end_date_obj.date(), datetime.max.time())
            
#         except:
#             # Fallback si les dates ne sont pas valides
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate 

#     # Assurez-vous que les dates sont conscientes du fuseau horaire (aware)
#     if start_date and not timezone.is_aware(start_date):
#         start_date = timezone.make_aware(start_date)
#     if end_date and not timezone.is_aware(end_date):
#         end_date = timezone.make_aware(end_date)
    
#     return {
#         'start_dt': start_date, 
#         'end_dt': end_date, 
#         'group_by_func': group_by_func
#     }


# def statistiques_dashboard(request):
    
#     today = timezone.localdate()
    
#     # Récupération des paramètres avec VALEURS PAR DÉFAUT pour éviter l'erreur strptime(None, ...)
#     period = request.GET.get('period', 'aujourdhui')
#     selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
#     start_date_param = request.GET.get('start_date', today.strftime('%Y-%m-%d'))
#     end_date_param = request.GET.get('end_date', today.strftime('%Y-%m-%d'))

    
#     # 1. Détermination de la période
#     time_info = get_time_range_filter(
#         period, 
#         today.year, 
#         today.month, 
#         selected_date, 
#         start_date_param, 
#         end_date_param
#     )
#     start_dt = time_info['start_dt']
#     end_dt = time_info['end_dt']
#     group_by_func = time_info['group_by_func']
    
#     # 2. Contexte pour les filtres (UI)
#     all_years_qs = Commande.objects.filter(date_validation__isnull=False).values_list('date_validation__year', flat=True).distinct()
#     available_years = sorted(list(set(all_years_qs)), reverse=True)
    
#     context = {
#         'period': period,
#         'selected_date': selected_date,
#         'start_date_param': start_date_param,
#         'end_date_param': end_date_param,
#         'available_years': available_years,
#         'current_graph': request.GET.get('graph', 'financial'),
#     }
    
    
#     # ----------------------------------------------------
#     # FONCTION D'AGRÉGATION 
#     # ----------------------------------------------------
#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
#         qs = model.objects.all()
        
#         # Filtre sur la plage de temps [start_dt, end_dt] (inclusif aux deux bouts)
#         range_filter_key = f'{date_field}__range'
        
#         # On filtre toutes les transactions dont le champ de date (start_time) est dans la plage choisie.
#         qs = qs.filter(**{range_filter_key: (start_dt, end_dt)}) 

#         if extra_filter:
#             qs = qs.filter(**extra_filter)

#         data = defaultdict(lambda: 0)
        
#         # Truncation pour le regroupement
#         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
#             total=Sum(amount_field)
#         ).order_by('date_group')
        
#         # Logique de Formattage des Labels
#         for item in qs:
#             if item['date_group']:
#                 date_group = item['date_group']
#                 label = ""
#                 if period == 'trimestriel':
#                     q_num = (date_group.month - 1) // 3 + 1
#                     label = f"T{q_num}/{date_group.year}"
#                 elif period == 'hebdomadaire':
#                     # Utiliser strftime('%W') pour le numéro de semaine ISO 8601
#                     label = date_group.strftime('Semaine %V (%Y)') 
#                 elif period == 'annuel':
#                     label = date_group.strftime('%Y')
#                 elif period == 'mensuel':
#                     label = date_group.strftime('%Y-%m')
#                 elif period in ['aujourdhui', 'journalier', 'autre']:
#                     label = date_group.strftime('%Y-%m-%d')
                
#                 data[label] = float(item['total'] or 0)
#         return data


#     # ----------------------------------------------------
#     # 3. Récupération des données pour les graphiques
#     # ----------------------------------------------------
    
#     data_ca = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'payer'})
#     data_impayes = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'impaye'})
#     data_depenses = get_aggregated_data(Depense, 'date', 'montant')
#     data_avances = get_aggregated_data(Avance, 'date_avance', 'montant')
        
#     all_labels = sorted(list(
#         set(data_ca.keys()) | set(data_impayes.keys()) | set(data_depenses.keys()) | set(data_avances.keys())
#     ))

#     context['ca_labels'] = json.dumps(all_labels)
#     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels])
#     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
#     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
#     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])
    
#     # ----------------------------------------------------
#     # 2. VENTES PAR BOISSON
#     # ----------------------------------------------------

#     commande_filter = {
#         'statut': 'payer', 
#         'date_validation__range': (start_dt, end_dt)
#     }
    
#     items_qs = CommandeItem.objects.filter(
#         **{f'commande__{k}': v for k, v in commande_filter.items()} 
#     ).select_related('boisson', 'commande__personnel__user')

#     boissons_quantite = items_qs.values('boisson__nom').annotate(total_quantite=Sum('quantite')).order_by('-total_quantite')
#     context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])
#     context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])

#     # ----------------------------------------------------
#     # 3. & 4. VENTES PAR PERSONNEL
#     # ----------------------------------------------------

#     personnel_sales_data = defaultdict(lambda: defaultdict(lambda: 0))
#     personnel_total_sales = defaultdict(lambda: 0)
    
#     for item in items_qs:
#         personnel_profile = item.commande.personnel
#         personnel_name = personnel_profile.nom_complet if personnel_profile else f"Personnel ID {item.commande.personnel_id}"
#         boisson_name = item.boisson.nom
#         personnel_sales_data[personnel_name][boisson_name] += item.quantite
#         personnel_total_sales[personnel_name] += item.quantite

#     all_boissons = sorted(list(set(item.boisson.nom for item in items_qs)))
#     personnel_names = sorted(list(personnel_sales_data.keys()))
    
#     context['personnel_boisson_labels'] = json.dumps(all_boissons)
#     personnel_boisson_datasets = []
#     for name in personnel_names:
#         data_set = {'label': name, 'data': [personnel_sales_data[name].get(b_name, 0) for b_name in all_boissons]}
#         personnel_boisson_datasets.append(data_set)
#     context['personnel_boisson_datasets'] = json.dumps(personnel_boisson_datasets)

#     personnel_total_sorted = sorted(personnel_total_sales.items(), key=lambda item: item[1], reverse=True)
#     context['personnel_total_labels'] = json.dumps([item[0] for item in personnel_total_sorted])
#     context['personnel_total_data'] = json.dumps([item[1] for item in personnel_total_sorted])

#     # ----------------------------------------------------
#     # 5. TOP CLIENTS
#     # ----------------------------------------------------
#     top_clients_qs = Commande.objects.filter(numero_telephone__isnull=False, **commande_filter)
#     top_clients_qs = top_clients_qs.values('numero_telephone', 'client_nom', 'client_prenom').annotate(
#         total_depense=Sum('montant_total', output_field=DecimalField())
#     ).order_by('-total_depense')[:10]
    
#     top_clients_labels = []
#     top_clients_data = []
    
#     for client in top_clients_qs:
#         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
#         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
#         top_clients_labels.append(client_display)
#         top_clients_data.append(float(client['total_depense'] or 0))
        
#     context['top_clients_labels'] = json.dumps(top_clients_labels)
#     context['top_clients_data'] = json.dumps(top_clients_data)

#     return render(request, 'statistiques/dashboard.html', context)

#####################

# from django.shortcuts import render
# from django.db import models
# # Imports mis à jour : ajout de Concat, Value
# from django.db.models import Sum, F, DecimalField, Value
# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate, Concat
# from django.utils import timezone
# from datetime import timedelta, datetime
# from collections import defaultdict
# import json
# from django.db.models import Q 


# # Import de vos modèles (vérifiez les chemins)
# from commandes.models import Commande, CommandeItem, Boisson
# from avances.models import Avance
# from depenses.models import Depense
# from personnel.models import Personnel
# from ventes.models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne # Assurez-vous que vos modèles sont bien dans 'ventes'


# # ----------------------------------------------------
# # FONCTION : DÉTERMINER LES BORNES TEMPORELLES
# # ----------------------------------------------------
# def get_time_range_filter(period, current_year, current_month, current_date, start_date_param=None, end_date_param=None):
#     """Calcule les bornes (datetime) pour la période donnée, basé sur le début de la transaction."""

#     now = timezone.now()
#     today = timezone.localdate()
    
#     start_date = None
#     end_date = None
#     group_by_func = TruncDate
    
#     if period == 'aujourdhui':
#         start_date = datetime.combine(today, datetime.min.time())
#         end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate
        
#     elif period == 'journalier':
#         try:
#             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
#             start_date = datetime.combine(date_obj, datetime.min.time())
#             end_date = datetime.combine(date_obj, datetime.max.time())
#         except ValueError:
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate

#     elif period == 'hebdomadaire':
#         start_of_week = today - timedelta(days=today.weekday())
#         start_date = datetime.combine(start_of_week, datetime.min.time())
#         end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())
#         group_by_func = TruncWeek
        
#     elif period == 'mensuel':
#         start_date = datetime(today.year, today.month, 1)
#         # Calcul du dernier jour du mois
#         if today.month == 12:
#             end_date = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)
#         group_by_func = TruncMonth
    
#     elif period == 'trimestriel':
#         q = (today.month - 1) // 3 + 1
#         start_month = 3 * q - 2
        
#         start_date = datetime(today.year, start_month, 1)
        
#         next_month_start = start_month + 3
#         if next_month_start > 12:
#             end_date = datetime(today.year + 1, next_month_start % 12, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, next_month_start, 1) - timedelta(seconds=1)
#         group_by_func = TruncQuarter


#     elif period == 'annuel':
#         start_date = datetime(current_year, 1, 1)
#         end_date = datetime(current_year, 12, 31, 23, 59, 59)
#         group_by_func = TruncYear

#     elif period == 'autre':
#         try:
#             start_date_obj = datetime.strptime(start_date_param, '%Y-%m-%d')
#             end_date_obj = datetime.strptime(end_date_param, '%Y-%m-%d')
            
#             start_date = datetime.combine(start_date_obj.date(), datetime.min.time())
#             end_date = datetime.combine(end_date_obj.date(), datetime.max.time())
            
#         except:
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate 

#     # Assurez-vous que les dates sont conscientes du fuseau horaire (aware)
#     if start_date and not timezone.is_aware(start_date):
#         start_date = timezone.make_aware(start_date)
#     if end_date and not timezone.is_aware(end_date):
#         end_date = timezone.make_aware(end_date)
    
#     return {
#         'start_dt': start_date, 
#         'end_dt': end_date, 
#         'group_by_func': group_by_func
#     }

# # ----------------------------------------------------
# # FONCTION : STATISTIQUES DASHBOARD 
# # ----------------------------------------------------
# def statistiques_dashboard(request):
    
#     today = timezone.localdate()
    
#     # Récupération des paramètres avec VALEURS PAR DÉFAUT
#     period = request.GET.get('period', 'aujourdhui')
#     selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
#     start_date_param = request.GET.get('start_date', today.strftime('%Y-%m-%d'))
#     end_date_param = request.GET.get('end_date', today.strftime('%Y-%m-%d'))

    
#     # 1. Détermination de la période
#     time_info = get_time_range_filter(
#         period, 
#         today.year, 
#         today.month, 
#         selected_date, 
#         start_date_param, 
#         end_date_param
#     )
#     start_dt = time_info['start_dt']
#     end_dt = time_info['end_dt']
#     group_by_func = time_info['group_by_func']
    
#     # 2. Contexte pour les filtres (UI)
#     all_years_qs = RapportVenteNocturne.objects.values_list('start_time__year', flat=True).distinct()
#     available_years = sorted(list(set(all_years_qs)), reverse=True)
    
#     context = {
#         'period': period,
#         'selected_date': selected_date,
#         'start_date_param': start_date_param,
#         'end_date_param': end_date_param,
#         'available_years': available_years,
#         'current_graph': request.GET.get('graph', 'financial'),
#     }
    
    
#     # ----------------------------------------------------
#     # FONCTION D'AGRÉGATION
#     # ----------------------------------------------------
#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
#         qs = model.objects.all()
        
#         # Filtre sur la plage de temps [start_dt, end_dt]
#         range_filter_key = f'{date_field}__range'
        
#         if start_dt and end_dt:
#              qs = qs.filter(**{range_filter_key: (start_dt, end_dt)}) 

#         if extra_filter:
#             qs = qs.filter(**extra_filter)

#         data = defaultdict(lambda: 0)
        
#         # Truncation pour le regroupement
#         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
#             total=Sum(amount_field)
#         ).order_by('date_group')
        
#         # Logique de Formattage des Labels
#         for item in qs:
#             if item['date_group']:
#                 date_group = item['date_group']
#                 label = ""
                
#                 if isinstance(date_group, datetime):
#                     date_group = date_group.date()
                
#                 if period == 'trimestriel':
#                     q_num = (date_group.month - 1) // 3 + 1
#                     label = f"T{q_num}/{date_group.year}"
#                 elif period == 'hebdomadaire':
#                     # Utiliser %V pour le numéro de semaine ISO
#                     label = date_group.strftime('Semaine %V (%Y)') 
#                 elif period == 'annuel':
#                     label = date_group.strftime('%Y')
#                 elif period == 'mensuel':
#                     label = date_group.strftime('%Y-%m')
#                 elif period in ['aujourdhui', 'journalier', 'autre']:
#                     label = date_group.strftime('%Y-%m-%d')
                
#                 data[label] = float(item['total'] or 0)
#         return data


#     # ----------------------------------------------------
#     # 3. Récupération des données pour les graphiques FINANCIERS (RapportVenteNocturne)
#     # ----------------------------------------------------
    
#     base_model = RapportVenteNocturne
#     date_field = 'start_time'
#     # Filtrer les rapports terminés
#     extra_filter_completed = {'end_time__isnull': False}

#     data_ca = get_aggregated_data(base_model, date_field, 'montant_total_vente', extra_filter=extra_filter_completed)
#     data_impayes = get_aggregated_data(base_model, date_field, 'montant_total_impayees', extra_filter=extra_filter_completed)
#     data_depenses = get_aggregated_data(base_model, date_field, 'montant_total_depenses', extra_filter=extra_filter_completed)
#     data_avances = get_aggregated_data(base_model, date_field, 'montant_total_avances', extra_filter=extra_filter_completed)
        
#     all_labels = sorted(list(
#         set(data_ca.keys()) | set(data_impayes.keys()) | set(data_depenses.keys()) | set(data_avances.keys())
#     ))

#     context['ca_labels'] = json.dumps(all_labels)
#     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels]) 
#     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
#     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
#     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])
    
#     # ----------------------------------------------------
#     # 2. VENTES PAR BOISSON (DetailVenteBoisson)
#     # ----------------------------------------------------
    
#     # IDs des rapports terminés dans la période pour filtrer les autres modèles
#     rapport_ids = RapportVenteNocturne.objects.filter(
#         start_time__range=(start_dt, end_dt),
#         end_time__isnull=False
#     ).values_list('id', flat=True)

#     boissons_quantite = DetailVenteBoisson.objects.filter(
#         rapport_id__in=rapport_ids
#     ).values('boisson__nom').annotate(
#         total_quantite=Sum('quantite_totale')
#     ).order_by('-total_quantite')

#     context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])
#     context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])

#     # ----------------------------------------------------
#     # 3. & 4. VENTES PAR PERSONNEL (PerformancePersonnelNocturne)
#     # ----------------------------------------------------

#     personnel_total_qs = PerformancePersonnelNocturne.objects.filter(
#         rapport_id__in=rapport_ids
#     ).annotate(
#         # CORRECTION de l'erreur 'nom_complet' : Utilisation de Concat
#         personnel_nom=Concat(
#             'personnel__prenom', 
#             Value(' '),
#             'personnel__nom',
#             output_field=models.CharField()
#         )
#     ).values('personnel_nom').annotate(
#         total_quantite=Sum('quantite_totale_boissons_vendues')
#     ).order_by('-total_quantite')

#     context['personnel_total_labels'] = json.dumps([p['personnel_nom'] for p in personnel_total_qs])
#     context['personnel_total_data'] = json.dumps([p['total_quantite'] or 0 for p in personnel_total_qs])

#     # ----------------------------------------------------
#     # 5. TOP CLIENTS (Commande)
#     # ----------------------------------------------------
    
#     top_clients_qs = Commande.objects.filter(
#         numero_telephone__isnull=False, 
#         # CORRECTION de l'erreur 'rapport' : On filtre sur l'objet de la relation 
#         # en utilisant la liste d'IDs valides.
#         rapport__in=rapport_ids, 
#         statut='payer' 
#     ).values('numero_telephone', 'client_nom', 'client_prenom').annotate(
#         total_depense=Sum('montant_total', output_field=DecimalField())
#     ).order_by('-total_depense')[:10]
    
#     top_clients_labels = []
#     top_clients_data = []
    
#     for client in top_clients_qs:
#         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
#         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
#         top_clients_labels.append(client_display)
#         top_clients_data.append(float(client['total_depense'] or 0))
        
#     context['top_clients_labels'] = json.dumps(top_clients_labels)
#     context['top_clients_data'] = json.dumps(top_clients_data)

#     return render(request, 'statistiques/dashboard.html', context)







# ##############################
# from django.shortcuts import render
# from django.db import models
# from django.db.models import Sum, F, DecimalField, Value
# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate, Concat
# from django.utils import timezone
# from datetime import timedelta, datetime
# from collections import defaultdict
# import json
# from django.db.models import Q


# # Import de vos modèles
# from commandes.models import Commande
# from avances.models import Avance
# from depenses.models import Depense
# from personnel.models import Personnel
# from ventes.models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne 


# # ----------------------------------------------------
# # FONCTION : DÉTERMINER LES BORNES TEMPORELLES
# # ----------------------------------------------------
# def get_time_range_filter(period, current_year, current_month, current_date, start_date_param=None, end_date_param=None):
#     """Calcule les bornes (datetime) pour la période donnée, basé sur le début de la transaction."""

#     now = timezone.now()
#     today = timezone.localdate()
    
#     start_date = None
#     end_date = None
#     group_by_func = TruncDate
    
#     if period == 'aujourdhui':
#         start_date = datetime.combine(today, datetime.min.time())
#         end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate
        
#     elif period == 'journalier':
#         try:
#             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
#             start_date = datetime.combine(date_obj, datetime.min.time())
#             end_date = datetime.combine(date_obj, datetime.max.time())
#         except ValueError:
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate

#     elif period == 'hebdomadaire':
#         start_of_week = today - timedelta(days=today.weekday())
#         start_date = datetime.combine(start_of_week, datetime.min.time())
#         end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())
#         group_by_func = TruncWeek
        
#     elif period == 'mensuel':
#         start_date = datetime(today.year, today.month, 1)
#         # Calcul du dernier jour du mois
#         if today.month == 12:
#             end_date = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)
#         group_by_func = TruncMonth
    
#     elif period == 'trimestriel':
#         q = (today.month - 1) // 3 + 1
#         start_month = 3 * q - 2
        
#         start_date = datetime(today.year, start_month, 1)
        
#         next_month_start = start_month + 3
#         if next_month_start > 12:
#             end_date = datetime(today.year + 1, next_month_start % 12, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, next_month_start, 1) - timedelta(seconds=1)
#         group_by_func = TruncQuarter


#     elif period == 'annuel':
#         start_date = datetime(current_year, 1, 1)
#         end_date = datetime(current_year, 12, 31, 23, 59, 59)
#         group_by_func = TruncYear

#     elif period == 'autre':
#         try:
#             start_date_obj = datetime.strptime(start_date_param, '%Y-%m-%d')
#             end_date_obj = datetime.strptime(end_date_param, '%Y-%m-%d')
            
#             start_date = datetime.combine(start_date_obj.date(), datetime.min.time())
#             end_date = datetime.combine(end_date_obj.date(), datetime.max.time())
            
#         except:
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate 

#     # Assurez-vous que les dates sont conscientes du fuseau horaire (aware)
#     if start_date and not timezone.is_aware(start_date):
#         start_date = timezone.make_aware(start_date)
#     if end_date and not timezone.is_aware(end_date):
#         end_date = timezone.make_aware(end_date)
    
#     return {
#         'start_dt': start_date, 
#         'end_dt': end_date, 
#         'group_by_func': group_by_func
#     }

# # ----------------------------------------------------
# # FONCTION : STATISTIQUES DASHBOARD 
# # ----------------------------------------------------
# def statistiques_dashboard(request):
    
#     today = timezone.localdate()
    
#     # Récupération des paramètres avec VALEURS PAR DÉFAUT
#     period = request.GET.get('period', 'aujourdhui')
#     selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
#     start_date_param = request.GET.get('start_date', today.strftime('%Y-%m-%d'))
#     end_date_param = request.GET.get('end_date', today.strftime('%Y-%m-%d'))

    
#     # 1. Détermination de la période
#     time_info = get_time_range_filter(
#         period, 
#         today.year, 
#         today.month, 
#         selected_date, 
#         start_date_param, 
#         end_date_param
#     )
#     start_dt = time_info['start_dt']
#     end_dt = time_info['end_dt']
#     group_by_func = time_info['group_by_func']
    
#     # 2. Contexte pour les filtres (UI)
#     all_years_qs = RapportVenteNocturne.objects.values_list('start_time__year', flat=True).distinct()
#     available_years = sorted(list(set(all_years_qs)), reverse=True)
    
#     context = {
#         'period': period,
#         'selected_date': selected_date,
#         'start_date_param': start_date_param,
#         'end_date_param': end_date_param,
#         'available_years': available_years,
#         'current_graph': request.GET.get('graph', 'financial'),
#     }
    
    
#     # ----------------------------------------------------
#     # FONCTION D'AGRÉGATION
#     # ----------------------------------------------------
#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
#         qs = model.objects.all()
        
#         # Filtre sur la plage de temps [start_dt, end_dt]
#         range_filter_key = f'{date_field}__range'
        
#         if start_dt and end_dt:
#              qs = qs.filter(**{range_filter_key: (start_dt, end_dt)}) 

#         if extra_filter:
#             qs = qs.filter(**extra_filter)

#         data = defaultdict(lambda: 0)
        
#         # Truncation pour le regroupement
#         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
#             total=Sum(amount_field)
#         ).order_by('date_group')
        
#         # Logique de Formattage des Labels
#         for item in qs:
#             if item['date_group']:
#                 date_group = item['date_group']
#                 label = ""
                
#                 if isinstance(date_group, datetime):
#                     date_group = date_group.date()
                
#                 if period == 'trimestriel':
#                     q_num = (date_group.month - 1) // 3 + 1
#                     label = f"T{q_num}/{date_group.year}"
#                 elif period == 'hebdomadaire':
#                     # Utiliser %V pour le numéro de semaine ISO
#                     label = date_group.strftime('Semaine %V (%Y)') 
#                 elif period == 'annuel':
#                     label = date_group.strftime('%Y')
#                 elif period == 'mensuel':
#                     label = date_group.strftime('%Y-%m')
#                 elif period in ['aujourdhui', 'journalier', 'autre']:
#                     label = date_group.strftime('%Y-%m-%d')
                
#                 data[label] = float(item['total'] or 0)
#         return data


#     # ----------------------------------------------------
#     # 3. Récupération des données pour les graphiques FINANCIERS (RapportVenteNocturne)
#     # ----------------------------------------------------
    
#     base_model = RapportVenteNocturne
#     date_field = 'start_time'
#     # Filtrer les rapports terminés
#     extra_filter_completed = {'end_time__isnull': False}

#     data_ca = get_aggregated_data(base_model, date_field, 'montant_total_vente', extra_filter=extra_filter_completed)
#     data_impayes = get_aggregated_data(base_model, date_field, 'montant_total_impayees', extra_filter=extra_filter_completed)
#     data_depenses = get_aggregated_data(base_model, date_field, 'montant_total_depenses', extra_filter=extra_filter_completed)
#     data_avances = get_aggregated_data(base_model, date_field, 'montant_total_avances', extra_filter=extra_filter_completed)
        
#     all_labels = sorted(list(
#         set(data_ca.keys()) | set(data_impayes.keys()) | set(data_depenses.keys()) | set(data_avances.keys())
#     ))

#     context['ca_labels'] = json.dumps(all_labels)
#     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels]) 
#     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
#     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
#     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])
    
#     # ----------------------------------------------------
#     # 2. VENTES PAR BOISSON (DetailVenteBoisson)
#     # ----------------------------------------------------
    
#     # IDs des rapports terminés dans la période pour filtrer les autres modèles
#     rapport_ids = RapportVenteNocturne.objects.filter(
#         start_time__range=(start_dt, end_dt),
#         end_time__isnull=False
#     ).values_list('id', flat=True)

#     boissons_quantite = DetailVenteBoisson.objects.filter(
#         rapport_id__in=rapport_ids
#     ).values('boisson__nom').annotate(
#         total_quantite=Sum('quantite_totale')
#     ).order_by('-total_quantite')

#     context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])
#     context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])

#     # ----------------------------------------------------
#     # 3. & 4. VENTES PAR PERSONNEL (PerformancePersonnelNocturne)
#     # ----------------------------------------------------

#     personnel_total_qs = PerformancePersonnelNocturne.objects.filter(
#         rapport_id__in=rapport_ids
#     ).annotate(
#         personnel_nom=Concat(
#             'personnel__prenom', 
#             Value(' '),
#             'personnel__nom',
#             output_field=models.CharField()
#         )
#     ).values('personnel_nom').annotate(
#         total_quantite=Sum('quantite_totale_boissons_vendues')
#     ).order_by('-total_quantite')

#     context['personnel_total_labels'] = json.dumps([p['personnel_nom'] for p in personnel_total_qs])
#     context['personnel_total_data'] = json.dumps([p['total_quantite'] or 0 for p in personnel_total_qs])

#     # ----------------------------------------------------
#     # 5. TOP CLIENTS (Commande) - CORRECTION APPLIQUÉE ICI
#     # ----------------------------------------------------
    
#     # CORRECTION : Utiliser date_validation au lieu du champ 'rapport' qui n'existe pas
#     top_clients_qs = Commande.objects.filter(
#         numero_telephone__isnull=False, 
#         date_validation__range=(start_dt, end_dt),
#         statut__in=['payer', 'impayee']
#     ).values('numero_telephone', 'client_nom', 'client_prenom').annotate(
#         total_depense=Sum('montant_total', output_field=DecimalField())
#     ).order_by('-total_depense')[:10]
    
#     top_clients_labels = []
#     top_clients_data = []
    
#     for client in top_clients_qs:
#         # Construction du nom complet
#         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
        
#         # Affichage (Nom complet + Téléphone)
#         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
        
#         top_clients_labels.append(client_display)
#         top_clients_data.append(float(client['total_depense'] or 0))
        
#     context['top_clients_labels'] = json.dumps(top_clients_labels)
#     context['top_clients_data'] = json.dumps(top_clients_data)

#     return render(request, 'statistiques/dashboard.html', context)


######################## 28 -10- 2025 #################
# from django.shortcuts import render
# from django.db import models
# from django.db.models import Sum, F, DecimalField, Value, ExpressionWrapper
# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate, Concat
# from django.utils import timezone
# from datetime import timedelta, datetime
# from collections import defaultdict
# import json
# from django.db.models import Q


# # Import de vos modèles
# from commandes.models import Commande
# from avances.models import Avance
# from depenses.models import Depense
# from personnel.models import Personnel
# from ventes.models import RapportVenteNocturne, DetailVenteProduit, PerformancePersonnelNocturne 


# # ----------------------------------------------------
# # FONCTION : DÉTERMINER LES BORNES TEMPORELLES
# # ----------------------------------------------------
# def get_time_range_filter(period, current_year, current_month, current_date, start_date_param=None, end_date_param=None):
#     """Calcule les bornes (datetime) pour la période donnée, basé sur le début de la transaction."""

#     now = timezone.now()
#     today = timezone.localdate()
    
#     start_date = None
#     end_date = None
#     group_by_func = TruncDate
    
#     if period == 'aujourdhui':
#         start_date = datetime.combine(today, datetime.min.time())
#         end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate
        
#     elif period == 'journalier':
#         try:
#             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
#             start_date = datetime.combine(date_obj, datetime.min.time())
#             end_date = datetime.combine(date_obj, datetime.max.time())
#         except ValueError:
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate

#     elif period == 'hebdomadaire':
#         start_of_week = today - timedelta(days=today.weekday())
#         start_date = datetime.combine(start_of_week, datetime.min.time())
#         end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())
#         group_by_func = TruncWeek
        
#     elif period == 'mensuel':
#         start_date = datetime(today.year, today.month, 1)
#         # Calcul du dernier jour du mois
#         if today.month == 12:
#             end_date = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)
#         group_by_func = TruncMonth
    
#     elif period == 'trimestriel':
#         q = (today.month - 1) // 3 + 1
#         start_month = 3 * q - 2
        
#         start_date = datetime(today.year, start_month, 1)
        
#         next_month_start = start_month + 3
#         if next_month_start > 12:
#             end_date = datetime(today.year + 1, next_month_start % 12, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, next_month_start, 1) - timedelta(seconds=1)
#         group_by_func = TruncQuarter


#     elif period == 'annuel':
#         start_date = datetime(current_year, 1, 1)
#         end_date = datetime(current_year, 12, 31, 23, 59, 59)
#         group_by_func = TruncYear

#     elif period == 'autre':
#         try:
#             start_date_obj = datetime.strptime(start_date_param, '%Y-%m-%d')
#             end_date_obj = datetime.strptime(end_date_param, '%Y-%m-%d')
            
#             start_date = datetime.combine(start_date_obj.date(), datetime.min.time())
#             end_date = datetime.combine(end_date_obj.date(), datetime.max.time())
            
#         except:
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate 

#     # Assurez-vous que les dates sont conscientes du fuseau horaire (aware)
#     if start_date and not timezone.is_aware(start_date):
#         start_date = timezone.make_aware(start_date)
#     if end_date and not timezone.is_aware(end_date):
#         end_date = timezone.make_aware(end_date)
    
#     return {
#         'start_dt': start_date, 
#         'end_dt': end_date, 
#         'group_by_func': group_by_func
#     }

# # ----------------------------------------------------
# # FONCTION : STATISTIQUES DASHBOARD 
# # ----------------------------------------------------
# def statistiques_dashboard(request):
    
#     today = timezone.localdate()
    
#     # Récupération des paramètres avec VALEURS PAR DÉFAUT
#     period = request.GET.get('period', 'aujourdhui')
#     selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
#     start_date_param = request.GET.get('start_date', today.strftime('%Y-%m-%d'))
#     end_date_param = request.GET.get('end_date', today.strftime('%Y-%m-%d'))

    
#     # 1. Détermination de la période
#     time_info = get_time_range_filter(
#         period, 
#         today.year, 
#         today.month, 
#         selected_date, 
#         start_date_param, 
#         end_date_param
#     )
#     start_dt = time_info['start_dt']
#     end_dt = time_info['end_dt']
#     group_by_func = time_info['group_by_func']
    
#     # 2. Contexte pour les filtres (UI)
#     all_years_qs = RapportVenteNocturne.objects.values_list('start_time__year', flat=True).distinct()
#     available_years = sorted(list(set(all_years_qs)), reverse=True)
    
#     context = {
#         'period': period,
#         'selected_date': selected_date,
#         'start_date_param': start_date_param,
#         'end_date_param': end_date_param,
#         'available_years': available_years,
#         'current_graph': request.GET.get('graph', 'financial'),
#     }
    
    
#     # ----------------------------------------------------
#     # FONCTION D'AGRÉGATION
#     # ----------------------------------------------------
#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
#         qs = model.objects.all()
        
#         # Filtre sur la plage de temps [start_dt, end_dt]
#         range_filter_key = f'{date_field}__range'
        
#         if start_dt and end_dt:
#              qs = qs.filter(**{range_filter_key: (start_dt, end_dt)}) 

#         if extra_filter:
#             qs = qs.filter(**extra_filter)

#         data = defaultdict(lambda: 0)
        
#         # Truncation pour le regroupement
#         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
#             total=Sum(amount_field)
#         ).order_by('date_group')
        
#         # Logique de Formattage des Labels
#         for item in qs:
#             if item['date_group']:
#                 date_group = item['date_group']
#                 label = ""
                
#                 if isinstance(date_group, datetime):
#                     date_group = date_group.date()
                
#                 if period == 'trimestriel':
#                     q_num = (date_group.month - 1) // 3 + 1
#                     label = f"T{q_num}/{date_group.year}"
#                 elif period == 'hebdomadaire':
#                     # Utiliser %V pour le numéro de semaine ISO
#                     label = date_group.strftime('Semaine %V (%Y)') 
#                 elif period == 'annuel':
#                     label = date_group.strftime('%Y')
#                 elif period == 'mensuel':
#                     label = date_group.strftime('%Y-%m')
#                 elif period in ['aujourdhui', 'journalier', 'autre']:
#                     label = date_group.strftime('%Y-%m-%d')
                
#                 data[label] = float(item['total'] or 0)
#         return data


#     # ----------------------------------------------------
#     # 3. Récupération des données pour les graphiques FINANCIERS (RapportVenteNocturne)
#     # ----------------------------------------------------
    
#     base_model = RapportVenteNocturne
#     date_field = 'start_time'
#     # Filtrer les rapports terminés
#     extra_filter_completed = {'end_time__isnull': False}

#     # Données financières globales
#     data_ca = get_aggregated_data(base_model, date_field, 'chiffre_affaire', extra_filter=extra_filter_completed)
#     data_marge = get_aggregated_data(base_model, date_field, 'marge_totale', extra_filter=extra_filter_completed)
#     data_impayes = get_aggregated_data(base_model, date_field, 'montant_total_impayees', extra_filter=extra_filter_completed)
#     data_depenses = get_aggregated_data(base_model, date_field, 'montant_total_depenses', extra_filter=extra_filter_completed)
#     data_avances = get_aggregated_data(base_model, date_field, 'montant_total_avances', extra_filter=extra_filter_completed)
#     data_benefice = get_aggregated_data(base_model, date_field, 'benefice_net', extra_filter=extra_filter_completed)
        
#     all_labels = sorted(list(
#         set(data_ca.keys()) | set(data_marge.keys()) | set(data_impayes.keys()) | 
#         set(data_depenses.keys()) | set(data_avances.keys()) | set(data_benefice.keys())
#     ))

#     context['ca_labels'] = json.dumps(all_labels)
#     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels]) 
#     context['marge_data'] = json.dumps([data_marge.get(d, 0) for d in all_labels])
#     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
#     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
#     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])
#     context['benefice_data'] = json.dumps([data_benefice.get(d, 0) for d in all_labels])
    
#     # ----------------------------------------------------
#     # 4. VENTES PAR PRODUIT (DetailVenteProduit)
#     # ----------------------------------------------------
    
#     # IDs des rapports terminés dans la période pour filtrer les autres modèles
#     rapport_ids = RapportVenteNocturne.objects.filter(
#         start_time__range=(start_dt, end_dt),
#         end_time__isnull=False
#     ).values_list('id', flat=True)

#     # Performance des produits par quantité
#     produits_quantite = DetailVenteProduit.objects.filter(
#         rapport_id__in=rapport_ids
#     ).values('produit__nom').annotate(
#         total_quantite=Sum('quantite_totale')
#     ).order_by('-total_quantite')[:15]  # Limiter à 15 produits pour la lisibilité

#     context['produits_labels'] = json.dumps([p['produit__nom'] for p in produits_quantite])
#     context['produits_data'] = json.dumps([p['total_quantite'] or 0 for p in produits_quantite])

#     # Performance des produits par marge
#     produits_marge = DetailVenteProduit.objects.filter(
#         rapport_id__in=rapport_ids
#     ).values('produit__nom').annotate(
#         total_marge=Sum('marge_totale_produit')
#     ).order_by('-total_marge')[:15]  # Limiter à 15 produits pour la lisibilité

#     context['produits_marge_labels'] = json.dumps([p['produit__nom'] for p in produits_marge])
#     context['produits_marge_data'] = json.dumps([float(p['total_marge'] or 0) for p in produits_marge])

#     # ----------------------------------------------------
#     # 5. PERFORMANCE DU PERSONNEL (PerformancePersonnelNocturne)
#     # ----------------------------------------------------

#     # Performance du personnel par quantité
#     personnel_quantite_qs = PerformancePersonnelNocturne.objects.filter(
#         rapport_id__in=rapport_ids
#     ).annotate(
#         personnel_nom=Concat(
#             'personnel__prenom', 
#             Value(' '),
#             'personnel__nom',
#             output_field=models.CharField()
#         )
#     ).values('personnel_nom').annotate(
#         total_quantite=Sum('quantite_totale_produits_vendus')
#     ).order_by('-total_quantite')

#     context['personnel_quantite_labels'] = json.dumps([p['personnel_nom'] for p in personnel_quantite_qs])
#     context['personnel_quantite_data'] = json.dumps([p['total_quantite'] or 0 for p in personnel_quantite_qs])

#     # CORRECTION : Calcul de la marge réelle du personnel à partir des détails des produits
#     # On va calculer la marge totale générée par chaque personnel
#     personnel_marge_data = {}
    
#     # Récupérer tous les détails de vente pour les rapports concernés
#     details_ventes = DetailVenteProduit.objects.filter(
#         rapport_id__in=rapport_ids
#     ).select_related('rapport', 'produit')
    
#     # Pour chaque détail de vente, trouver le personnel associé via PerformancePersonnelNocturne
#     for detail in details_ventes:
#         # Trouver les performances du personnel pour ce rapport
#         performances = PerformancePersonnelNocturne.objects.filter(
#             rapport=detail.rapport
#         ).select_related('personnel')
        
#         for perf in performances:
#             nom_complet = f"{perf.personnel.prenom} {perf.personnel.nom}"
#             if nom_complet not in personnel_marge_data:
#                 personnel_marge_data[nom_complet] = 0
            
#             # Répartir la marge proportionnellement au montant vendu par chaque personnel
#             if perf.montant_vendu_total > 0 and detail.rapport.chiffre_affaire > 0:
#                 proportion = perf.montant_vendu_total / detail.rapport.chiffre_affaire
#                 marge_attribuee = detail.marge_totale_produit * proportion
#                 personnel_marge_data[nom_complet] += marge_attribuee

#     # Trier par marge décroissante
#     personnel_marge_trie = sorted(
#         personnel_marge_data.items(), 
#         key=lambda x: x[1], 
#         reverse=True
#     )
    
#     personnel_marge_labels = [item[0] for item in personnel_marge_trie]
#     personnel_marge_values = [float(item[1]) for item in personnel_marge_trie]

#     context['personnel_marge_labels'] = json.dumps(personnel_marge_labels)
#     context['personnel_marge_data'] = json.dumps(personnel_marge_values)

#     # ----------------------------------------------------
#     # 6. TOP CLIENTS (Commande)
#     # ----------------------------------------------------
    
#     top_clients_qs = Commande.objects.filter(
#         numero_telephone__isnull=False, 
#         date_validation__range=(start_dt, end_dt),
#         statut__in=['payer', 'impayee']
#     ).values('numero_telephone', 'client_nom', 'client_prenom').annotate(
#         total_depense=Sum('montant_total', output_field=DecimalField())
#     ).order_by('-total_depense')[:10]
    
#     top_clients_labels = []
#     top_clients_data = []
    
#     for client in top_clients_qs:
#         # Construction du nom complet
#         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
        
#         # Affichage (Nom complet + Téléphone)
#         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
        
#         top_clients_labels.append(client_display)
#         top_clients_data.append(float(client['total_depense'] or 0))
        
#     context['top_clients_labels'] = json.dumps(top_clients_labels)
#     context['top_clients_data'] = json.dumps(top_clients_data)

#     return render(request, 'statistiques/dashboard.html', context)



############### 29- 10- 2025 #########


# from commandes.models import Commande

# from avances.models import Avance

# from depenses.models import Depense

# from personnel.models import Personnel

# from ventes.models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne 


# from django.shortcuts import render
# from django.db import models
# from django.db.models import Sum, F, DecimalField, Value
# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate, Concat
# from django.utils import timezone
# from datetime import timedelta, datetime
# from collections import defaultdict
# import json
# from django.db.models import Q


# # Import de vos modèles
# from commandes.models import Commande
# from avances.models import Avance
# from depenses.models import Depense
# from personnel.models import Personnel
# from ventes.models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne 



# # ----------------------------------------------------

# # FONCTION : DÉTERMINER LES BORNES TEMPORELLES

# # ----------------------------------------------------

# def get_time_range_filter(period, current_year, current_month, current_date, start_date_param=None, end_date_param=None):

#     """Calcule les bornes (datetime) pour la période donnée, basé sur le début de la transaction."""



#     now = timezone.now()

#     today = timezone.localdate()

    

#     start_date = None

#     end_date = None

#     group_by_func = TruncDate

    

#     if period == 'aujourdhui':

#         start_date = datetime.combine(today, datetime.min.time())

#         end_date = datetime.combine(today, datetime.max.time())

#         group_by_func = TruncDate

        

#     elif period == 'journalier':

#         try:

#             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()

#             start_date = datetime.combine(date_obj, datetime.min.time())

#             end_date = datetime.combine(date_obj, datetime.max.time())

#         except ValueError:

#             start_date = datetime.combine(today, datetime.min.time())

#             end_date = datetime.combine(today, datetime.max.time())

#         group_by_func = TruncDate



#     elif period == 'hebdomadaire':

#         start_of_week = today - timedelta(days=today.weekday())

#         start_date = datetime.combine(start_of_week, datetime.min.time())

#         end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())

#         group_by_func = TruncWeek

        

#     elif period == 'mensuel':

#         start_date = datetime(today.year, today.month, 1)

#         # Calcul du dernier jour du mois

#         if today.month == 12:

#             end_date = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)

#         else:

#             end_date = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)

#         group_by_func = TruncMonth

    

#     elif period == 'trimestriel':

#         q = (today.month - 1) // 3 + 1

#         start_month = 3 * q - 2

        

#         start_date = datetime(today.year, start_month, 1)

        

#         next_month_start = start_month + 3

#         if next_month_start > 12:

#             end_date = datetime(today.year + 1, next_month_start % 12, 1) - timedelta(seconds=1)

#         else:

#             end_date = datetime(today.year, next_month_start, 1) - timedelta(seconds=1)

#         group_by_func = TruncQuarter





#     elif period == 'annuel':

#         start_date = datetime(current_year, 1, 1)

#         end_date = datetime(current_year, 12, 31, 23, 59, 59)

#         group_by_func = TruncYear



#     elif period == 'autre':

#         try:

#             start_date_obj = datetime.strptime(start_date_param, '%Y-%m-%d')

#             end_date_obj = datetime.strptime(end_date_param, '%Y-%m-%d')

            

#             start_date = datetime.combine(start_date_obj.date(), datetime.min.time())

#             end_date = datetime.combine(end_date_obj.date(), datetime.max.time())

            

#         except:

#             start_date = datetime.combine(today, datetime.min.time())

#             end_date = datetime.combine(today, datetime.max.time())

#         group_by_func = TruncDate 



#     # Assurez-vous que les dates sont conscientes du fuseau horaire (aware)

#     if start_date and not timezone.is_aware(start_date):

#         start_date = timezone.make_aware(start_date)

#     if end_date and not timezone.is_aware(end_date):

#         end_date = timezone.make_aware(end_date)

    

#     return {

#         'start_dt': start_date, 

#         'end_dt': end_date, 

#         'group_by_func': group_by_func

#     }



# # ----------------------------------------------------

# # FONCTION : STATISTIQUES DASHBOARD 

# # ----------------------------------------------------

# def statistiques_dashboard(request):

    

#     today = timezone.localdate()

    

#     # Récupération des paramètres avec VALEURS PAR DÉFAUT

#     period = request.GET.get('period', 'aujourdhui')

#     selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))

#     start_date_param = request.GET.get('start_date', today.strftime('%Y-%m-%d'))

#     end_date_param = request.GET.get('end_date', today.strftime('%Y-%m-%d'))



    

#     # 1. Détermination de la période

#     time_info = get_time_range_filter(

#         period, 

#         today.year, 

#         today.month, 

#         selected_date, 

#         start_date_param, 

#         end_date_param

#     )

#     start_dt = time_info['start_dt']

#     end_dt = time_info['end_dt']

#     group_by_func = time_info['group_by_func']

    

#     # 2. Contexte pour les filtres (UI)

#     all_years_qs = RapportVenteNocturne.objects.values_list('start_time__year', flat=True).distinct()

#     available_years = sorted(list(set(all_years_qs)), reverse=True)

    

#     context = {

#         'period': period,

#         'selected_date': selected_date,

#         'start_date_param': start_date_param,

#         'end_date_param': end_date_param,

#         'available_years': available_years,

#         'current_graph': request.GET.get('graph', 'financial'),

#     }

    

    

#     # ----------------------------------------------------

#     # FONCTION D'AGRÉGATION

#     # ----------------------------------------------------

#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):

#         qs = model.objects.all()

        

#         # Filtre sur la plage de temps [start_dt, end_dt]

#         range_filter_key = f'{date_field}__range'

        

#         if start_dt and end_dt:

#              qs = qs.filter(**{range_filter_key: (start_dt, end_dt)}) 



#         if extra_filter:

#             qs = qs.filter(**extra_filter)



#         data = defaultdict(lambda: 0)

        

#         # Truncation pour le regroupement

#         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(

#             total=Sum(amount_field)

#         ).order_by('date_group')

        

#         # Logique de Formattage des Labels

#         for item in qs:

#             if item['date_group']:

#                 date_group = item['date_group']

#                 label = ""

                

#                 if isinstance(date_group, datetime):

#                     date_group = date_group.date()

                

#                 if period == 'trimestriel':

#                     q_num = (date_group.month - 1) // 3 + 1

#                     label = f"T{q_num}/{date_group.year}"

#                 elif period == 'hebdomadaire':

#                     # Utiliser %V pour le numéro de semaine ISO

#                     label = date_group.strftime('Semaine %V (%Y)') 

#                 elif period == 'annuel':

#                     label = date_group.strftime('%Y')

#                 elif period == 'mensuel':

#                     label = date_group.strftime('%Y-%m')

#                 elif period in ['aujourdhui', 'journalier', 'autre']:

#                     label = date_group.strftime('%Y-%m-%d')

                

#                 data[label] = float(item['total'] or 0)

#         return data





#     # ----------------------------------------------------

#     # 3. Récupération des données pour les graphiques FINANCIERS (RapportVenteNocturne)

#     # ----------------------------------------------------

    

#     base_model = RapportVenteNocturne

#     date_field = 'start_time'

#     # Filtrer les rapports terminés

#     extra_filter_completed = {'end_time__isnull': False}



#     data_ca = get_aggregated_data(base_model, date_field, 'montant_total_vente', extra_filter=extra_filter_completed)

#     data_impayes = get_aggregated_data(base_model, date_field, 'montant_total_impayees', extra_filter=extra_filter_completed)

#     data_depenses = get_aggregated_data(base_model, date_field, 'montant_total_depenses', extra_filter=extra_filter_completed)

#     data_avances = get_aggregated_data(base_model, date_field, 'montant_total_avances', extra_filter=extra_filter_completed)

        

#     all_labels = sorted(list(

#         set(data_ca.keys()) | set(data_impayes.keys()) | set(data_depenses.keys()) | set(data_avances.keys())

#     ))



#     context['ca_labels'] = json.dumps(all_labels)

#     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels]) 

#     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])

#     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])

#     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])

    

#     # ----------------------------------------------------

#     # 2. VENTES PAR BOISSON (DetailVenteBoisson)

#     # ----------------------------------------------------

    

#     # IDs des rapports terminés dans la période pour filtrer les autres modèles

#     rapport_ids = RapportVenteNocturne.objects.filter(

#         start_time__range=(start_dt, end_dt),

#         end_time__isnull=False

#     ).values_list('id', flat=True)



#     boissons_quantite = DetailVenteBoisson.objects.filter(

#         rapport_id__in=rapport_ids

#     ).values('boisson__nom').annotate(

#         total_quantite=Sum('quantite_totale')

#     ).order_by('-total_quantite')



#     context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])

#     context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])



#     # ----------------------------------------------------

#     # 3. & 4. VENTES PAR PERSONNEL (PerformancePersonnelNocturne)

#     # ----------------------------------------------------



#     personnel_total_qs = PerformancePersonnelNocturne.objects.filter(

#         rapport_id__in=rapport_ids

#     ).annotate(

#         personnel_nom=Concat(

#             'personnel__prenom', 

#             Value(' '),

#             'personnel__nom',

#             output_field=models.CharField()

#         )

#     ).values('personnel_nom').annotate(

#         total_quantite=Sum('quantite_totale_boissons_vendues')

#     ).order_by('-total_quantite')



#     context['personnel_total_labels'] = json.dumps([p['personnel_nom'] for p in personnel_total_qs])

#     context['personnel_total_data'] = json.dumps([p['total_quantite'] or 0 for p in personnel_total_qs])



#     # ----------------------------------------------------

#     # 5. TOP CLIENTS (Commande) - CORRECTION APPLIQUÉE ICI

#     # ----------------------------------------------------

    

#     # CORRECTION : Utiliser date_validation au lieu du champ 'rapport' qui n'existe pas

#     top_clients_qs = Commande.objects.filter(

#         numero_telephone__isnull=False, 

#         date_validation__range=(start_dt, end_dt),

#         statut__in=['payer', 'impayee']

#     ).values('numero_telephone', 'client_nom', 'client_prenom').annotate(

#         total_depense=Sum('montant_total', output_field=DecimalField())

#     ).order_by('-total_depense')[:10]

    

#     top_clients_labels = []

#     top_clients_data = []

    

#     for client in top_clients_qs:

#         # Construction du nom complet

#         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()

        

#         # Affichage (Nom complet + Téléphone)

#         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']

        

#         top_clients_labels.append(client_display)

#         top_clients_data.append(float(client['total_depense'] or 0))

        

#     context['top_clients_labels'] = json.dumps(top_clients_labels)

#     context['top_clients_data'] = json.dumps(top_clients_data)



#     return render(request, 'statistiques/dashboard.html', context)



#####################




# from django.shortcuts import render

# from django.db import models

# from django.db.models import Sum, F, DecimalField, Value

# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate, Concat

# from django.utils import timezone

# from datetime import timedelta, datetime

# from collections import defaultdict

# import json

# from django.db.models import Q





# # Import de vos modèles

# from commandes.models import Commande

# from avances.models import Avance

# from depenses.models import Depense

# from personnel.models import Personnel

# from ventes.models import RapportVenteNocturne, DetailVenteBoisson, PerformancePersonnelNocturne 





# # ----------------------------------------------------

# # FONCTION : DÉTERMINER LES BORNES TEMPORELLES

# # ----------------------------------------------------

# def get_time_range_filter(period, current_year, current_month, current_date, start_date_param=None, end_date_param=None):

#     """Calcule les bornes (datetime) pour la période donnée, basé sur le début de la transaction."""



#     now = timezone.now()

#     today = timezone.localdate()

    

#     start_date = None

#     end_date = None

#     group_by_func = TruncDate

    

#     if period == 'aujourdhui':

#         start_date = datetime.combine(today, datetime.min.time())

#         end_date = datetime.combine(today, datetime.max.time())

#         group_by_func = TruncDate

        

#     elif period == 'journalier':

#         try:

#             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()

#             start_date = datetime.combine(date_obj, datetime.min.time())

#             end_date = datetime.combine(date_obj, datetime.max.time())

#         except ValueError:

#             start_date = datetime.combine(today, datetime.min.time())

#             end_date = datetime.combine(today, datetime.max.time())

#         group_by_func = TruncDate



#     elif period == 'hebdomadaire':

#         start_of_week = today - timedelta(days=today.weekday())

#         start_date = datetime.combine(start_of_week, datetime.min.time())

#         end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())

#         group_by_func = TruncWeek

        

#     elif period == 'mensuel':

#         start_date = datetime(today.year, today.month, 1)

#         # Calcul du dernier jour du mois

#         if today.month == 12:

#             end_date = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)

#         else:

#             end_date = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)

#         group_by_func = TruncMonth

    

#     elif period == 'trimestriel':

#         q = (today.month - 1) // 3 + 1

#         start_month = 3 * q - 2

        

#         start_date = datetime(today.year, start_month, 1)

        

#         next_month_start = start_month + 3

#         if next_month_start > 12:

#             end_date = datetime(today.year + 1, next_month_start % 12, 1) - timedelta(seconds=1)

#         else:

#             end_date = datetime(today.year, next_month_start, 1) - timedelta(seconds=1)

#         group_by_func = TruncQuarter





#     elif period == 'annuel':

#         start_date = datetime(current_year, 1, 1)

#         end_date = datetime(current_year, 12, 31, 23, 59, 59)

#         group_by_func = TruncYear



#     elif period == 'autre':

#         try:

#             start_date_obj = datetime.strptime(start_date_param, '%Y-%m-%d')

#             end_date_obj = datetime.strptime(end_date_param, '%Y-%m-%d')

            

#             start_date = datetime.combine(start_date_obj.date(), datetime.min.time())

#             end_date = datetime.combine(end_date_obj.date(), datetime.max.time())

            

#         except:

#             start_date = datetime.combine(today, datetime.min.time())

#             end_date = datetime.combine(today, datetime.max.time())

#         group_by_func = TruncDate 



#     # Assurez-vous que les dates sont conscientes du fuseau horaire (aware)

#     if start_date and not timezone.is_aware(start_date):

#         start_date = timezone.make_aware(start_date)

#     if end_date and not timezone.is_aware(end_date):

#         end_date = timezone.make_aware(end_date)

    

#     return {

#         'start_dt': start_date, 

#         'end_dt': end_date, 

#         'group_by_func': group_by_func

#     }



# # ----------------------------------------------------

# # FONCTION : STATISTIQUES DASHBOARD 

# # ----------------------------------------------------

# def statistiques_dashboard(request):

    

#     today = timezone.localdate()

    

#     # Récupération des paramètres avec VALEURS PAR DÉFAUT

#     period = request.GET.get('period', 'aujourdhui')

#     selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))

#     start_date_param = request.GET.get('start_date', today.strftime('%Y-%m-%d'))

#     end_date_param = request.GET.get('end_date', today.strftime('%Y-%m-%d'))



    

#     # 1. Détermination de la période

#     time_info = get_time_range_filter(

#         period, 

#         today.year, 

#         today.month, 

#         selected_date, 

#         start_date_param, 

#         end_date_param

#     )

#     start_dt = time_info['start_dt']

#     end_dt = time_info['end_dt']

#     group_by_func = time_info['group_by_func']

    

#     # 2. Contexte pour les filtres (UI)

#     all_years_qs = RapportVenteNocturne.objects.values_list('start_time__year', flat=True).distinct()

#     available_years = sorted(list(set(all_years_qs)), reverse=True)

    

#     context = {

#         'period': period,

#         'selected_date': selected_date,

#         'start_date_param': start_date_param,

#         'end_date_param': end_date_param,

#         'available_years': available_years,

#         'current_graph': request.GET.get('graph', 'financial'),

#     }

    

    

#     # ----------------------------------------------------

#     # FONCTION D'AGRÉGATION

#     # ----------------------------------------------------

#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):

#         qs = model.objects.all()

        

#         # Filtre sur la plage de temps [start_dt, end_dt]

#         range_filter_key = f'{date_field}__range'

        

#         if start_dt and end_dt:

#              qs = qs.filter(**{range_filter_key: (start_dt, end_dt)}) 



#         if extra_filter:

#             qs = qs.filter(**extra_filter)



#         data = defaultdict(lambda: 0)

        

#         # Truncation pour le regroupement

#         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(

#             total=Sum(amount_field)

#         ).order_by('date_group')

        

#         # Logique de Formattage des Labels

#         for item in qs:

#             if item['date_group']:

#                 date_group = item['date_group']

#                 label = ""

                

#                 if isinstance(date_group, datetime):

#                     date_group = date_group.date()

                

#                 if period == 'trimestriel':

#                     q_num = (date_group.month - 1) // 3 + 1

#                     label = f"T{q_num}/{date_group.year}"

#                 elif period == 'hebdomadaire':

#                     # Utiliser %V pour le numéro de semaine ISO

#                     label = date_group.strftime('Semaine %V (%Y)') 

#                 elif period == 'annuel':

#                     label = date_group.strftime('%Y')

#                 elif period == 'mensuel':

#                     label = date_group.strftime('%Y-%m')

#                 elif period in ['aujourdhui', 'journalier', 'autre']:

#                     label = date_group.strftime('%Y-%m-%d')

                

#                 data[label] = float(item['total'] or 0)

#         return data





#     # ----------------------------------------------------

#     # 3. Récupération des données pour les graphiques FINANCIERS (RapportVenteNocturne)

#     # ----------------------------------------------------

    

#     base_model = RapportVenteNocturne

#     date_field = 'start_time'

#     # Filtrer les rapports terminés

#     extra_filter_completed = {'end_time__isnull': False}



#     data_ca = get_aggregated_data(base_model, date_field, 'montant_total_vente', extra_filter=extra_filter_completed)

#     data_impayes = get_aggregated_data(base_model, date_field, 'montant_total_impayees', extra_filter=extra_filter_completed)

#     data_depenses = get_aggregated_data(base_model, date_field, 'montant_total_depenses', extra_filter=extra_filter_completed)

#     data_avances = get_aggregated_data(base_model, date_field, 'montant_total_avances', extra_filter=extra_filter_completed)

        

#     all_labels = sorted(list(

#         set(data_ca.keys()) | set(data_impayes.keys()) | set(data_depenses.keys()) | set(data_avances.keys())

#     ))



#     context['ca_labels'] = json.dumps(all_labels)

#     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels]) 

#     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])

#     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])

#     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])

    

#     # ----------------------------------------------------

#     # 2. VENTES PAR BOISSON (DetailVenteBoisson)

#     # ----------------------------------------------------

    

#     # IDs des rapports terminés dans la période pour filtrer les autres modèles

#     rapport_ids = RapportVenteNocturne.objects.filter(

#         start_time__range=(start_dt, end_dt),

#         end_time__isnull=False

#     ).values_list('id', flat=True)



#     boissons_quantite = DetailVenteBoisson.objects.filter(

#         rapport_id__in=rapport_ids

#     ).values('boisson__nom').annotate(

#         total_quantite=Sum('quantite_totale')

#     ).order_by('-total_quantite')



#     context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])

#     context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])



#     # ----------------------------------------------------

#     # 3. & 4. VENTES PAR PERSONNEL (PerformancePersonnelNocturne)

#     # ----------------------------------------------------



#     personnel_total_qs = PerformancePersonnelNocturne.objects.filter(

#         rapport_id__in=rapport_ids

#     ).annotate(

#         personnel_nom=Concat(

#             'personnel__prenom', 

#             Value(' '),

#             'personnel__nom',

#             output_field=models.CharField()

#         )

#     ).values('personnel_nom').annotate(

#         total_quantite=Sum('quantite_totale_boissons_vendues')

#     ).order_by('-total_quantite')



#     context['personnel_total_labels'] = json.dumps([p['personnel_nom'] for p in personnel_total_qs])

#     context['personnel_total_data'] = json.dumps([p['total_quantite'] or 0 for p in personnel_total_qs])



#     # ----------------------------------------------------

#     # 5. TOP CLIENTS (Commande) - CORRECTION APPLIQUÉE ICI

#     # ----------------------------------------------------

    

#     # CORRECTION : Utiliser date_validation au lieu du champ 'rapport' qui n'existe pas

#     top_clients_qs = Commande.objects.filter(

#         numero_telephone__isnull=False, 

#         date_validation__range=(start_dt, end_dt),

#         statut__in=['payer', 'impayee']

#     ).values('numero_telephone', 'client_nom', 'client_prenom').annotate(

#         total_depense=Sum('montant_total', output_field=DecimalField())

#     ).order_by('-total_depense')[:10]

    

#     top_clients_labels = []

#     top_clients_data = []

    

#     for client in top_clients_qs:

#         # Construction du nom complet

#         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()

        

#         # Affichage (Nom complet + Téléphone)

#         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']

        

#         top_clients_labels.append(client_display)

#         top_clients_data.append(float(client['total_depense'] or 0))

        

#     context['top_clients_labels'] = json.dumps(top_clients_labels)

#     context['top_clients_data'] = json.dumps(top_clients_data)



#     return render(request, 'statistiques/dashboard.html', context)


############# Ancien code non fonctionnel en haut ###########

# from django.shortcuts import render
# from django.db import models
# from django.db.models import Sum, F, DecimalField, Value
# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate, Concat
# from django.utils import timezone
# from datetime import timedelta, datetime
# from collections import defaultdict
# import json
# from django.db.models import Q

# # Import de vos modèles
# from commandes.models import Commande
# from avances.models import Avance
# from depenses.models import Depense
# from personnel.models import Personnel
# from ventes.models import RapportVenteNocturne, DetailVenteProduit, PerformancePersonnelNocturne 

# # ----------------------------------------------------
# # FONCTION : DÉTERMINER LES BORNES TEMPORELLES
# # ----------------------------------------------------
# def get_time_range_filter(period, current_year, current_month, current_date, start_date_param=None, end_date_param=None):
#     """Calcule les bornes (datetime) pour la période donnée, basé sur le début de la transaction."""

#     now = timezone.now()
#     today = timezone.localdate()
    
#     start_date = None
#     end_date = None
#     group_by_func = TruncDate
    
#     if period == 'aujourdhui':
#         start_date = datetime.combine(today, datetime.min.time())
#         end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate
        
#     elif period == 'journalier':
#         try:
#             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
#             start_date = datetime.combine(date_obj, datetime.min.time())
#             end_date = datetime.combine(date_obj, datetime.max.time())
#         except ValueError:
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate

#     elif period == 'hebdomadaire':
#         start_of_week = today - timedelta(days=today.weekday())
#         start_date = datetime.combine(start_of_week, datetime.min.time())
#         end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())
#         group_by_func = TruncWeek
        
#     elif period == 'mensuel':
#         start_date = datetime(today.year, today.month, 1)
#         # Calcul du dernier jour du mois
#         if today.month == 12:
#             end_date = datetime(today.year + 1, 1, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, today.month + 1, 1) - timedelta(seconds=1)
#         group_by_func = TruncMonth
    
#     elif period == 'trimestriel':
#         q = (today.month - 1) // 3 + 1
#         start_month = 3 * q - 2
        
#         start_date = datetime(today.year, start_month, 1)
        
#         next_month_start = start_month + 3
#         if next_month_start > 12:
#             end_date = datetime(today.year + 1, next_month_start % 12, 1) - timedelta(seconds=1)
#         else:
#             end_date = datetime(today.year, next_month_start, 1) - timedelta(seconds=1)
#         group_by_func = TruncQuarter

#     elif period == 'annuel':
#         start_date = datetime(current_year, 1, 1)
#         end_date = datetime(current_year, 12, 31, 23, 59, 59)
#         group_by_func = TruncYear

#     elif period == 'autre':
#         try:
#             start_date_obj = datetime.strptime(start_date_param, '%Y-%m-%d')
#             end_date_obj = datetime.strptime(end_date_param, '%Y-%m-%d')
            
#             start_date = datetime.combine(start_date_obj.date(), datetime.min.time())
#             end_date = datetime.combine(end_date_obj.date(), datetime.max.time())
            
#         except:
#             start_date = datetime.combine(today, datetime.min.time())
#             end_date = datetime.combine(today, datetime.max.time())
#         group_by_func = TruncDate 

#     # Assurez-vous que les dates sont conscientes du fuseau horaire (aware)
#     if start_date and not timezone.is_aware(start_date):
#         start_date = timezone.make_aware(start_date)
#     if end_date and not timezone.is_aware(end_date):
#         end_date = timezone.make_aware(end_date)
    
#     return {
#         'start_dt': start_date, 
#         'end_dt': end_date, 
#         'group_by_func': group_by_func
#     }

# # ----------------------------------------------------
# # FONCTION : STATISTIQUES DASHBOARD 
# # ----------------------------------------------------
# def statistiques_dashboard(request):
    
#     today = timezone.localdate()
    
#     # Récupération des paramètres avec VALEURS PAR DÉFAUT
#     period = request.GET.get('period', 'aujourdhui')
#     selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
#     start_date_param = request.GET.get('start_date', today.strftime('%Y-%m-%d'))
#     end_date_param = request.GET.get('end_date', today.strftime('%Y-%m-%d'))

    
#     # 1. Détermination de la période
#     time_info = get_time_range_filter(
#         period, 
#         today.year, 
#         today.month, 
#         selected_date, 
#         start_date_param, 
#         end_date_param
#     )
#     start_dt = time_info['start_dt']
#     end_dt = time_info['end_dt']
#     group_by_func = time_info['group_by_func']
    
#     # 2. Contexte pour les filtres (UI)
#     all_years_qs = RapportVenteNocturne.objects.values_list('start_time__year', flat=True).distinct()
#     available_years = sorted(list(set(all_years_qs)), reverse=True)
    
#     context = {
#         'period': period,
#         'selected_date': selected_date,
#         'start_date_param': start_date_param,
#         'end_date_param': end_date_param,
#         'available_years': available_years,
#         'current_graph': request.GET.get('graph', 'financial'),
#     }
    
    
#     # ----------------------------------------------------
#     # FONCTION D'AGRÉGATION
#     # ----------------------------------------------------
#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
#         qs = model.objects.all()
        
#         # Filtre sur la plage de temps [start_dt, end_dt]
#         range_filter_key = f'{date_field}__range'
        
#         if start_dt and end_dt:
#              qs = qs.filter(**{range_filter_key: (start_dt, end_dt)}) 

#         if extra_filter:
#             qs = qs.filter(**extra_filter)

#         data = defaultdict(lambda: 0)
        
#         # Truncation pour le regroupement
#         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
#             total=Sum(amount_field)
#         ).order_by('date_group')
        
#         # Logique de Formattage des Labels
#         for item in qs:
#             if item['date_group']:
#                 date_group = item['date_group']
#                 label = ""
                
#                 if isinstance(date_group, datetime):
#                     date_group = date_group.date()
                
#                 if period == 'trimestriel':
#                     q_num = (date_group.month - 1) // 3 + 1
#                     label = f"T{q_num}/{date_group.year}"
#                 elif period == 'hebdomadaire':
#                     # Utiliser %V pour le numéro de semaine ISO
#                     label = date_group.strftime('Semaine %V (%Y)') 
#                 elif period == 'annuel':
#                     label = date_group.strftime('%Y')
#                 elif period == 'mensuel':
#                     label = date_group.strftime('%Y-%m')
#                 elif period in ['aujourdhui', 'journalier', 'autre']:
#                     label = date_group.strftime('%Y-%m-%d')
                
#                 data[label] = float(item['total'] or 0)
#         return data

#     # ----------------------------------------------------
#     # 3. Récupération des données pour les graphiques FINANCIERS (RapportVenteNocturne)
#     # ----------------------------------------------------
    
#     base_model = RapportVenteNocturne
#     date_field = 'start_time'
#     # Filtrer les rapports terminés
#     extra_filter_completed = {'end_time__isnull': False}

#     # CORRECTION : Utiliser les nouveaux noms de champs
#     data_ca = get_aggregated_data(base_model, date_field, 'chiffre_affaire', extra_filter=extra_filter_completed)
#     data_impayes = get_aggregated_data(base_model, date_field, 'montant_total_impayees', extra_filter=extra_filter_completed)
#     data_depenses = get_aggregated_data(base_model, date_field, 'montant_total_depenses', extra_filter=extra_filter_completed)
#     data_avances = get_aggregated_data(base_model, date_field, 'montant_total_avances', extra_filter=extra_filter_completed)
#     data_marge = get_aggregated_data(base_model, date_field, 'marge_totale', extra_filter=extra_filter_completed)
#     data_benefice = get_aggregated_data(base_model, date_field, 'benefice_net', extra_filter=extra_filter_completed)
        
#     all_labels = sorted(list(
#         set(data_ca.keys()) | set(data_impayes.keys()) | set(data_depenses.keys()) | 
#         set(data_avances.keys()) | set(data_marge.keys()) | set(data_benefice.keys())
#     ))

#     context['ca_labels'] = json.dumps(all_labels)
#     context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels]) 
#     context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
#     context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
#     context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])
#     context['marge_data'] = json.dumps([data_marge.get(d, 0) for d in all_labels])
#     context['benefice_data'] = json.dumps([data_benefice.get(d, 0) for d in all_labels])
    
#     # ----------------------------------------------------
#     # 4. PERFORMANCE DES PRODUITS (DetailVenteProduit)
#     # ----------------------------------------------------
    
#     # IDs des rapports terminés dans la période pour filtrer les autres modèles
#     rapport_ids = RapportVenteNocturne.objects.filter(
#         start_time__range=(start_dt, end_dt),
#         end_time__isnull=False
#     ).values_list('id', flat=True)

#     # CORRECTION : Vérifier s'il y a des rapports
#     if rapport_ids:
#         # Performance quantitative des produits - CORRECTION : utilisation de DetailVenteProduit
#         produits_quantite = DetailVenteProduit.objects.filter(
#             rapport_id__in=rapport_ids
#         ).values('produit__nom').annotate(
#             total_quantite=Sum('quantite_totale')
#         ).order_by('-total_quantite')[:10]  # Top 10

#         # Performance financière des produits (marge) - CORRECTION : utilisation de DetailVenteProduit
#         produits_marge = DetailVenteProduit.objects.filter(
#             rapport_id__in=rapport_ids
#         ).values('produit__nom').annotate(
#             total_marge=Sum('marge_totale_produit')
#         ).order_by('-total_marge')[:10]  # Top 10

#         context['produits_quantite_labels'] = json.dumps([p['produit__nom'] for p in produits_quantite])
#         context['produits_quantite_data'] = json.dumps([p['total_quantite'] or 0 for p in produits_quantite])
#         context['produits_marge_labels'] = json.dumps([p['produit__nom'] for p in produits_marge])
#         context['produits_marge_data'] = json.dumps([float(p['total_marge'] or 0) for p in produits_marge])
#     else:
#         # Données par défaut si aucun rapport trouvé
#         context['produits_quantite_labels'] = json.dumps([])
#         context['produits_quantite_data'] = json.dumps([])
#         context['produits_marge_labels'] = json.dumps([])
#         context['produits_marge_data'] = json.dumps([])

#     # ----------------------------------------------------
#     # 5. PERFORMANCE DU PERSONNEL (PerformancePersonnelNocturne)
#     # ----------------------------------------------------

#     # CORRECTION : Vérifier s'il y a des rapports
#     if rapport_ids:
#         # Performance quantitative du personnel - CORRECTION : utilisation du bon champ
#         personnel_quantite_qs = PerformancePersonnelNocturne.objects.filter(
#             rapport_id__in=rapport_ids
#         ).annotate(
#             personnel_nom=Concat(
#                 'personnel__prenom', 
#                 Value(' '),
#                 'personnel__nom',
#                 output_field=models.CharField()
#             )
#         ).values('personnel_nom').annotate(
#             total_quantite=Sum('quantite_totale_produits_vendus')  # CORRECTION : utilisation du bon champ
#         ).order_by('-total_quantite')[:10]  # Top 10

#         # Performance financière du personnel (marge)
#         personnel_marge_qs = PerformancePersonnelNocturne.objects.filter(
#             rapport_id__in=rapport_ids
#         ).annotate(
#             personnel_nom=Concat(
#                 'personnel__prenom', 
#                 Value(' '),
#                 'personnel__nom',
#                 output_field=models.CharField()
#             )
#         ).values('personnel_nom').annotate(
#             total_marge=Sum('montant_vendu_total')  # Approximation de la marge
#         ).order_by('-total_marge')[:10]  # Top 10

#         context['personnel_quantite_labels'] = json.dumps([p['personnel_nom'] for p in personnel_quantite_qs])
#         context['personnel_quantite_data'] = json.dumps([p['total_quantite'] or 0 for p in personnel_quantite_qs])
#         context['personnel_marge_labels'] = json.dumps([p['personnel_nom'] for p in personnel_marge_qs])
#         context['personnel_marge_data'] = json.dumps([float(p['total_marge'] or 0) for p in personnel_marge_qs])
#     else:
#         # Données par défaut si aucun rapport trouvé
#         context['personnel_quantite_labels'] = json.dumps([])
#         context['personnel_quantite_data'] = json.dumps([])
#         context['personnel_marge_labels'] = json.dumps([])
#         context['personnel_marge_data'] = json.dumps([])

#     # ----------------------------------------------------
#     # 6. TOP CLIENTS (Commande)
#     # ----------------------------------------------------
    
#     top_clients_qs = Commande.objects.filter(
#         numero_telephone__isnull=False, 
#         date_validation__range=(start_dt, end_dt),
#         statut__in=['payer', 'impayee']
#     ).values('numero_telephone', 'client_nom', 'client_prenom').annotate(
#         total_depense=Sum('montant_total', output_field=DecimalField())
#     ).order_by('-total_depense')[:10]
    
#     top_clients_labels = []
#     top_clients_data = []
    
#     for client in top_clients_qs:
#         # Construction du nom complet
#         full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
        
#         # Affichage (Nom complet + Téléphone)
#         client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
        
#         top_clients_labels.append(client_display)
#         top_clients_data.append(float(client['total_depense'] or 0))
        
#     context['top_clients_labels'] = json.dumps(top_clients_labels)
#     context['top_clients_data'] = json.dumps(top_clients_data)

#     return render(request, 'statistiques/dashboard.html', context)


from django.shortcuts import render
from django.db import models
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate, Concat
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
import json
from django.db.models import Q
from django.contrib import messages

# Import de vos modèles
from commandes.models import Commande, CommandeItem 
from avances.models import Avance
from depenses.models import Depense
from personnel.models import Personnel
from ventes.models import RapportVenteNocturne, DetailVenteProduit, PerformancePersonnelNocturne 
from produits.models import Produit 
# !!! NÉCESSAIRE : Assurez-vous d'avoir ces fonctions dans votre ventes/views.py !!!
from ventes.views import ( 
    calculer_ventes_detaillees_en_temps_reel,
    calculer_performance_personnel_en_temps_reel
)


# ----------------------------------------------------
# FONCTION UTILITAIRE : CALCULER CA/MARGE EN TEMPS RÉEL (CORRIGÉ)
# ----------------------------------------------------
def calculer_ca_marge_en_temps_reel(start_dt, end_dt):
    """Calcule le CA et la Marge à partir des Commandes et CommandesItem dans la période."""
    
    # Agrégation du Chiffre d'Affaires (CA)
    qs_commandes = Commande.objects.filter(
        date_validation__range=(start_dt, end_dt),
        statut__in=['payer', 'impayee'] # Inclure toutes les ventes validées
    ).aggregate(
        total_ca=Sum('montant_total', output_field=DecimalField()),
    )
    
    # Agrégation de la Marge (nécessite de passer par les CommandesItem)
    qs_items = CommandeItem.objects.filter(
        commande__date_validation__range=(start_dt, end_dt),
        commande__statut__in=['payer', 'impayee']
    ).aggregate(
        # CORRECTION ICI: Utiliser 'produit__prix_vente' pour le prix de vente unitaire
        total_marge=Sum(F('quantite') * (F('produit__prix_vente') - F('produit__prix_achat')), output_field=DecimalField())
    )
    
    # Conversion sécurisée en float
    ca = float(qs_commandes['total_ca'] or 0.0)
    marge = float(qs_items['total_marge'] or 0.0)
    
    return ca, marge


# ----------------------------------------------------
# FONCTION : DÉTERMINER LES BORNES TEMPORELLES 
# ----------------------------------------------------
def get_time_range_filter(period, current_year, current_month, current_date, start_date_param=None, end_date_param=None):
    """Calcule les bornes (datetime) pour la période donnée."""

    now = timezone.now()
    today = timezone.localdate()
    
    start_date = None
    end_date = None
    group_by_func = TruncDate
    
    if period == 'aujourdhui':
        start_date = datetime.combine(today, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())
        group_by_func = TruncDate
        
    elif period == 'journalier':
        try:
            date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
            start_date = datetime.combine(date_obj, datetime.min.time())
            end_date = datetime.combine(date_obj, datetime.max.time())
        except ValueError:
            start_date = datetime.combine(today, datetime.min.time())
            end_date = datetime.combine(today, datetime.max.time())
        group_by_func = TruncDate

    elif period == 'hebdomadaire':
        start_of_week = today - timedelta(days=today.weekday())
        start_date = datetime.combine(start_of_week, datetime.min.time())
        end_date = datetime.combine(start_of_week + timedelta(days=6), datetime.max.time())
        group_by_func = TruncWeek
        
    elif period == 'mensuel':
        start_date = datetime(today.year, today.month, 1)
        if today.month == 12:
            end_date = datetime(today.year + 1, 1, 1) - timedelta(microseconds=1)
        else:
            end_date = datetime(today.year, today.month + 1, 1) - timedelta(microseconds=1)
        group_by_func = TruncMonth
    
    elif period == 'trimestriel':
        q = (today.month - 1) // 3 + 1
        start_month = 3 * q - 2
        
        start_date = datetime(today.year, start_month, 1)
        
        next_month_start = start_month + 3
        if next_month_start > 12:
            end_date = datetime(today.year + 1, next_month_start % 12, 1) - timedelta(microseconds=1)
        else:
            end_date = datetime(today.year, next_month_start, 1) - timedelta(microseconds=1)
        group_by_func = TruncQuarter

    elif period == 'annuel':
        start_date = datetime(current_year, 1, 1)
        end_date = datetime(current_year, 12, 31, 23, 59, 59, 999999)
        group_by_func = TruncYear

    elif period == 'autre':
        try:
            start_date_obj = datetime.strptime(start_date_param, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date_param, '%Y-%m-%d')
            
            start_date = datetime.combine(start_date_obj.date(), datetime.min.time())
            end_date = datetime.combine(end_date_obj.date(), datetime.max.time())
            
        except:
            start_date = datetime.combine(today, datetime.min.time())
            end_date = datetime.combine(today, datetime.max.time())
        group_by_func = TruncDate 

    if start_date and not timezone.is_aware(start_date):
        start_date = timezone.make_aware(start_date)
    if end_date and not timezone.is_aware(end_date):
        end_date = timezone.make_aware(end_date)
    
    return {
        'start_dt': start_date, 
        'end_dt': end_date, 
        'group_by_func': group_by_func
    }

# ----------------------------------------------------
# FONCTION : STATISTIQUES DASHBOARD 
# ----------------------------------------------------
def statistiques_dashboard(request):
    
    today = timezone.localdate()
    
    # Récupération des paramètres avec VALEURS PAR DÉFAUT
    period = request.GET.get('period', 'aujourdhui')
    selected_date = request.GET.get('date', today.strftime('%Y-%m-%d'))
    start_date_param = request.GET.get('start_date', today.strftime('%Y-%m-%d'))
    end_date_param = request.GET.get('end_date', today.strftime('%Y-%m-%d'))

    
    # 1. Détermination de la période
    time_info = get_time_range_filter(
        period, 
        today.year, 
        today.month, 
        selected_date, 
        start_date_param, 
        end_date_param
    )
    start_dt = time_info['start_dt']
    end_dt = time_info['end_dt']
    group_by_func = time_info['group_by_func']
    
    # 2. Contexte pour les filtres (UI)
    all_years_qs = RapportVenteNocturne.objects.values_list('start_time__year', flat=True).distinct()
    available_years = sorted(list(set(all_years_qs)), reverse=True)
    
    context = {
        'period': period,
        'selected_date': selected_date,
        'start_date_param': start_date_param,
        'end_date_param': end_date_param,
        'available_years': available_years,
        'current_graph': request.GET.get('graph', 'financial'),
    }
    
    # ----------------------------------------------------
    # DÉTERMINATION DU MODE D'EXTRACTION (Temps Réel vs. Archivé)
    # ----------------------------------------------------

    rapports_filter = Q(rapport__start_time__range=(start_dt, end_dt)) | Q(rapport__end_time__range=(start_dt, end_dt))
    
    session_active = RapportVenteNocturne.objects.filter(is_active=True).first()

    is_time_range_current = end_dt >= timezone.now()
    is_real_time_mode = is_time_range_current and (session_active is not None)

    
    # ----------------------------------------------------
    # FONCTION D'AGRÉGATION FINANCIÈRE 
    # ----------------------------------------------------
    def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
        qs = model.objects.all()
        
        range_filter_key = f'{date_field}__range'
        
        if start_dt and end_dt:
            qs = qs.filter(**{range_filter_key: (start_dt, end_dt)}) 

        if extra_filter:
            qs = qs.filter(**extra_filter)

        data = defaultdict(lambda: 0)
        
        qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
            total=Sum(amount_field)
        ).order_by('date_group')
        
        # Logique de Formattage des Labels
        for item in qs:
            if item['date_group']:
                date_group = item['date_group']
                label = ""
                
                if isinstance(date_group, datetime):
                    date_group = date_group.date()
                
                if period == 'trimestriel':
                    q_num = (date_group.month - 1) // 3 + 1
                    label = f"T{q_num}/{date_group.year}"
                elif period == 'hebdomadaire':
                    label = date_group.strftime('Semaine %V (%Y)') 
                elif period == 'annuel':
                    label = date_group.strftime('%Y')
                elif period == 'mensuel':
                    label = date_group.strftime('%Y-%m')
                elif period in ['aujourdhui', 'journalier', 'autre']:
                    label = date_group.strftime('%Y-%m-%d')
                
                data[label] = float(item['total'] or 0)
        return data

    # ----------------------------------------------------
    # 3. Récupération des données pour les graphiques FINANCIERS (Injection du Temps Réel)
    # ----------------------------------------------------
    
    base_model = RapportVenteNocturne
    date_field = 'start_time'

    # 1. Calculer les données agrégées à partir des Rapports de Vente (y compris le rapport actif, qui a CA/Marge à 0.0)
    data_ca = get_aggregated_data(base_model, date_field, 'chiffre_affaire')
    data_marge = get_aggregated_data(base_model, date_field, 'marge_totale')
    
    # 2. Si mode Temps Réel : Calculer le CA/Marge réel et l'injecter pour le jour actif
    if is_real_time_mode and session_active:
        
        # Calculer le CA/Marge pour la date active à partir des Commandes
        ca_reel, marge_reelle = calculer_ca_marge_en_temps_reel(session_active.start_time, timezone.now())

        # Déterminer le label temporel pour le rapport actif
        rapport_start_date = session_active.start_time
        
        label = ""
        if isinstance(rapport_start_date, datetime):
            rapport_start_date = rapport_start_date.date()
        
        # Utilisation du même formattage de label que dans get_aggregated_data
        if period == 'trimestriel':
            q_num = (rapport_start_date.month - 1) // 3 + 1
            label = f"T{q_num}/{rapport_start_date.year}"
        elif period == 'hebdomadaire':
            label = rapport_start_date.strftime('Semaine %V (%Y)') 
        elif period == 'annuel':
            label = rapport_start_date.strftime('%Y')
        elif period == 'mensuel':
            label = rapport_start_date.strftime('%Y-%m')
        elif period in ['aujourdhui', 'journalier', 'autre']:
            label = rapport_start_date.strftime('%Y-%m-%d')

        # Écraser (ou ajouter) les données temps réel au dictionnaire agrégé
        data_ca[label] = ca_reel
        data_marge[label] = marge_reelle
    
    # 3. Récupération des autres données financières (non modifiées)
    data_impayes = get_aggregated_data(base_model, date_field, 'montant_total_impayees')
    data_depenses = get_aggregated_data(base_model, date_field, 'montant_total_depenses')
    data_avances = get_aggregated_data(base_model, date_field, 'montant_total_avances')
    data_benefice = get_aggregated_data(base_model, date_field, 'benefice_net')
        
    all_labels = sorted(list(
        set(data_ca.keys()) | set(data_impayes.keys()) | set(data_depenses.keys()) | 
        set(data_avances.keys()) | set(data_marge.keys()) | set(data_benefice.keys())
    ))

    context['ca_labels'] = json.dumps(all_labels)
    context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels]) 
    context['impayes_data'] = json.dumps([data_impayes.get(d, 0) for d in all_labels])
    context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
    context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])
    context['marge_data'] = json.dumps([data_marge.get(d, 0) for d in all_labels])
    context['benefice_data'] = json.dumps([data_benefice.get(d, 0) for d in all_labels])
    
    # ----------------------------------------------------
    # 4. PERFORMANCE DES PRODUITS (DetailVenteProduit / CommandeItem)
    # ----------------------------------------------------
    if is_real_time_mode:
        # --- Mode TEMPS RÉEL ---
        real_time_data = calculer_ventes_detaillees_en_temps_reel(start_dt, end_dt)
        
        quantite_map = defaultdict(float)
        marge_map = defaultdict(float)
        
        for item in real_time_data:
            nom = item['produit'].nom if hasattr(item['produit'], 'nom') else f"Produit ID {item['produit'].id}"
            quantite_map[nom] += float(item['quantite_totale'] or 0.0)
            marge_map[nom] += float(item['marge_totale_produit'] or 0.0)

        produits_quantite_list = sorted(quantite_map.items(), key=lambda item: item[1], reverse=True)[:10]
        produits_marge_list = sorted(marge_map.items(), key=lambda item: item[1], reverse=True)[:10]

        context['produits_quantite_labels'] = json.dumps([nom for nom, val in produits_quantite_list])
        context['produits_quantite_data'] = json.dumps([val for nom, val in produits_quantite_list])
        context['produits_marge_labels'] = json.dumps([nom for nom, val in produits_marge_list])
        context['produits_marge_data'] = json.dumps([val for nom, val in produits_marge_list])

    else:
        # --- Mode ARCHIVÉ ---
        produits_quantite = DetailVenteProduit.objects.filter(
            rapports_filter,
            rapport__end_time__isnull=False 
        ).values('produit__id', 'produit__nom').annotate(
            total_quantite=Sum('quantite_totale') 
        ).order_by('-total_quantite')[:10]

        produits_marge = DetailVenteProduit.objects.filter(
            rapports_filter,
            rapport__end_time__isnull=False
        ).values('produit__id', 'produit__nom').annotate(
            total_marge=Sum('marge_totale_produit') 
        ).order_by('-total_marge')[:10]

        context['produits_quantite_labels'] = json.dumps([p['produit__nom'] for p in produits_quantite])
        context['produits_quantite_data'] = json.dumps([float(p['total_quantite'] or 0.0) for p in produits_quantite])
        context['produits_marge_labels'] = json.dumps([p['produit__nom'] for p in produits_marge])
        context['produits_marge_data'] = json.dumps([float(p['total_marge'] or 0.0) for p in produits_marge])

    # ----------------------------------------------------
    # 5. PERFORMANCE DU PERSONNEL (PerformancePersonnelNocturne / Temps Réel)
    # ----------------------------------------------------
    if is_real_time_mode:
        # --- Mode TEMPS RÉEL ---
        personnel_performance_list = calculer_performance_personnel_en_temps_reel(start_dt, end_dt)

        personnel_quantite_list = sorted(
            personnel_performance_list, 
            key=lambda x: x['quantite_totale_produits_vendus'], 
            reverse=True
        )[:10]
        personnel_marge_list = sorted(
            personnel_performance_list, 
            key=lambda x: x['montant_vendu_total'], 
            reverse=True
        )[:10]

        context['personnel_quantite_labels'] = json.dumps([p['nom_complet'] for p in personnel_quantite_list])
        context['personnel_quantite_data'] = json.dumps([float(p['quantite_totale_produits_vendus'] or 0.0) for p in personnel_quantite_list])
        context['personnel_marge_labels'] = json.dumps([p['nom_complet'] for p in personnel_marge_list])
        context['personnel_marge_data'] = json.dumps([float(p['montant_vendu_total'] or 0.0) for p in personnel_marge_list])

    else:
        # --- Mode ARCHIVÉ ---
        personnel_quantite_qs = PerformancePersonnelNocturne.objects.filter(
            rapports_filter,
            rapport__end_time__isnull=False
        ).annotate(
            personnel_nom=Concat(
                'personnel__prenom', 
                Value(' '),
                'personnel__nom',
                output_field=models.CharField()
            )
        ).values('personnel_nom').annotate(
            total_quantite=Sum(F('quantite_totale_produits_vendus')) 
        ).order_by('-total_quantite')[:10]

        personnel_marge_qs = PerformancePersonnelNocturne.objects.filter(
            rapports_filter,
            rapport__end_time__isnull=False
        ).annotate(
            personnel_nom=Concat(
                'personnel__prenom', 
                Value(' '),
                'personnel__nom',
                output_field=models.CharField()
            )
        ).values('personnel_nom').annotate(
            total_marge=Sum(F('montant_vendu_total')) 
        ).order_by('-total_marge')[:10]

        context['personnel_quantite_labels'] = json.dumps([p['personnel_nom'] for p in personnel_quantite_qs])
        context['personnel_quantite_data'] = json.dumps([float(p['total_quantite'] or 0.0) for p in personnel_quantite_qs])
        context['personnel_marge_labels'] = json.dumps([p['personnel_nom'] for p in personnel_marge_qs])
        context['personnel_marge_data'] = json.dumps([float(p['total_marge'] or 0.0) for p in personnel_marge_qs])

    # ----------------------------------------------------
    # 6. TOP CLIENTS (Commande - Reste inchangée car déjà temps réel)
    # ----------------------------------------------------
    
    top_clients_qs = Commande.objects.filter(
        numero_telephone__isnull=False, 
        date_validation__range=(start_dt, end_dt),
        statut__in=['payer', 'impayee']
    ).values('numero_telephone', 'client_nom', 'client_prenom').annotate(
        total_depense=Sum('montant_total', output_field=DecimalField())
    ).order_by('-total_depense')[:10]
    
    top_clients_labels = []
    top_clients_data = []
    
    for client in top_clients_qs:
        full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
        client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
        
        top_clients_labels.append(client_display)
        top_clients_data.append(float(client['total_depense'] or 0.0))
        
    context['top_clients_labels'] = json.dumps(top_clients_labels)
    context['top_clients_data'] = json.dumps(top_clients_data)

    # =========================================================================
    # MESSAGES DE DÉBOGAGE FINAL
    # =========================================================================
    
    messages.info(request, 
        f"MODE : {'TEMPS RÉEL (Session Active)' if is_real_time_mode else 'ARCHIVÉ (Rapports Clos)'} | Période filtrée : {start_dt.strftime('%d/%m %H:%M')} à {end_dt.strftime('%d/%m %H:%M')}"
    )
    
    messages.info(request, 
        f"💰 DEBUG CA/MARGE : Labels: {context.get('ca_labels')} | CA: {context.get('ca_data')} | Marge: {context.get('marge_data')}"
    )

    messages.info(request, 
        f"📊 DEBUG PRODUITS (Qté) : Labels: {context.get('produits_quantite_labels')} | Données: {context.get('produits_quantite_data')}"
    )
    messages.info(request, 
        f"📊 DEBUG PRODUITS (Marge) : Labels: {context.get('produits_marge_labels')} | Données: {context.get('produits_marge_data')}"
    )
    
    messages.info(request, 
        f"👤 DEBUG PERSONNEL (Qté) : Labels: {context.get('personnel_quantite_labels')} | Données: {context.get('personnel_quantite_data')}"
    )
    messages.info(request, 
        f"👤 DEBUG PERSONNEL (Marge) : Labels: {context.get('personnel_marge_labels')} | Données: {context.get('personnel_marge_data')}"
    )
    
    messages.info(request, 
        f"💰 DEBUG CLIENTS : Labels: {context.get('top_clients_labels')} | Données: {context.get('top_clients_data')}"
    )
    
    return render(request, 'statistiques/dashboard.html', context)