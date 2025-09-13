from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Personnel
from .forms import PersonnelForm

# Liste du personnel
def liste_personnel(request):
    personnels = Personnel.objects.all()
    return render(request, "personnel/liste_personnel.html", {"personnels": personnels})

# Ajouter un employé
def add_personnel(request):
    if request.method == "POST":
        form = PersonnelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("personnel:liste_personnel")
    else:
        form = PersonnelForm()
    return render(request, "personnel/add_personnel.html", {"form": form})

# Modifier un employé
def edit_personnel(request, personnel_id):
    personnel = get_object_or_404(Personnel, pk=personnel_id)
    if request.method == "POST":
        form = PersonnelForm(request.POST, instance=personnel)
        if form.is_valid():
            form.save()
            return redirect("personnel:liste_personnel")
    else:
        form = PersonnelForm(instance=personnel)
    return render(request, "personnel/edit_personnel.html", {"form": form})

# Supprimer un employé
def delete_personnel(request, personnel_id):
    personnel = get_object_or_404(Personnel, pk=personnel_id)
    if request.method == "POST":
        personnel.delete()
        return redirect("personnel:liste_personnel")
    return render(request, "personnel/delete_personnel.html", {"personnel": personnel})
