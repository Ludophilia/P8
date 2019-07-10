from django.core.management.base import BaseCommand, CommandError
from website.models import Product, NutritionPanel, Media
import requests
import os
import re

class Command(BaseCommand):
    
    def handle(self, *args, **options): 
        
        # Obtenir les catégories vu que les requetes sont faites categories par categories

        def get_categories_from_categories_txt():
            file_path = os.path.join(os.path.dirname(__file__), "categories.txt")
            with open(file_path) as f: 
                return [category.replace("\n","") for category in list(f)]

        # Obtenir les données d'OFF

        def get_products_data_list_from_off(search_terms, page_size, page_number):
            
            search_pr = {"action": "process", 
            "search_terms": search_terms, 
            "tagtype_0":"categories", 
            "tag_contains_0":"contains", 
            "tag_0": search_terms, 
            "sort_by": "unique_scans_n", 
            "page_size": page_size, 
            "page": page_number, 
            "json": "true"}

            data = requests.get('https://fr.openfoodfacts.org/cgi/search.pl', params = search_pr)
            
            return data.json()["products"] 

        for category in get_categories_from_categories_txt():

            for product in get_products_data_list_from_off(category, 20, 1):

                def get_product_data(product_dict, value):
                    
                    type1_values = ["product_name_fr", "url", "nutrition_grade_fr", "image_front_url", "image_thumb_url"]

                    try:
                        if value in type1_values:
                            return product_dict[value]
                        else:
                            return product_dict["nutriments"][value]

                    except (KeyError):
                        if value == "nutrition_grade_fr":
                            return "-"
                        elif re.search(r'^.{3,13}_100g$',value):
                            return 0
                        elif re.search(r'^.{3,13}_unit$',value):
                            return "-"

                product_entry = Product.objects.create(
                    product_name = get_product_data(product, "product_name_fr"),
                    off_url = get_product_data(product, "url"), 
                    category = category
                )

                Media.objects.create(
                    product = product_entry,
                    image_front_url = get_product_data(product, "image_front_url"),
                    image_back_url = get_product_data(product, "image_thumb_url")
                )

                NutritionPanel.objects.create(
                    product = product_entry,
                    nutriscore = get_product_data(product, "nutrition_grade_fr"),
                    energy_100g = get_product_data(product, "energy_100g"),
                    energy_unit = get_product_data(product, "energy_unit"),
                    proteins_100g = get_product_data(product, "proteins_100g"),
                    proteins_unit = get_product_data(product, "proteins_unit"),
                    fat_100g = get_product_data(product, "fat_100g"),
                    fat_unit = get_product_data(product, "fat_unit"),
                    saturated_fat_100g = get_product_data(product, "saturated-fat_100g"),
                    saturated_fat_unit = get_product_data(product, "saturated-fat_unit"),
                    carbohydrates_100g = get_product_data(product, "carbohydrates_100g"),
                    carbohydrates_unit = get_product_data(product, "carbohydrates_unit"),
                    sugars_100g = get_product_data(product, "sugars_100g"),
                    sugars_unit = get_product_data(product, "sugars_unit"),
                    fiber_100g = get_product_data(product, "fiber_100g"),
                    fiber_unit = get_product_data(product, "fiber_unit"),
                    salt_100g = get_product_data(product, "salt_100g"),
                    salt_unit = get_product_data(product, "salt_unit")
                )

        for product in Product.objects.all():
            print("Product:", product.product_id, product.product_name, product.category)
        
        for media in Media.objects.all():
            print("Media:", media.product, media.image_front_url, media.image_back_url)

        for nutriment in NutritionPanel.objects.all():
            print("Nutrition:", nutriment.product, nutriment.nutriscore, nutriment.energy_100g, nutriment.energy_unit, nutriment.proteins_100g, nutriment.proteins_unit, nutriment.fat_100g, nutriment.fat_unit, nutriment.saturated_fat_100g, nutriment.saturated_fat_unit, nutriment.carbohydrates_100g, nutriment.carbohydrates_unit, nutriment.sugars_100g, nutriment.sugars_unit, nutriment.salt_100g, nutriment.salt_unit)