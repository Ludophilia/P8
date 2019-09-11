from website.models import Product, Nutrition, Record

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

def replacement_picker(product, index_start, index_end): #product est un produit obtenu via un query selector
    
    # Le but : un produit en entrée
    if type(index_start) == int and type(index_end) == int:

        if product.category in sugary_product_categories: #On peut aussi modifier l'ordre du traitement en fonction des aliments. Les aliments sucres auront un ordre de filtrage different des aliments salés.

            substitute = Product.objects.filter(
                    category__exact=product.category    #Produit de la même category
                ).order_by(
                    "nutrition__nutriscore",
                    "nutrition__sugars_100g",
                    "nutrition__saturated_fat_100g",
                    "nutrition__salt_100g"
                )[index_start:index_end]

        else:
            
            substitute = Product.objects.filter(
                    category__exact=product.category    #Produit de la même category
                ).order_by(
                    "nutrition__nutriscore",
                    "nutrition__saturated_fat_100g",
                    "nutrition__salt_100g",
                    "nutrition__sugars_100g"
                )[index_start:index_end]
    else:
        raise TypeError("index_start et index_end doivent être des int")

    return substitute #Un queryset produit plus sain en sortie

def wrapper(substitutes_list, **extra_args):

    substitutes = [] # Wrapper ajoute le statut de sauvegarde de l'utilisateur du substitut à la liste des substituts 

    for substitute in substitutes_list:

        if "user" in extra_args:
            
            user_recordings = Record.objects.filter(user__exact=extra_args['user']).filter(substitute__exact=substitute).count()

            if user_recordings > 0:
                substitutes += [
                    {"product": substitute,
                    "save_button_text": "Sauvegardé",
                    "save_button_class": "save-link"}
                ]
            else:
                substitutes += [
                    {"product": substitute,
                    "save_button_text": "Sauvegarder",
                    "save_button_class": "save-link"}
                ]
        else:

            substitutes += [
                {"product": substitute
                }
            ]

    return substitutes