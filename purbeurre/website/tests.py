from django.test import TestCase, Client, tag
from website.models import Product, Nutrition
from website.management.commands.add_off_data import Command
from website.product_selector import replacement_picker, sugary_product_categories
import random
from website.views import results

# from selenium import webdriver

# Create your tests here.

class TestWebsite(TestCase):
    
    def setUp(self):
        self.client = Client() # self.driver = webdriver.Chrome('app/tests/chromedriver')

    def tearDown(self):
        pass # self.driver.quit()
    
    def test_if_the_page_is_at_the_right_address(self):
        
        response = self.client.get('')
        self.assertEqual(response.status_code, 200) # Verifier que l'adresse est la bonne. Ou plutôt qu'on arrive à l'atteindre. #Code 200.

class TestProductAddition(TestCase):
    
    def setUp(self):
        pass

    def tearDown(self):
        pass 

    @tag("db_addition")
    def test_what_handle_returns(self):
        command = Command()
        command.handle() #Builds the database
        command.show_data("media_data")

class TestProductSelector(TestCase):
    
    def setUp(self):
        command = Command()
        command.handle() #Builds the database

    def tearDown(self):
        pass 

    @tag("check")
    def test_if_replacement_picker_only_accepts_int(self):
        product_id = random.randint(0, len(Product.objects.all())-1)
        random_product = Product.objects.get(pk=product_id)
        
        with self.assertRaises(TypeError):
            substitute = replacement_picker(random_product, "a", "b")

    @tag("not-really-a-test")
    def test_what_products_replacement_picker_gives_to_the_user(self):
        product_id = random.randint(0, len(Product.objects.all())-1)
        
        random_product = Product.objects.get(pk=product_id)
        substitute = replacement_picker(random_product, 0, 6)

        print("Produit:",
            random_product.product_name,
            random_product.nutrition.nutriscore,
            random_product.nutrition.saturated_fat_100g,
            random_product.nutrition.sugars_100g,
            random_product.nutrition.salt_100g)

        for substitute in substitute: 
            print("Substitut:",
                substitute.product_name,
                substitute.nutrition.nutriscore,
                substitute.nutrition.saturated_fat_100g,
                substitute.nutrition.sugars_100g,
                substitute.nutrition.salt_100g)

    @tag("best-result")
    def test_if_the_first_replacement_prodiuct_is_better_from_a_nutrition_standpoint(self):
    
        product_id = random.randint(0, len(Product.objects.all())-1)
        
        random_product = Product.objects.get(pk=product_id)
        substitute = replacement_picker(random_product, 0,1) #  Determiner produit avec replacement_picker

        print(random_product.product_name,
            random_product.nutrition.nutriscore,
            random_product.nutrition.saturated_fat_100g,
            random_product.nutrition.sugars_100g,
            random_product.nutrition.salt_100g)

        # for substitute in substitute: 
        print(substitute.product_name,
            substitute.nutrition.nutriscore,
            substitute.nutrition.saturated_fat_100g,
            substitute.nutrition.sugars_100g,
            substitute.nutrition.salt_100g)
        
        # Non rigoureux : on aurait du vérifier pour toutes les valeurs mais bon... On va s'arrêter là, ce n'est qu'un exercice.

        self.assertLessEqual(ord(substitute.nutrition.nutriscore), ord(random_product.nutrition.nutriscore)) 

        self.assertLessEqual(substitute.nutrition.saturated_fat_100g, random_product.nutrition.saturated_fat_100g)

        if random_product.category in sugary_product_categories:
            self.assertLessEqual(substitute.nutrition.sugars_100g, random_product.nutrition.sugars_100g)
        else:
            self.assertLessEqual(substitute.nutrition.salt_100g, random_product.nutrition.salt_100g)

class TestViewFunctions(TestCase):
    
    def setUp(self):
        command = Command()
        command.handle() #Builds the database

    def tearDown(self):
        pass 

    def test_a_def(self):
        #Analyser ce que recoit la view en query
        pass
