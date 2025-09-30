from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Boisson, Commande, CommandeItem, Avoir
from boissons.models import Boisson
from personnel.models import Personnel

class CommandeItemInline(admin.TabularInline):
    model = CommandeItem
    extra = 1

@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    inlines = [CommandeItemInline]
    list_display = ['id','personnel','date_commande','montant_total','statut','type_paiement']



@admin.register(Avoir)
class AvoirAdmin(admin.ModelAdmin):
    list_display = ['id','commande','montant','statut','date_creation']
