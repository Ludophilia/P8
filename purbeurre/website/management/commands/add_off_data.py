from django.core.management.base import BaseCommand, CommandError
from website.models import Product, NutritionPanel, Media
import requests, os, re

class Command(BaseCommand):
    
    def handle(self, *args, **options): 
        
        def get_categories_from_categories_txt():
            file_path = os.path.join(os.path.dirname(__file__), "categories.txt")
            with open(file_path) as f: 
                return [category.replace("\n","") for category in list(f)]

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

        def get_product_data(product_dict, value):
            
            type1_values = ["product_name_fr", "url", "nutrition_grade_fr", "image_front_url", "image_thumb_url"]

            try:
                if value in type1_values:
                    return product_dict[value]
                else:
                    return product_dict["nutriments"][value]

            except (KeyError):

                if re.search(r'^.{3,13}_100g$',value):
                    return -999.99
                elif re.search(r'^.{3,13}_unit$',value):
                    return "-"

        def check_if_important_values_exist(product_dict): 

            try:
                if len(product_dict["product_name_fr"]) != 0 and len(product_dict["nutrition_grade_fr"]) != 0 and product_dict["nutriments"]["energy_100g"] >= 0:
                    return True
                else:
                    return False
            except:
                return False

        for category in get_categories_from_categories_txt():

            for product in get_products_data_list_from_off(category, 20, 1):

                if check_if_important_values_exist(product):

                    product_entry = Product.objects.create(
                        product_name = get_product_data(product, "product_name_fr"),
                        off_url = get_product_data(product, "url"), 
                        category = category
                    )

                    Media.objects.create(
                        product = product_entry,
                        image_front_url = get_product_data(product, "image_front_url"),
                        image_thumb_url = get_product_data(product, "image_thumb_url")
                    )

                    NutritionPanel.objects.create(
                        product = product_entry,
                        nutriscore = get_product_data(product, "nutrition_grade_fr"),
                        energy_100g = get_product_data(product, "energy_100g"),
                        energy_unit = get_product_data(product, "energy_unit"),
                        proteins_100g = get_product_data(product, "proteins_100g"),
                        fat_100g = get_product_data(product, "fat_100g"),
                        saturated_fat_100g = get_product_data(product, "saturated-fat_100g"),
                        carbohydrates_100g = get_product_data(product, "carbohydrates_100g"),
                        sugars_100g = get_product_data(product, "sugars_100g"),
                        fiber_100g = get_product_data(product, "fiber_100g"),
                        salt_100g = get_product_data(product, "salt_100g")
                    )

        for product in Product.objects.all():
            print("Product:", product.product_id, product.product_name, product.category)
        
        for media in Media.objects.all():
            print("Media:", media.product, media.image_front_url, media.image_thumb_url)

        for nutriment in NutritionPanel.objects.all():
            print("Nutrition:", nutriment.product, nutriment.nutriscore, nutriment.energy_100g, nutriment.energy_unit,
            nutriment.proteins_100g, nutriment.fat_100g, nutriment.saturated_fat_100g, nutriment.carbohydrates_100g, nutriment.sugars_100g, nutriment.fiber_100g, nutriment.salt_100g)