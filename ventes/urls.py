from django.urls import path
from . import views

app_name = 'ventes'

urlpatterns = [
   
     # Point des Ventes
    path('', views.point_des_ventes, name='point_des_ventes'),
]
