from django.test import TestCase, Client, tag, SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from website.models import Product, Nutrition, Media
from website.management.commands.add_off_data import Command
from website.product_selector import replacement_picker, sugary_product_categories
from website.views import results
from selenium import webdriver
from decimal import Decimal
import os, time, random

# Create your tests here.

@tag("example")
class TestExample(SimpleTestCase):
    
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass 
    
    def test_if_the_page_is_at_the_right_address(self):
        
        response = self.client.get('')
        self.assertEqual(response.status_code, 200) # Verifier que l'adresse est la bonne. Ou plutôt qu'on arrive à l'atteindre. #Code 200.

@tag("db_addition")
class TestProductAdditionToDatabase(TestCase):
    
    def setUp(self):
        self.command = Command() 
        self.command.handle()

    def tearDown(self):
        pass 
 
    @tag("data-added")
    def test_if_data_has_been_added(self):
        
        total_products = Product.objects.count()
        total_nutrition = Nutrition.objects.count()
        total_media = Media.objects.count()

        self.assertGreaterEqual(total_products, 36*15) #Make sure there is more than 540 items or 15 items per category
        self.assertGreaterEqual(total_nutrition, 36*15)
        self.assertGreaterEqual(total_media, 36*15)

        self.assertEqual(total_products, total_nutrition)
        self.assertEqual(total_nutrition, total_media)

        # self.command.show_data("media_data")
    
    @tag("product-quality")
    def test_the_quality_of_product_data(self):

        def get_categories_from_categories_txt():
            file_path = os.path.join(os.path.dirname(__file__), "management", "commands", "categories.txt")
            with open(file_path) as f: 
                return [category.replace("\n","") for category in list(f)]   

        categories = get_categories_from_categories_txt()

        for product in Product.objects.all():
            self.assertNotEqual(len(product.product_name), 0) 
            self.assertIn(product.category, categories)
            self.assertIn("https://fr.openfoodfacts.org/produit/", product.off_url)
    
    @tag("media-quality")
    def test_the_quality_of_media_data(self):

        for media in Media.objects.all():
            self.assertIn("https://static.openfoodfacts.org/images/products/", media.image_full_url)
            self.assertIn("full", media.image_full_url)
            self.assertIn("https://static.openfoodfacts.org/images/products/", media.image_front_url)
            self.assertIn("400", media.image_front_url)

    @tag("nutrition-quality")
    def test_the_quality_of_nutrition_data(self):
        
        for nutrition in Nutrition.objects.all():
            self.assertIn(nutrition.nutriscore, "abcde")

            self.assertEqual(type(nutrition.energy_100g), Decimal)
            self.assertGreaterEqual(nutrition.energy_100g, 0)
            self.assertRegex(nutrition.energy_unit, r"^[kK]([Cc][Aa][Ll]|[Jj])$")

            self.assertEqual(type(nutrition.proteins_100g), Decimal)
            self.assertGreaterEqual(nutrition.proteins_100g, 0)

            self.assertEqual(type(nutrition.fat_100g), Decimal)
            self.assertGreaterEqual(nutrition.fat_100g, 0)

            self.assertEqual(type(nutrition.saturated_fat_100g), Decimal)
            self.assertGreaterEqual(nutrition.saturated_fat_100g, 0)

            self.assertEqual(type(nutrition.carbohydrates_100g), Decimal)
            self.assertGreaterEqual(nutrition.carbohydrates_100g, 0)

            self.assertEqual(type(nutrition.sugars_100g), Decimal)
            self.assertGreaterEqual(nutrition.sugars_100g, 0)

            self.assertEqual(type(nutrition.fiber_100g), Decimal)
            # self.assertGreaterEqual(nutrition.fiber_100g, 0)

            self.assertEqual(type(nutrition.salt_100g), Decimal)
            self.assertGreaterEqual(nutrition.salt_100g, 0)

class TestProductSelectorModule(TestCase):
    
    def setUp(self):
        self.command = Command()
        self.command.handle() 

    @tag("check")
    def test_if_replacement_picker_only_accepts_int(self):
        product_id = random.randint(0, len(Product.objects.all())-1)
        random_product = Product.objects.get(pk=product_id)
        
        with self.assertRaises(TypeError):
            substitute = replacement_picker(random_product, "a", "b")

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

@tag("replacement")
class TestProductReplacementFunction(StaticLiveServerTestCase):
    
    def setUp(self):
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))
   
    def tearDown(self):
        self.driver.quit() 

    @tag("repl_working?")
    def test_if_the_product_replacement_is_working_correctly(self):
        #Analyser ce que recoit la view en query

        self.command = Command()
        self.command.handle()

        products = ["bâtonnets de surimi", "Orangina", "Perrier fines bulles", "Pâtes Spaghetti au blé complet", "Salade de quinoa aux légumes", "Magnum Double Caramel"]
        substitutes = ["Filets de Colin Panés", "Perrier fines bulles", "Perrier fines bulles", "Coquillettes", "Betteraves à la Moutarde à l'Ancienne", "Les bios vanille douce sava"]
        i = 0
        
        # e = Product.objects.get(product_name__iexact="bâtonnets de surimi")
        # print(e.product_name)

        for product in products:
            self.driver.get("{}".format(self.live_server_url)) 

            searchbox = self.driver.find_element_by_name("query")
            searchbox.send_keys(product)
            searchbox.submit()

            substitute_name = self.driver.find_element_by_css_selector(".results.card-title").text
            self.assertEqual(substitute_name, substitutes[i])

            product_nutriscore = Product.objects.get(product_name__iexact=product).nutrition.nutriscore
            substitute_nutriscore = Product.objects.get(product_name__iexact=substitute_name).nutrition.nutriscore     

            self.assertLessEqual(ord(substitute_nutriscore), ord(product_nutriscore))
            time.sleep(1)
            i+=1
        
    @tag("repl_404")
    def test_if_404_is_correctly_raised(self):
        
        #Problème avec le mini client, une requete normale de type get("search", {"query":"orangina"}) donne une status_code de 404

        # Il existe Sans doute une autre façon de faire, faudrait la trouver

        self.driver.get("{}".format(self.live_server_url)) 

        searchbox = self.driver.find_element_by_name("query")
        searchbox.send_keys("orangin")
        searchbox.submit()
        time.sleep(1)

        error = self.driver.find_element_by_css_selector("h1").text
        self.assertEqual(error,"Not Found") #En mode débug s'entend

@tag("account")
class TestUserAccountCreation(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))
   
    def tearDown(self):
        self.driver.quit() 

    def test_if_user_account_data_is_correctly_added_to_the_database(self):
        
        user_info = {
                "username":"lusername",
                "last_name":"last",
                "first_name":"first",
                "mail":"first_last_who_cares@me.com",
                "password":"mucho_secure"
            }

        self.driver.get("{}{}".format(self.live_server_url, '/signup'))

        for field in ["username", "first_name", "last_name", "mail", "password"]:

            element = self.driver.find_element_by_name(field)
            element.send_keys(user_info[field])

            if field == "password":
                element.submit()

        time.sleep(1)
        
        user_added = User.objects.get(username="lusername")

        self.assertEqual(user_added.username, user_info["username"])
        self.assertEqual(user_added.first_name, user_info["first_name"])
        self.assertEqual(user_added.last_name, user_info["last_name"])
        self.assertEqual(user_added.email, user_info["mail"])
        self.assertTrue(check_password(user_info["password"], user_added.password))