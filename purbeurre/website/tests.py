from django.test import TestCase, Client, tag, SimpleTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase 
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from website.models import Product, Nutrition, Media, Record
from website.management.commands.add_off_data import Command
from website.product_selector import replacement_picker, sugary_product_categories
from website.views import results
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from decimal import Decimal
import os, time, random


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
        print("total products:", total_products) #Tester feedback

        self.assertGreaterEqual(total_nutrition, 36*15)
        print("total nutrition:", total_nutrition)

        self.assertGreaterEqual(total_media, 36*15)
        print("total media:", total_media) 

        self.assertEqual(total_products, total_nutrition)
        self.assertEqual(total_nutrition, total_media)

        if total_products == total_nutrition and total_nutrition == total_media: 
            print("Données uniformes, vous pouvez y aller!")
            if total_products < 600:
                print("C'est moins que la dernière fois en revanche.")

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
        
        self.command = Command()
        self.command.handle()

        products = ["bâtonnets de surimi", "Orangina", "Perrier fines bulles", "Pâtes Spaghetti au blé complet", "Salade de quinoa aux légumes", "Magnum Double Caramel"]
        substitutes = ["Filets de Colin Panés", "Cristaline", "Cristaline", "Coquillettes", "Betteraves à la Moutarde à l'Ancienne", "Les bios vanille douce sava"]
        i = 0
        
        for product in products:
            self.driver.get("{}".format(self.live_server_url)) 

            searchbox = self.driver.find_element_by_name("query")
            searchbox.send_keys(product)
            searchbox.submit()

            time.sleep(2)

            substitute_name = self.driver.find_element_by_css_selector(".results.card-title").text
            # self.assertEqual(substitute_name, substitutes[i]) # Retiré, le nom des substituts a changé en 1 mois et demi... Diable. Seul le nutriscore sera testé

            product_nutriscore = Product.objects.get(product_name__iexact=product).nutrition.nutriscore
            substitute_nutriscore = Product.objects.get(product_name__iexact=substitute_name).nutrition.nutriscore     

            self.assertLessEqual(ord(substitute_nutriscore), ord(product_nutriscore))
            i+=1
        
    @tag("repl_404")
    def test_if_404_is_correctly_raised(self):
        
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

@tag("connect")
class TestUserAccountConnection(StaticLiveServerTestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))
    
    def tearDown(self):
        self.driver.quit() 

    def test_if_connection_form_displays_the_error_message(self):

        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        self.driver.get("{}/{}".format(self.live_server_url, "signin"))
        time.sleep(3)

        for field in ["username", "password"]:

            element = self.driver.find_element_by_name(field)
            element.send_keys(user_info[field])

            if field == "password":
                element.submit()

        time.sleep(1)

        error_message = "Saisissez un nom d'utilisateur et un mot de passe valides. Remarquez que chacun de ces champs est sensible à la casse (différenciation des majuscules/minuscules)."

        error_message_in_webpage = self.driver.find_element_by_css_selector("ul.errorlist li")

        self.assertEqual(error_message, error_message_in_webpage.text)
    
    @tag("works")
    def test_if_connection_works_as_expected(self):
        
        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        User.objects.create_user(
            username = user_info['username'],
            password = user_info['password']
        )

        self.driver.get("{}/{}".format(self.live_server_url, "signin"))
        time.sleep(1)

        for field in ["username", "password"]:

            element = self.driver.find_element_by_name(field)
            element.send_keys(user_info[field])

            if field == "password":
                element.submit()

        time.sleep(1)

        self.assertEqual(self.driver.current_url, self.live_server_url+"/")

@tag("connectDjango")
class TestUserAccountConnectionDjangoClientVersion(TestCase):
    
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass
    
    @tag("error2")
    def test_if_connection_form_displays_the_error_message(self):

        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        response = self.client.post(path=reverse("signin"), data=user_info)

        error_message = "Saisissez un nom d&#39;utilisateur et un mot de passe valides. Remarquez que chacun de ces champs est sensible à la casse (différenciation des majuscules/minuscules)." #Eeeet oui, on réplique les erreurs

        self.assertIn(error_message, response.content.decode())

    @tag("works2")
    def test_if_connection_works_as_expected(self):
        
        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        User.objects.create_user(
            username = user_info['username'],
            password = user_info['password']
        )

        response = self.client.post(path=reverse("signin"), data=user_info)

        error_message = "Saisissez un nom d&#39;utilisateur et un mot de passe valides. Remarquez que chacun de ces champs est sensible à la casse (différenciation des majuscules/minuscules)."

        self.assertNotIn(error_message, response.content.decode())

        self.assertEqual(response.url, "/") # Juste la partie après le nom de domaine

@tag("nav")
class TestNavBarBehaviour(StaticLiveServerTestCase):    
    
    @tag("se-connecter")
    def test_if_se_connecter_appear_in_menubar_when_the_user_is_not_connected(self):
        # Tester que qu'il y ait bien marquer se connecter dans le logo de connection

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))

        self.driver.get(self.live_server_url)
        connect_logo = self.driver.find_element_by_css_selector(".fas.fa-user")
        self.assertEqual(connect_logo.text, "Se connecter")

        self.driver.quit()

    @tag("nav-redirect")
    def test_if_anonymous_user_is_redirected_to_sign_in_page(self):
        # Tester que appuyer sur mon compte envoie la page de connexion en mode Anonymous user

        self.client = Client()

        response = self.client.get("/account")
        self.assertRedirects(response,"/signin?next=/account")

    @tag("mon-compte")
    def test_if_mon_compte_appear_in_menubar_when_the_user_is_connected(self):
        # Tester que qu'il y ait bien marquer se connecter dans le logo de connection une fois connecté
        self.selenium_is_active = True
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),"chromedriver"))
        self.driver.get("{}{}".format(self.live_server_url, "/signin"))
        
        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        User.objects.create_user(
            username = user_info['username'],
            password = user_info['password']
        )

        for type_field in user_info: 
            field = self.driver.find_element_by_name(type_field)
            field.send_keys(user_info[type_field])

            if type_field == "password":
                field.submit()

        mon_compte = self.driver.find_element_by_css_selector(".fas.fa-user")

        self.assertEqual(mon_compte.text, "Mon compte")
        self.driver.quit()

    @tag("access")
    def test_if_a_connected_user_can_access_to_mon_compte_page(self):

        # Tester qu'un utilisateur connecté peut accéder au compte

        self.client = Client()

        user_info = {
            "username" : "username",
            "password" : "password"
        }

        User.objects.create_user(
            username = user_info["username"],
            password = user_info["password"]
        )

        self.client.post("/signin", data=user_info)
        response = self.client.get("/account")

        self.assertEqual(response.status_code, 200) #Si 200, c'est qu'on a pu accéder, si c'est  c'est 302 c'est qu'il y a eu une redirection

    @tag("deco")
    def test_if_clicking_on_logout_button_does_logout_the_user(self):
        
        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chromedriver"))

        self.driver.get("{}{}".format(self.live_server_url, "/signin"))
        
        user_info = {
            "username" : "lusername",
            "password" : "mucho_secure"
        }

        User.objects.create_user(
            username = user_info['username'],
            password = user_info['password']
        )

        for type_field in user_info: 
            field = self.driver.find_element_by_name(type_field)
            field.send_keys(user_info[type_field])

            if type_field == "password":
                field.submit()

        time.sleep(3)

        self.actions = ActionChains(self.driver)

        logout = self.driver.find_element_by_css_selector(".fas.fa-sign-out-alt")

        self.actions.move_to_element(logout).click().perform()

        mon_compte = self.driver.find_element_by_css_selector(".fas.fa-user")

        self.assertEqual(mon_compte.text, "Se connecter")
        self.driver.quit()
        
class TestAccountPage(StaticLiveServerTestCase):

    def setUp(self):
        
        self.user_info = {
            "username" : "lusername",
            "password" : "mucho_secure",
            "mail": "lusername@makeinu.com",
            "first_name": "luser",
            "last_name": "dunner"
        }

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),'chromedriver'))
        
        User.objects.create_user (
            username = self.user_info['username'],
            password = self.user_info['password'],
            email = self.user_info['mail'],
            first_name = self.user_info['first_name'],
            last_name = self.user_info['last_name']
        )

        self.driver.get('{}{}'.format(self.live_server_url, '/signin'))

        for fieldname in ['username', "password"]:
            field = self.driver.find_element_by_name(fieldname)
            field.send_keys(self.user_info[fieldname])

            if fieldname == "password":
                field.submit()
        
        self.driver.get('{}{}'.format(self.live_server_url, '/account'))

        time.sleep(1)

    def tearDown(self):
        self.driver.quit()

    @tag("myusername")
    def test_if_user_name_appear_on_account_page_header(self):
        
        # Tester que le nom de l'utilisateur apparait bien dans le header

        element = self.driver.find_element_by_css_selector("h1")
        self.assertEqual(element.text, "Ahoy {} !".format(self.user_info['username']).upper())
    
    @tag("accountinfo")
    def test_if_the_form_does_display_user_account_info(self):
        
        # Tester que le formulaire affiche bien les informations de l'utilisateur

        for fieldname in self.user_info:
            field = self.driver.find_element_by_name(fieldname)
            if fieldname != "password":
                self.assertEqual(field.get_attribute("value"), self.user_info[fieldname])
    
    @tag("userdont")
    def test_if_the_user_is_not_allowed_to_modify_his_account_info(self):

        # Tester que le formulaire n'est pas modifiable par l'utilisateur

        fieldset = self.driver.find_element_by_css_selector("fieldset")
        self.assertEqual(fieldset.get_attribute("disabled"), "true")

@tag("srecord")
class TestSubstituteRecording(StaticLiveServerTestCase):

    def setUp(self):
        
        # Remplissage de la base en produits

        self.command = Command()
        self.command.handle()
        
        # Création d'un utilisateur

        self.user_info = {
            "username" : "lusername",
            "password" : "mucho_secure",
            "mail": "lusername@makeinu.com",
            "first_name": "luser",
            "last_name": "dunner"
        }

        User.objects.create_user (
            username = self.user_info['username'],
            password = self.user_info['password'],
            email = self.user_info['mail'],
            first_name = self.user_info['first_name'],
            last_name = self.user_info['last_name']
        )

        # Connexion utiilisateur

        self.driver = webdriver.Chrome(os.path.join(os.path.dirname(os.path.dirname(__file__)),'chromedriver'))

        self.driver.get('{}{}'.format(self.live_server_url, '/signin'))

        for fieldname in ['username', "password"]:
            field = self.driver.find_element_by_name(fieldname)
            field.send_keys(self.user_info[fieldname])

            if fieldname == "password":
                field.submit()
        
    def tearDown(self):
        self.driver.quit()
    
    def test_if_the_user_can_associate_a_substitute_to_his_account(self):
        
        # Obtenir la page produit, celle d'orangina typiquement

        self.driver.get('{}{}'.format(self.live_server_url, '/'))

        searchbox = self.driver.find_element_by_name("query")
        searchbox.send_keys("orangina")
        searchbox.submit()

        save_link = self.driver.find_elements_by_css_selector("a.save-link")[0]

        ActionChains(self.driver).click(save_link).perform()

        time.sleep(1)
        
        print(Record.objects.all())

        recording = Record.objects.get(pk=1)
        subsitute = self.driver.find_elements_by_css_selector("h3.results")[0].text

        self.assertEqual(recording.user.username, "lusername")
        self.assertEqual(recording.substitute.product_name, subsitute)