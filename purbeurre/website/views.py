from django.shortcuts import render, get_list_or_404, redirect
from website.models import Media, Product
from website.product_selector import replacement_picker
from website.forms import RegistrationForm, SignInForm, AuthenticationFormPlus
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.

def home(request):
    
    var = {'title': "P8 - Plateforme pour Amateurs de Nutella"}
    
    return render(request, "home.html", var)

def results(request):
    
    query = request.GET.get('query')
    product = get_list_or_404(Product, product_name__iexact=query)[0]
    
    product_name = product.product_name
    product_photo_url = product.media.image_full_url
    substitutes = replacement_picker(product, 0, 6)

    var = {'title': "Resultats de la recherche",
            'product_name': product_name,
            'product_photo_url': product_photo_url,
            'substitutes': substitutes}
            
    return render(request, "results.html", var)

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
    
    print("1 Vous êtes connecté en tant que: ", request.user)

    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)  

        if form.is_valid():

            user_obj = authenticate(
                username = form.cleaned_data["username"], 
                password = form.cleaned_data["password"]
                ) #test aaa, aaa

            login(request, user_obj)

            if request.user.is_authenticated:
                print("2 Vous êtes connecté en tant que: ", request.user)
                return redirect("/")

    else:
        form = AuthenticationForm(request)
    
    vars = {
        'title': "Connexion",
        'form' : form 
        }

    return render(request, "signin.html", vars)