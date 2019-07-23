from django.shortcuts import render

# Create your views here.
def home(request):
    var = {'title': "P8 - Plateforme pour Amateurs de Nutella"}
    return render(request, "index.html", var)

def results(request):
    var = {'title': "Resultats de la recherche", 
            'loops': range(6)}
    return render(request, "results.html", var)