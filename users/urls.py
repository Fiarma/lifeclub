# from django.urls import path
# from django.contrib.auth import views as auth_views 
# from django.urls import reverse_lazy 

# app_name = 'users'

# urlpatterns = [
#     # AUTHENTIFICATION
#     path('login/', auth_views.LoginView.as_view(
#         template_name='users/login.html'
#     ), name='login'),
#     path('logout/', auth_views.LogoutView.as_view(
#         next_page='users:login'
#     ), name='logout'), 

#     # CHANGEMENT DE MOT DE PASSE (Connecté)
#     path('password_change/', auth_views.PasswordChangeView.as_view(
#         template_name='users/password_change_form.html',
#         success_url=reverse_lazy('users:password_change_done') 
#     ), name='password_change'),
#     path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
#         template_name='users/password_change_done.html'
#     ), name='password_change_done'),

#     # RÉINITIALISATION MOT DE PASSE OUBLIÉ (FLUX PAR EMAIL)
#     path('password_reset/', auth_views.PasswordResetView.as_view(
#         template_name='users/password_reset_form.html',
#         email_template_name='users/password_reset_email.html',
#         subject_template_name='users/password_reset_subject.txt',
#         success_url=reverse_lazy('users:password_reset_done')
#     ), name='password_reset'),
#     path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
#         template_name='users/password_reset_done.html'
#     ), name='password_reset_done'),
#     path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
#         template_name='users/password_reset_confirm.html',
#         success_url=reverse_lazy('users:password_reset_complete')
#     ), name='password_reset_confirm'),
#     path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
#         template_name='users/password_reset_complete.html'
#     ), name='password_reset_complete'),
# ]


from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views 
from . import views 

app_name = 'users'

urlpatterns = [
    # AUTHENTIFICATION
    path('login/', views.CustomLoginView.as_view(), name='login'), # Vue personnalisée
    path('logout/', auth_views.LogoutView.as_view(
        next_page='users:login'
    ), name='logout'), 

    # CHANGEMENT DE MOT DE PASSE (Connecté)
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='users/password_change_form.html',
        success_url=reverse_lazy('users:password_change_done') 
    ), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='users/password_change_done.html'
    ), name='password_change_done'),

    # RÉINITIALISATION MOT DE PASSE OUBLIÉ (FLUX PAR EMAIL)
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset_form.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    
    # VUES PERSONNALISÉES (Déblocage)
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), 
        name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), 
        name='password_reset_complete'),
]