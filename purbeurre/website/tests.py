from django.test import TestCase, Client
from selenium import webdriver

# Create your tests here.

class TestWebsite(TestCase): #Nom à changer
    
    def SetUp(self):
        pass # self.driver = webdriver.Chrome('app/tests/chromedriver')

    def tearDown(self):
        pass # self.driver.quit()
    
    def test_if_the_page_is_at_the_right_address(self):
        
        self.client = Client()

        # Verifier que l'adresse est la bonne. Ou plutôt qu'on arrive à l'atteindre. #Code 200.
        # self.driver.get("localhost:8943")
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
