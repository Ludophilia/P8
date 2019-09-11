from django.shortcuts import render, get_list_or_404, redirect
from website.models import Media, Product, Record
from website.selection_tools import replacement_picker, wrapper
from website.forms import RegistrationForm, SignInForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.http import HttpResponse, Http404

def home(request):
    
    var = {'title': "P8 - Plateforme pour Amateurs de Nutella"}
    
    return render(request, "home.html", var)

def results(request):
    
    # Record.objects.all().delete() #Suppression rapide.

    query = request.GET.get('query')

    product = get_list_or_404(Product, product_name__iexact=query)[0]
    product_name = product.product_name
    product_photo_url = product.media.image_full_url
    
    if request.user.is_authenticated:
        substitutes_wrapped = wrapper(
            replacement_picker(product, 0, 6), 
            user = request.user)
    else:
        substitutes_wrapped = wrapper(replacement_picker(product, 0, 6))

    vars = {'title': "Resultats de la recherche",
            'product_name': product_name,
            'product_photo_url': product_photo_url,
            'substitutes_wrapped': substitutes_wrapped}
            
    return render(request, "results.html", vars)

def save(request):
    if request.method == 'POST':
        
        user_request = request.POST.get("request")
        substitute = request.POST.get('substitute')
        user_obj = request.user

        if user_request == "save":
            
            try:
                
                substitute_obj = Product.objects.get(pk=substitute)

                Record.objects.create(
                    user = user_obj,
                    substitute = substitute_obj
                )

                print("Nombre d'objects après create:", Record.objects.count())

                return HttpResponse("SaveOK")

            except:
                return HttpResponse("SaveError")

        if user_request == "unsave":
            
            try:
                
                substitute_obj = Product.objects.get(pk=substitute)

                Record.objects.filter(
                    user__exact=user_obj
                    ).filter(
                    substitute__exact=substitute_obj).delete()

                print("Nombre d'objects après delete:", Record.objects.count())
                    
                return HttpResponse("UnsaveOK")

            except:
                return HttpResponse("SaveError")

    else:
        raise Http404("Web ressource not found! Well excuuuuuuse us, your highness!")
    
def signup(request):
    
    if request.method == "POST":
        # print(request.POST.dict()) #Et ça marche : {'csrfmiddlewaretoken': '26jzicmx6iR3LxTY4AvA9Fsfw0ofgrKlcJSJqjrsDsHnRSFAm1s5ihKBNJiqfust', 'first_name': 'dd', 'last_name': 'dd', 'username': 'dd', 'mail': 'a@j.fr', 'password': 'rr'}
        
        User.objects.create_user(
            username = request.POST.get('username'),
            password = request.POST.get('password'),
            email = request.POST.get('mail'),
            first_name = request.POST.get('first_name'),
            last_name = request.POST.get('last_name')
        )

        # for user in User.objects.all():
        #     print(user)

        return redirect("/") #pas de retour utilisateur ? Avec redirect par exemple ? 

    var = {'title': "Inscrivez-vous",
          'form': RegistrationForm()}
    
    return render(request, "signup.html", var)

def signin(request):
    
    # print("1 Vous êtes connecté en tant que: ", request.user)
    # next = request.GET.get('next')
    # print("YA QUOI DEDANS", next)

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)  

        if form.is_valid():

            user_obj = authenticate(
                username = form.cleaned_data["username"], 
                password = form.cleaned_data["password"]
                ) #test aaa, aaa

            login(request, user_obj)

            if request.user.is_authenticated:
                # print("2 Vous êtes connecté en tant que: ", request.user)
                return HttpResponseRedirect("/")

    else:
        form = AuthenticationForm(request)
    
    vars = {
        'title': "Connexion",
        'form' : form 
        }

    return render(request, "signin.html", vars)

@login_required()
def account(request):

    user = request.user

    user_data = {
        'username':user.username,
        'first_name':user.first_name,
        'last_name':user.last_name,
        'mail': user.email
        }

    vars = {
        'title': "Mon compte",
        'form': RegistrationForm(initial=user_data)
    }

    return render(request, "account.html", vars)

def logoutv(request):
    logout(request)
    return redirect(reverse("home"))