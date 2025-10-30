from django.urls import path
from . import views

app_name = 'produits' 

urlpatterns = [
    # --- 1. Gestion des Catégories (CRUD) ---
    path('categories/', views.category_list, name='category_list'),
    path('categories/new/', views.category_create, name='category_create'),
    path('categories/edit/<int:pk>/', views.category_update, name='category_update'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    
    # --- 2. Gestion des Produits (CRUD) ---
    path('', views.product_list, name='product_list'), # Page d'accueil de l'app: liste des produits
    path('produits/new/', views.product_create, name='product_create'),
    path('produits/edit/<int:pk>/', views.product_update, name='product_update'),
    path('produits/delete/<int:pk>/', views.product_delete, name='product_delete'),
    
    # --- 3. Gestion de l'Inventaire (Fonctions) ---
    path('inventaire/', views.inventaire_list, name='inventaire_list'), 
    path('inventaire/new/', views.inventaire_create_update, name='inventaire_create'),
    path('inventaire/edit/<int:pk>/', views.inventaire_create_update, name='inventaire_update'), 
    path('inventaire/<int:pk>/', views.inventaire_detail, name='inventaire_detail'),
    path('inventaire/<int:pk>/validate/', views.inventaire_validate, name='inventaire_validate'),
    path('inventaire/ligne/<int:pk>/modifier/', views.inventaire_ligne_update, name='inventaire_ligne_update'),
    #path('ligne-inventaire/<int:pk>/edit/', views.ligne_inventaire_edit, name='ligne_inventaire_edit'),

# --- Fournisseurs (CRUD) ---
    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/creer/', views.fournisseur_create_update, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/modifier/', views.fournisseur_create_update, name='fournisseur_update'),
    path('fournisseurs/<int:pk>/supprimer/', views.fournisseur_delete, name='fournisseur_delete'),

    # --- Approvisionnements ---
    path('approvisionnements/', views.approvisionnement_list, name='approvisionnement_list'),
    path('approvisionnements/creer/', views.approvisionnement_create_update, name='approvisionnement_create'),
    path('approvisionnements/<int:pk>/', views.approvisionnement_detail, name='approvisionnement_detail'),
    path('approvisionnements/<int:pk>/modifier/', views.approvisionnement_create_update, name='approvisionnement_update'),
    path('approvisionnements/<int:pk>/valider/', views.approvisionnement_valider, name='approvisionnement_valider'),
    path('approvisionnements/<int:pk>/supprimer/', views.approvisionnement_delete, name='approvisionnement_delete'),
    path('approvisionnements/ligne/<int:pk>/modifier/', views.ligne_approvisionnement_update, name='ligne_approvisionnement_update'),
]
