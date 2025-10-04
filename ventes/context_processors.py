# ventes/context_processors.py

from .models import RapportVenteNocturne

def session_status(request):
    """
    Ajoute l'état de la session de vente nocturne à toutes les requêtes.
    """
    session_active = RapportVenteNocturne.objects.filter(is_active=True).first()
    return {
        'IS_SESSION_ACTIVE': session_active is not None,
        'CURRENT_VENTE_SESSION': session_active,
    }