from django.urls import path
from . import views

app_name = 'ventes'

urlpatterns = [
   
     # Point des Ventes
    path('', views.point_des_ventes, name='point_des_ventes'),

    # 2. URL pour la nouvelle vue de gestion de session (CETTE LIGNE EST LA SOLUTION)
    path('toggle-session/', views.toggle_session, name='toggle_session'), 
]
