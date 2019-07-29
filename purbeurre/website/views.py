from django.shortcuts import render, get_list_or_404
from website.models import Media, Product
from website.product_selector import replacement_picker


# Create your views here.
def home(request):
    
    var = {'title': "P8 - Plateforme pour Amateurs de Nutella"}
    
    return render(request, "index.html", var)

def results(request):
    
    query = request.GET['query'] #Afficher le nom de la query bâtonnets de surimi, Orangina, Perrier fines bulles, Pâtes Spaghetti au blé complet, Salade de quinoa aux légumes, Magnum Double Caramel 
    # print(query)
    
    # products_alike = Product.objects.filter(product_name__iexact=query)

    products_alike = get_list_or_404(Product, product_name__iexact=query) #Ca marche, ça lève bien l'exception, ça pourrait faire l'objet de tests
    product = products_alike[0]
    
    product_name = product.product_name # Alt: product_photo_url = Media.objects.filter(product__product_name=product_name)[0].image_front_url #Afficher photo produit de la query s'il existe
    product_photo_url = product.media.image_front_url

    substitutes = replacement_picker(product, 0, 6) #Remplacer le produit de la query

    #Obtenir des produits (nom, nutriscore, photos) 

    var = {'title': "Resultats de la recherche",
            'product_name': product_name,
            'product_photo_url': product_photo_url,
            'substitutes': substitutes}
            
    return render(request, "results.html", var)