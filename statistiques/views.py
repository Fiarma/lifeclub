from django.shortcuts import render
from django.db import models
from django.db.models import Sum, F, DecimalField
from django.utils import timezone
from datetime import timedelta, datetime
from collections import defaultdict
import calendar
import json 

# Import des fonctions d'agrégation spécifiques
from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate 

# ----------------------------------------------------
# Import de vos modèles
# ----------------------------------------------------
from commandes.models import Commande, CommandeItem, Boisson 
from avances.models import Avance 
from depenses.models import Depense 
from personnel.models import Personnel

def statistiques_dashboard(request):
    period = request.GET.get('period', 'mensuel')
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    selected_date = request.GET.get('date')

    today = timezone.localdate()

    # 1. Préparation de l'année et des filtres de temps
    
    all_years_qs = Commande.objects.filter(date_validation__isnull=False).values_list('date_validation__year', flat=True).distinct()
    available_years = sorted(list(set(all_years_qs)), reverse=True)
    
    if not selected_year and available_years:
        current_year = available_years[0]
    else:
        current_year = int(selected_year) if selected_year and selected_year.isdigit() else today.year
    
    current_month = int(selected_month) if selected_month and selected_month.isdigit() else today.month
    current_date = selected_date if selected_date else today.strftime('%Y-%m-%d')
    
    group_by_func = TruncDate
    date_format = '%Y-%m-%d'
    base_filter = {}
    
    if period == 'annuel':
        group_by_func = TruncYear
        date_format = '%Y'
        
    elif period == 'trimestriel':
        group_by_func = TruncQuarter
        base_filter = {'__year': current_year}
        
    elif period == 'mensuel':
        group_by_func = TruncMonth
        base_filter = {'__year': current_year}

    elif period == 'hebdomadaire':
        group_by_func = TruncWeek
        base_filter = {'__year': current_year, '__month': current_month}
        
    elif period == 'journalier':
        group_by_func = TruncDate
        try:
            date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
            base_filter = {'__date': date_obj}
        except ValueError:
            pass 

    context = {
        'period': period,
        'available_years': available_years,
        'selected_year': current_year,
        'selected_month': current_month,
        'selected_date': current_date,
        'months': [ (i, calendar.month_name[i]) for i in range(1, 13) ],
    }
    
    
    # ----------------------------------------------------
    # FONCTION D'AGRÉGATION (CA / DÉPENSES / AVANCES)
    # ----------------------------------------------------
    def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
        qs = model.objects.all()
        
        filter_dict = {}
        for k, v in base_filter.items():
            filter_dict[f'{date_field}{k}'] = v

        if extra_filter:
            qs = qs.filter(**extra_filter)

        qs = qs.filter(**filter_dict)

        data = defaultdict(lambda: 0)
        
        qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
            total=Sum(amount_field)
        ).order_by('date_group')
        
        for item in qs:
            if item['date_group']:
                # Formattage du label de l'axe X selon la période
                if period == 'trimestriel':
                    q_num = (item['date_group'].month - 1) // 3 + 1
                    label = f"T{q_num}/{item['date_group'].year}"
                elif period == 'hebdomadaire':
                    # Utilise ISO week number pour la compatibilité (Semaine %V)
                    label = item['date_group'].strftime('Semaine %V (%Y)') 
                elif period == 'annuel':
                    label = item['date_group'].strftime('%Y')
                elif period == 'mensuel':
                    label = item['date_group'].strftime('%Y-%m')
                else: # Journalier
                    label = item['date_group'].strftime('%Y-%m-%d')

                data[label] = float(item['total'] or 0)
        return data


    # ----------------------------------------------------
    # 1. ÉVOLUTION DES FLUX FINANCIERS
    # ----------------------------------------------------

    data_ca = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'payer'})
    data_depenses = get_aggregated_data(Depense, 'date', 'montant')
    data_avances = get_aggregated_data(Avance, 'date_avance', 'montant')
        
    all_labels = sorted(list(set(data_ca.keys()) | set(data_depenses.keys()) | set(data_avances.keys())))

    # CORRECTION : Utiliser la même structure que l'ancien code qui fonctionnait
    context['ca_labels'] = json.dumps(all_labels)
    context['ca_data'] = json.dumps([data_ca.get(d, 0) for d in all_labels])
    context['depenses_data'] = json.dumps([data_depenses.get(d, 0) for d in all_labels])
    context['avances_data'] = json.dumps([data_avances.get(d, 0) for d in all_labels])

    
    # ----------------------------------------------------
    # 2. 3. 4. 5. AUTRES GRAPHIQUES (Ventes, Clients, Personnel)
    # ----------------------------------------------------

    commande_filter = {'statut': 'payer'}
    for k, v in base_filter.items():
        commande_filter[f'date_validation{k}'] = v
        
    items_qs = CommandeItem.objects.filter(
        **{f'commande__{k}': v for k, v in commande_filter.items()} 
    ).select_related('boisson', 'commande__personnel__user')

    # 2. Quantité totale de boissons
    boissons_quantite = items_qs.values('boisson__nom').annotate(total_quantite=Sum('quantite')).order_by('-total_quantite')
    context['boissons_labels'] = json.dumps([b['boisson__nom'] for b in boissons_quantite])
    context['boissons_data'] = json.dumps([b['total_quantite'] or 0 for b in boissons_quantite])

    # 3. & 4. Ventes par personnel (par boisson et total)
    personnel_sales_data = defaultdict(lambda: defaultdict(lambda: 0))
    personnel_total_sales = defaultdict(lambda: 0)
    
    for item in items_qs:
        personnel_profile = item.commande.personnel
        personnel_name = personnel_profile.nom_complet if personnel_profile else f"Personnel Inconnu {item.commande.personnel_id}"
        boisson_name = item.boisson.nom
        personnel_sales_data[personnel_name][boisson_name] += item.quantite
        personnel_total_sales[personnel_name] += item.quantite

    all_boissons = sorted(list(set(item.boisson.nom for item in items_qs)))
    personnel_names = sorted(list(personnel_sales_data.keys()))
    
    context['personnel_boisson_labels'] = json.dumps(all_boissons)
    personnel_boisson_datasets = []
    for name in personnel_names:
        # Utilisation de .get(b_name, 0) pour garantir des zéros
        data_set = {'label': name, 'data': [personnel_sales_data[name].get(b_name, 0) for b_name in all_boissons]}
        personnel_boisson_datasets.append(data_set)
    context['personnel_boisson_datasets'] = json.dumps(personnel_boisson_datasets)

    personnel_total_sorted = sorted(personnel_total_sales.items(), key=lambda item: item[1], reverse=True)
    context['personnel_total_labels'] = json.dumps([item[0] for item in personnel_total_sorted])
    context['personnel_total_data'] = json.dumps([item[1] for item in personnel_total_sorted])

    # 5. Top Clients
    top_clients_qs = Commande.objects.filter(numero_telephone__isnull=False, **commande_filter)
    top_clients_qs = top_clients_qs.values('numero_telephone', 'client_nom', 'client_prenom').annotate(
        total_depense=Sum('montant_total', output_field=DecimalField())
    ).order_by('-total_depense')[:10]
    
    top_clients_labels = []
    top_clients_data = []
    
    for client in top_clients_qs:
        full_name = f"{client.get('client_prenom', '') or ''} {client.get('client_nom', '') or ''}".strip()
        client_display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
        top_clients_labels.append(client_display)
        top_clients_data.append(float(client['total_depense'] or 0))
        
    context['top_clients_labels'] = json.dumps(top_clients_labels)
    context['top_clients_data'] = json.dumps(top_clients_data)

    return render(request, 'statistiques/dashboard.html', context)

# from django.shortcuts import render
# from django.db.models import Sum, DecimalField
# from collections import defaultdict
# from django.db.models.functions import TruncYear, TruncQuarter, TruncMonth, TruncWeek, TruncDate
# from commandes.models import Commande, CommandeItem, Boisson
# from depenses.models import Depense
# from avances.models import Avance
# from personnel.models import Personnel
# from django.utils import timezone
# from datetime import datetime
# import calendar
# import plotly.graph_objs as go
# from plotly.offline import plot

# def statistiques_dashboard(request):
#     period = request.GET.get('period', 'mensuel')
#     selected_year = request.GET.get('year')
#     selected_month = request.GET.get('month')
#     selected_date = request.GET.get('date')
    
#     today = timezone.localdate()
#     all_years_qs = Commande.objects.filter(date_validation__isnull=False).values_list('date_validation__year', flat=True).distinct()
#     available_years = sorted(list(set(all_years_qs)), reverse=True)

#     current_year = int(selected_year) if selected_year else (available_years[0] if available_years else today.year)
#     current_month = int(selected_month) if selected_month else today.month
#     current_date = selected_date if selected_date else today.strftime('%Y-%m-%d')

#     # Définition de la fonction d'agrégation selon la période
#     group_by_func = TruncDate
#     date_format = '%Y-%m-%d'
#     base_filter = {}

#     if period == 'annuel':
#         group_by_func = TruncYear
#         date_format = '%Y'
#     elif period == 'trimestriel':
#         group_by_func = TruncQuarter
#         date_format = 'T%q/%Y'
#         base_filter = {'__year': current_year}
#     elif period == 'mensuel':
#         group_by_func = TruncMonth
#         date_format = '%Y-%m'
#         base_filter = {'__year': current_year}
#     elif period == 'hebdomadaire':
#         group_by_func = TruncWeek
#         date_format = 'Semaine %W'
#         base_filter = {'__year': current_year, '__month': current_month}
#     elif period == 'journalier':
#         group_by_func = TruncDate
#         try:
#             date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
#             base_filter = {'__date': date_obj}
#         except ValueError:
#             pass

#     # Fonction pour récupérer les données agrégées
#     def get_aggregated_data(model, date_field, amount_field, extra_filter={}):
#         qs = model.objects.all()
#         filter_dict = {f'{date_field}{k}': v for k, v in base_filter.items()}
#         if extra_filter:
#             qs = qs.filter(**extra_filter)
#         qs = qs.filter(**filter_dict)
#         data = defaultdict(lambda: 0)
#         qs = qs.annotate(date_group=group_by_func(date_field)).values('date_group').annotate(
#             total=Sum(amount_field)
#         ).order_by('date_group')
#         for item in qs:
#             if item['date_group']:
#                 if period == 'trimestriel':
#                     q_num = (item['date_group'].month - 1) // 3 + 1
#                     label = f"T{q_num}/{item['date_group'].year}"
#                 elif period == 'hebdomadaire':
#                     label = item['date_group'].strftime('Semaine %W')
#                 else:
#                     label = item['date_group'].strftime(date_format)
#                 data[label] = float(item['total'])
#         return data

#     # Récupération des données
#     data_ca = get_aggregated_data(Commande, 'date_validation', 'montant_total', extra_filter={'statut': 'payer'})
#     data_depenses = get_aggregated_data(Depense, 'date', 'montant')
#     data_avances = get_aggregated_data(Avance, 'date_avance', 'montant')
#     all_labels = sorted(list(set(data_ca.keys()) | set(data_depenses.keys()) | set(data_avances.keys())))

#     # --- Graphique CA / Dépenses / Avances ---
#     ca_fig = go.Figure()
#     ca_fig.add_trace(go.Scatter(x=all_labels, y=[data_ca.get(d, 0) for d in all_labels], mode='lines+markers', name='Chiffre d\'Affaires', line=dict(color='#007bff')))
#     ca_fig.add_trace(go.Scatter(x=all_labels, y=[data_depenses.get(d, 0) for d in all_labels], mode='lines+markers', name='Dépenses', line=dict(color='#dc3545')))
#     ca_fig.add_trace(go.Scatter(x=all_labels, y=[data_avances.get(d, 0) for d in all_labels], mode='lines+markers', name='Avances', line=dict(color='#ffc107')))
#     ca_fig.update_layout(title="Évolution CA / Dépenses / Avances", xaxis_title="Période", yaxis_title="Montant (F)")

#     ca_div = plot(ca_fig, output_type='div', include_plotlyjs=False)

#     # --- Graphique Quantité de Boissons ---
#     items_qs = CommandeItem.objects.filter(commande__statut='payer').select_related('boisson')
#     boissons_data = items_qs.values('boisson__nom').annotate(total_quantite=Sum('quantite')).order_by('-total_quantite')
#     boissons_labels = [b['boisson__nom'] for b in boissons_data]
#     boissons_values = [b['total_quantite'] for b in boissons_data]

#     boissons_fig = go.Figure([go.Bar(x=boissons_labels, y=boissons_values, marker_color='orange')])
#     boissons_fig.update_layout(title="Quantité de Boissons Vendues", yaxis_title="Quantité")
#     boissons_div = plot(boissons_fig, output_type='div', include_plotlyjs=False)

#     # --- Graphique Ventes par Personnel et Boisson ---
#     personnel_sales = defaultdict(lambda: defaultdict(int))
#     personnel_total = defaultdict(int)
#     for item in items_qs:
#         personnel_name = item.commande.personnel.nom_complet if item.commande.personnel else f"ID {item.commande.personnel_id}"
#         boisson_name = item.boisson.nom
#         personnel_sales[personnel_name][boisson_name] += item.quantite
#         personnel_total[personnel_name] += item.quantite
#     all_boissons = sorted(set(b.nom for b in Boisson.objects.all()))
#     personnel_names = sorted(personnel_sales.keys())

#     personnel_boisson_fig = go.Figure()
#     for person in personnel_names:
#         personnel_boisson_fig.add_trace(go.Bar(
#             x=all_boissons,
#             y=[personnel_sales[person].get(b, 0) for b in all_boissons],
#             name=person
#         ))
#     personnel_boisson_fig.update_layout(title="Ventes par Personnel et Boisson", barmode='stack', yaxis_title="Quantité")
#     personnel_boisson_div = plot(personnel_boisson_fig, output_type='div', include_plotlyjs=False)

#     # --- Graphique Quantité Totale par Personnel ---
#     personnel_total_fig = go.Figure([go.Bar(y=list(personnel_total.keys()), x=list(personnel_total.values()), orientation='h', marker_color='green')])
#     personnel_total_fig.update_layout(title="Quantité Totale par Personnel", xaxis_title="Quantité")
#     personnel_total_div = plot(personnel_total_fig, output_type='div', include_plotlyjs=False)

#     # --- Top Clients ---
#     top_clients_qs = Commande.objects.filter(numero_telephone__isnull=False, statut='payer').values('numero_telephone', 'client_nom', 'client_prenom').annotate(
#         total_depense=Sum('montant_total', output_field=DecimalField())
#     ).order_by('-total_depense')[:10]

#     top_clients_labels = []
#     top_clients_values = []
#     for client in top_clients_qs:
#         full_name = f"{client['client_prenom'] or ''} {client['client_nom'] or ''}".strip()
#         display = f"{full_name} ({client['numero_telephone']})" if full_name else client['numero_telephone']
#         top_clients_labels.append(display)
#         top_clients_values.append(float(client['total_depense']))

#     top_clients_fig = go.Figure([go.Pie(labels=top_clients_labels, values=top_clients_values)])
#     top_clients_fig.update_layout(title="Top 10 Clients")
#     top_clients_div = plot(top_clients_fig, output_type='div', include_plotlyjs=False)

#     context = {
#         'ca_div': ca_div,
#         'boissons_div': boissons_div,
#         'personnel_boisson_div': personnel_boisson_div,
#         'personnel_total_div': personnel_total_div,
#         'top_clients_div': top_clients_div,
#         'period': period,
#         'available_years': available_years,
#         'selected_year': current_year,
#         'selected_month': current_month,
#         'selected_date': current_date,
#         'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
#     }

#     return render(request, 'statistiques/dashboard.html', context)
