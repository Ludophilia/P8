from django.shortcuts import render

# Create your views here.
def home(request):
    var = {'title': "P8 - Plateforme pour Amateurs de Nutella"}
    return render(request, "index.html", var)