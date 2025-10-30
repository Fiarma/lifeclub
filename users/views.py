from django.shortcuts import render

# Create your views here.
# users/views.py

from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import (
    PasswordResetConfirmView, 
    PasswordResetCompleteView,
    LoginView, 
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView
)
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# --- Configuration des URLs ---
LOGIN_URL = reverse_lazy('users:login') 
HOME_URL = reverse_lazy('personnel:home_employe')

# --- Modèles ---
User = get_user_model()

# ----------------------------------------------------------------------
# 1. VUES PERSONNALISÉES POUR L'ACTIVATION (Déblocage du Compte)
# ----------------------------------------------------------------------

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """
    Vue sur laquelle l'utilisateur définit son nouveau mot de passe (suite au lien email).
    Elle gère le déblocage du compte (retire le drapeau de sécurité) et l'envoi de l'e-mail final de connexion.
    """
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')

    def form_valid(self, form):
        # 1. Exécute la logique normale : change le mot de passe, invalide le jeton
        response = super().form_valid(form)
        
        # L'objet User est accessible après la validation du formulaire de confirmation
        user = form.user 
        
        # 2. LOGIQUE PERSONNALISÉE : Déblocage et envoi de l'e-mail final
        try:
            profile = user.personnel_profile
            
            # RETIRER LE DRAPEAU DE SÉCURITÉ (DÉBLOCAGE)
            if profile.change_password_required:
                profile.change_password_required = False
                profile.save()
            
            # ENVOI DE L'EMAIL DE CONFIRMATION ET DE CONNEXION
            context = {
                'user': user,
                'login_url': self.request.build_absolute_uri(LOGIN_URL),
                'site_name': 'LifeClub',
            }
            
            html_message = render_to_string('users/activation_complete_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                'Votre mot de passe a été défini - Connexion au LifeClub',
                plain_message,
                None, # Utilise settings.DEFAULT_FROM_EMAIL
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
        except Exception as e:
            # En cas d'échec de l'envoi de l'e-mail (vérifiez la config SMTP)
            messages.warning(self.request, "Mot de passe défini, mais erreur lors de l'envoi de l'e-mail de confirmation. Vous pouvez vous connecter.")
            
        return response 


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """
    Vue de fin de réinitialisation. Redirige immédiatement l'utilisateur vers la page de connexion.
    """
    template_name = 'users/password_reset_complete.html' 
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Mot de passe défini avec succès. Veuillez vous connecter.")
        return redirect(LOGIN_URL) 

# ----------------------------------------------------------------------
# 2. VUES STANDARD (Pour l'URL de votre users/urls.py)
# ----------------------------------------------------------------------
# Nous les redéfinissons ici pour pouvoir les utiliser dans users/urls.py
# avec le préfixe 'views.' si vous le souhaitez, mais l'héritage n'est pas nécessaire.

class CustomLoginView(LoginView):
    """Vue de connexion standard."""
    template_name = 'users/login.html'
    
class CustomLogoutView(LogoutView):
    """Vue de déconnexion standard."""
    next_page = reverse_lazy('users:login')

class CustomPasswordChangeView(PasswordChangeView):
    """Vue de changement de mot de passe (si déjà connecté)."""
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    """Vue de confirmation du changement de mot de passe."""
    template_name = 'users/password_change_done.html'

class CustomPasswordResetView(PasswordResetView):
    """Vue d'envoi du lien de réinitialisation."""
    template_name = 'users/password_reset_form.html'
    email_template_name='users/password_reset_email.html'
    subject_template_name='users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Vue de confirmation de l'envoi du lien."""
    template_name = 'users/password_reset_done.html'

# FIN du fichier views.py