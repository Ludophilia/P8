from django.db import models

# Create your models here.

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    off_url = models.TextField()
    category = models.CharField(max_length=200)

    class Meta:
        db_table = "Product"

class NutritionPanel(models.Model):
    product_id = models.OneToOneField(Product, to_field="product_id", primary_key = True, on_delete = models.CASCADE)
    nutriscore = models.CharField(max_length=1)
    energy_100g = models.DecimalField(max_digits=7, decimal_places=2)
    energy_unit = models.CharField(max_length=5)
    proteins_100g = models.DecimalField(max_digits=6, decimal_places=2)
    proteins_unit = models.CharField(max_length=5)
    fat_100g = models.DecimalField(max_digits=6, decimal_places=2)
    fat_unit = models.CharField(max_length=2)
    saturated_fat_100g = models.DecimalField(max_digits=6, decimal_places=2)
    saturated_fat_unit = models.CharField(max_length=2)
    carbohydrates_100g = models.DecimalField(max_digits=6, decimal_places=2)
    carbohydrates_unit = models.CharField(max_length=2)
    sugars_100g = models.DecimalField(max_digits=6, decimal_places=2)
    sugars_unit = models.CharField(max_length=2)
    fiber_100g = models.DecimalField(max_digits=6, decimal_places=2)
    fiber_unit = models.CharField(max_length=2)
    salt_100g = models.DecimalField(max_digits=6, decimal_places=2)
    salt_unit = models.CharField(max_length=2)

    class Meta:
        db_table = "NutritionPanel"

class Media(models.Model):
    product_id = models.OneToOneField(Product, to_field="product_id", primary_key=True, on_delete=models.CASCADE)
    image_front_url = models.TextField()
    image_back_url = models.TextField()

    class Meta:
        db_table = "Media"

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mail_address = models.CharField(max_length=200)
    password = models.CharField(max_length=48)

    class Meta:
        db_table = "User"

class Record(models.Model):
    record_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, to_field="user_id", on_delete=models.CASCADE)
    product_recorded = models.ForeignKey(Product, to_field="product_id", on_delete=models.CASCADE, related_name='product_recorded_set')
    product_searched = models.ForeignKey(Product, to_field="product_id", on_delete=models.CASCADE, related_name='product_searched_set')

    class Meta:
        db_table = "Record"     