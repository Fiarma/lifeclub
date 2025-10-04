# ventes/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from .models import RapportVenteNocturne # Assurez-vous d'importer le modèle correct

def session_required(view_func):
    """
    Décorateur qui vérifie si une session RapportVenteNocturne est active.
    Redirige vers la page des ventes avec un message d'erreur si aucune session n'est active.
    """
    def wrapper(request, *args, **kwargs):
        # Cherche une session active
        session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
        
        if not session_active:
            # Si aucune session n'est active, affiche un message et redirige.
            messages.error(request, "Impossible d'effectuer cette action. Veuillez d'abord OUVRIR LA BOÎTE (Session de Vente).")
            # Redirige vers le point de vente principal
            return redirect('ventes:point_des_ventes') 
            
        # Si la session est active, exécute la vue originale
        return view_func(request, *args, **kwargs)

    return wrapper