from website.models import Product, Nutrition, Record

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

def product_url_builder(product_name):

    if "&" in product_name:
        product_name = product_name.replace("&", "%26")
    
    if " " in product_name:
        product_name = product_name.replace(" ", "%20")

    if "â" in product_name:
        product_name = product_name.replace("â", "%C3%A2")
    
    if "à" in product_name:
        product_name = product_name.replace("à", "%C3%A0")

    if "'" in product_name:
        product_name = product_name.replace("'", "%27")
    
    if "é" in product_name:
        product_name = product_name.replace("é", "%C3%A9")

    if "è" in product_name:
        product_name = product_name.replace("é", "%C3%A8")

    if "ç" in product_name:
        product_name = product_name.replace("é", "%C3%A7")   

    return "/product?query={}".format(product_name)

def replacement_picker(product, index_start, index_end):
    
    if type(index_start) == int and type(index_end) == int:

        substitute = Product.objects.filter(
            category__exact=product.category).order_by(
            "nutrition__nutriscore")

        if product.category in sugary_product_categories: 
            substitute = substitute.order_by("nutrition__sugars_100g", 
                "nutrition__saturated_fat_100g", 
                "nutrition__salt_100g")

        else:
            substitute = substitute.order_by("nutrition__saturated_fat_100g", 
                "nutrition__salt_100g", 
                "nutrition__sugars_100g")

    else:
        raise TypeError("index_start et index_end doivent être des int")

    return substitute[index_start:index_end]

def wrapper(product_list, **extra_args):

    def check_save_status(user_recordings):
        return "Sauvegardé" if user_recordings > 0 else "Sauvegarder"            

    products = [] # Wrapper ajoute le statut de sauvegarde de l'utilisateur du substitut à la liste des substituts 

    for product in product_list:

        product_name = product.product_name
        url = product_url_builder(product_name)

        if "user" in extra_args:
            
            user_recordings = Record.objects.filter(user__exact=extra_args['user']).filter(substitute__exact=product).count()
            save_status = check_save_status(user_recordings)
            
            products += [
                {"product": product,
                "status": save_status,
                "url": url}
            ]
          
        else:

            products += [
                {"product": product,
                "url": url}
            ]

    return products

