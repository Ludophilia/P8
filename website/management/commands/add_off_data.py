from django.core.management.base import BaseCommand, CommandError
from website.models import Product, Nutrition, Media
import requests, os, re

class Command(BaseCommand):
    
    def get_categories_from_categories_txt(self):
        file_path = os.path.join(os.path.dirname(__file__), "categories.txt")
        with open(file_path) as f: 
            return [category.replace("\n","") for category in list(f)]

    def get_products_data_list_from_off(self, search_terms, page_size, page_number):
        
        search_pr = {"action": "process", 
        "search_terms": search_terms, 
        "sort_by": "unique_scans_n", 
        "page_size": page_size, 
        "page": page_number, 
        "json": "true"}

        data = requests.get('https://fr.openfoodfacts.org/cgi/search.pl', params = search_pr)
        
        return data.json()["products"]

    def get_product_data(self, product_dict, value):
        
        type1_values = ["product_name_fr", "url", "nutrition_grade_fr", "image_full_url", "image_front_url"]

        try:
            if value in type1_values:
                if value == "image_full_url":
                    return product_dict["image_front_url"].replace(".400.jpg", ".full.jpg")
                else:
                    return product_dict[value]
            else:
                return product_dict["nutriments"][value]

        except (KeyError):
            if re.search(r'^.{3,13}_100g$',value):
                return -999.99
            elif re.search(r'^.{3,13}_unit$',value):
                return "-"

    def check_if_important_values_exist(self, product_dict): 

        try:
            if len(product_dict["product_name_fr"]) != 0 and len(product_dict["nutrition_grade_fr"]) != 0:
                if len(product_dict["image_front_url"])!=0 and product_dict["nutriments"]["energy_100g"] >= 0:
                    return True
            else:
                return False
        except:
            return False

    def escape(self, string):
        specials = list("+*?.[]()$^")

        for special in specials:
            if special in string:
                string = string.replace(special, f"\{special}")

        return string
   
    def handle(self, *args, **options): 
        
        products_already_in_db = ""
        
        if Product.objects.count() == 0:

            for category in self.get_categories_from_categories_txt():

                for product in self.get_products_data_list_from_off(category, 20, 1):
                    
                    if self.check_if_important_values_exist(product):

                        product_name = self.get_product_data(product, "product_name_fr")

                        if not re.search(fr"{self.escape(product_name)}", products_already_in_db, re.I|re.M):
                        
                            products_already_in_db += f"\n{product_name}"

                            product_entry = Product.objects.create(
                                product_name = product_name,
                                off_url = self.get_product_data(product, "url"), 
                                category = category
                            )

                            print(f"Produit ajouté: {product_entry}")

                            Media.objects.create(
                                product = product_entry,
                                image_front_url = self.get_product_data(product, "image_front_url"),
                                image_full_url = self.get_product_data(product, "image_full_url")
                            )

                            Nutrition.objects.create(
                                product = product_entry,
                                nutriscore = self.get_product_data(product, "nutrition_grade_fr"),
                                energy_100g = self.get_product_data(product, "energy_100g"),
                                energy_unit = self.get_product_data(product, "energy_unit"),
                                proteins_100g = self.get_product_data(product, "proteins_100g"),
                                fat_100g = self.get_product_data(product, "fat_100g"),
                                saturated_fat_100g = self.get_product_data(product, "saturated-fat_100g"),
                                carbohydrates_100g = self.get_product_data(product, "carbohydrates_100g"),
                                sugars_100g = self.get_product_data(product, "sugars_100g"),
                                fiber_100g = self.get_product_data(product, "fiber_100g"),
                                salt_100g = self.get_product_data(product, "salt_100g")
                            )

    def show_data(self, type_data):
        
        if type_data == "product_data":
            for product in Product.objects.all():
                print("Product:", product.product_name, product.category, product.off_url)
        
        if type_data == "media_data":
            for media in Media.objects.all():
                print("Media:", media.image_front_url, media.image_full_url)

        if type_data == "nutrition_data":
            for nutriment in Nutrition.objects.all():
                print("Nutrition:", nutriment.product, nutriment.nutriscore, nutriment.energy_100g, nutriment.energy_unit,
                nutriment.proteins_100g, nutriment.fat_100g, nutriment.saturated_fat_100g, nutriment.carbohydrates_100g, nutriment.sugars_100g, nutriment.fiber_100g, nutriment.salt_100g)