from website.models import Product, Nutrition

#Que faire? 

# Trouver un produit de remplacement au produit recherché (même catégorie)

#obj produit : Product.objects.get(pk=1)

sugary_product_categories = [
    "Biscuits et gâteaux", 
    "Barres Chocolats noirs",
    "Chocolats au lait",
    "Viennoiseries",
    "Pâtes à tartiner",
    "Confitures de fruits",
    "Céréales pour petit-déjeuner",
    "Chocolats en poudre",
    "Jus de fruits",
    "Boissons gazeuses",
    "Pizzas",
    "Céréales préparées",
    "Yaourts",
    "Crèmes dessert",
    "Compotes",
    "Glaces et sorbets",
    "Fruits en conserve"
    ]

def replacement_picker(product): #product est un produit obtenu via un query selector
    
    # Le but : un produit en entrée

    if product.category in sugary_product_categories: #On peut aussi modifier l'ordre du traitement en fonction des aliments. Les aliments sucres auront un ordre de filtrage different des aliments salés.

        substitute = Product.objects.filter(
                category__exact=product.category    #Produit de la même category
            ).order_by(
                "nutrition__nutriscore",
                "nutrition__sugars_100g",
                "nutrition__saturated_fat_100g",
                "nutrition__salt_100g"
            )[0]

    else:

        substitute = Product.objects.filter(
                category__exact=product.category    #Produit de la même category
            ).order_by(
                "nutrition__nutriscore",
                "nutrition__saturated_fat_100g",
                "nutrition__salt_100g",
                "nutrition__sugars_100g"
            )[0]

    return substitute #Un objet_produit produit plus sain en sortie