from django.urls import path
from . import views

app_name = "personnel"

urlpatterns = [
    path("", views.liste_personnel, name="liste_personnel"),
    path("add/", views.add_personnel, name="add_personnel"),
    path("edit/<str:personnel_id>/", views.edit_personnel, name="edit_personnel"),
    path("delete/<str:personnel_id>/", views.delete_personnel, name="delete_personnel"),
]
