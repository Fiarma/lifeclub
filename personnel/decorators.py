from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles=None):
    """
    Décorateur pour restreindre l'accès en fonction du rôle.
    Permet un accès complet à tout Superutilisateur (Boss/Propriétaire).
    """
    if allowed_roles is None:
        allowed_roles = []
        
    def decorator(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('users:login') 
            
            # 🌟 Le Superuser (Boss) a accès à TOUT sans vérification de rôle.
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            # Reste de la vérification pour le personnel régulier
            if hasattr(request.user, 'personnel_profile'):
                user_role = request.user.personnel_profile.role
                
                if user_role in allowed_roles:
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden("<h1>Accès refusé.</h1><p>Votre rôle ne vous permet pas d'accéder à cette ressource.</p>")
            
            # Utilisateur connecté sans profil Personnel
            return HttpResponseForbidden("<h1>Accès refusé.</h1><p>Compte utilisateur non lié à un profil personnel valide.</p>") 
            
        return wrapper_func
    return decorator