# from django.shortcuts import render

# # Create your views here.
# from django.shortcuts import render, redirect, get_object_or_404
# from .models import Personnel
# from .forms import PersonnelForm

# # Liste du personnel
# def liste_personnel(request):
#     personnels = Personnel.objects.all()
#     return render(request, "personnel/liste_personnel.html", {"personnels": personnels})

# # Ajouter un employé
# def add_personnel(request):
#     if request.method == "POST":
#         form = PersonnelForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect("personnel:liste_personnel")
#     else:
#         form = PersonnelForm()
#     return render(request, "personnel/add_personnel.html", {"form": form})

# # Modifier un employé
# def edit_personnel(request, personnel_id):
#     personnel = get_object_or_404(Personnel, pk=personnel_id)
#     if request.method == "POST":
#         form = PersonnelForm(request.POST, instance=personnel)
#         if form.is_valid():
#             form.save()
#             return redirect("personnel:liste_personnel")
#     else:
#         form = PersonnelForm(instance=personnel)
#     return render(request, "personnel/edit_personnel.html", {"form": form})

# # Supprimer un employé
# def delete_personnel(request, personnel_id):
#     personnel = get_object_or_404(Personnel, pk=personnel_id)
#     if request.method == "POST":
#         personnel.delete()
#         return redirect("personnel:liste_personnel")
#     return render(request, "personnel/delete_personnel.html", {"personnel": personnel})


################## 10 -10- 2025 ################

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Personnel
from .forms import PersonnelCreationForm, PersonnelEditForm 
from .decorators import role_required 
from django.contrib.auth.forms import PasswordResetForm # <--- C'ÉTAIT L'IMPORT MANQUANT

@login_required
@role_required(allowed_roles=['boss', 'manager', 'secretaire'])
def liste_personnel(request):
    """Liste complète du personnel (Boss/Manager/Secrétaire y ont accès)."""
    personnels = Personnel.objects.select_related('user').all().order_by('role', 'nom')
    return render(request, "personnel/liste_personnel.html", {"personnels": personnels})

# ----------------------------------------------------------------------
# 1. Vue d'Accueil (LOGIQUE DE REDIRECTION FORCÉE)
# ----------------------------------------------------------------------
@login_required
def home_employe(request):
    """Affiche le tableau de bord et force le changement de mot de passe si le drapeau est actif."""
    
    is_superuser = request.user.is_superuser
    personnel_profile = None

    try:
        personnel_profile = request.user.personnel_profile
        
        if not is_superuser and personnel_profile.change_password_required:
            messages.info(request, "Veuillez définir votre mot de passe personnel pour des raisons de sécurité.")
            return redirect('users:password_change') 
            
    except Personnel.DoesNotExist:
        if not is_superuser:
            messages.error(request, "Votre compte n'est pas lié à un profil personnel.")
            return redirect('users:logout') 
        
    return render(request, "personnel/home_employe.html", {
        'profile': personnel_profile, 
        'is_superuser': is_superuser
    })


# ----------------------------------------------------------------------
# 2. Vue de Création du Personnel (LOGIQUE D'ENVOI D'E-MAIL)
# ----------------------------------------------------------------------

@login_required
@role_required(allowed_roles=['boss']) 
def creer_personnel(request): 
    """Ajout d'un employé et envoi de l'e-mail d'activation/changement de mot de passe."""
    if request.method == "POST":
        form = PersonnelCreationForm(request.POST) 
        if form.is_valid():
            personnel_obj = form.save()
            
            # Envoi de l'e-mail d'intégration
            user_email = personnel_obj.user.email
            
            # Utilise le PasswordResetForm, maintenant correctement importé
            reset_form = PasswordResetForm({'email': user_email})
            if reset_form.is_valid():
                reset_form.save(
                    request=request, 
                    use_https=request.is_secure(),
                    email_template_name='users/creation_initial_email.html',   
                    subject_template_name='users/creation_initial_subject.txt', 
                )
                messages.success(request, f"L'employé {personnel_obj.nom_complet} (ID: {personnel_obj.pk}) a été créé. Un e-mail d'activation a été envoyé à {user_email}.")
            else:
                 messages.error(request, f"L'employé {personnel_obj.nom_complet} a été créé, mais l'envoi de l'e-mail a échoué. Vérifiez l'adresse e-mail ({user_email}) ou la configuration SMTP.")
                 
            return redirect("personnel:liste_personnel")
    else:
        form = PersonnelCreationForm()
        
    return render(request, "personnel/add_personnel.html", {"form": form})

@login_required
@role_required(allowed_roles=['boss', 'manager'])
def edit_personnel(request, personnel_id):
    """Modification du profil (Boss/Manager y ont accès)."""
    personnel = get_object_or_404(Personnel, pk=personnel_id)
    if request.method == "POST":
        form = PersonnelEditForm(request.POST, instance=personnel) 
        if form.is_valid():
            form.save()
            messages.success(request, f"Le profil de {personnel.nom_complet} a été mis à jour.")
            return redirect("personnel:liste_personnel")
    else:
        form = PersonnelEditForm(instance=personnel)
        
    return render(request, "personnel/edit_personnel.html", {"form": form, "personnel": personnel})

@login_required
@role_required(allowed_roles=['boss'])
def delete_personnel(request, personnel_id):
    """Suppression d'un employé et de son compte User (Boss/Superuser uniquement)."""
    personnel = get_object_or_404(Personnel, pk=personnel_id)
    
    if request.method == "POST":
        if personnel.user:
             personnel.user.delete()
        personnel.delete()
        messages.warning(request, f"L'employé {personnel.nom_complet} a été supprimé.")
        return redirect("personnel:liste_personnel")
        
    return render(request, "personnel/delete_personnel.html", {"personnel": personnel})