from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# class


class Category(models.Model):
	product_type = models.CharField(max_length=20, unique=True)

	def __str__(self):
		return self.product_type

class Product(models.Model):
	usertypes = {'M': 'Mens', 'F': 'Womens', 'C': 'Children'}
	product_type = models.ForeignKey(Category, on_delete=models.CASCADE)
	company_name = models.CharField(max_length=100,null=True)
	product_name = models.CharField(max_length=100,null=True)
	product_section = models.CharField(max_length=20, choices=usertypes,blank=True)
	features = models.TextField(blank=True)
	size1 = models.CharField(max_length=3,blank=True)
	size2 = models.CharField(max_length=3, blank=True)
	size3 = models.CharField(max_length=3, blank=True)
	size4 = models.CharField(max_length=3, blank=True)
	price = models.DecimalField(decimal_places=2, max_digits=10, default = 1)
	qty = models.IntegerField(null = True)
	description = models.TextField(blank=True)
	photo1 = models.ImageField(upload_to='product_images/', blank=True)
	photo2 = models.ImageField(upload_to='product_images/', blank=True)
	photo3 = models.ImageField(upload_to='product_images/', blank=True)
	photo4 = models.ImageField(upload_to='product_images/', blank=True)
	discount = models.IntegerField(default = 1)

	def __str__(self):
		return self.product_name

	def discountprice(self):
		return int((self.price) - int((self.discount/100) * float(self.price)))


class Orders(models.Model):
	userid = models.ForeignKey(User, on_delete=models.CASCADE)
	product_id = models.ForeignKey(Product, on_delete = models.CASCADE)
	qty = models.IntegerField()
	status = models.CharField(max_length=20, default="Pending", choices={
		"Pending": "Pending",
		"Accepted": "Accepted",
		"Shiping": "Shiping",
		"Out for Delivery": "Out for Delivery",
		"Delivered": "Deliverd",
		"Canceled": "Canceled"
	})
	created_at = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)


	def __str__(self):
		return f"{self.userid.id}-{self.product_id}"


class Addtocart(models.Model):
	userid = models.ForeignKey(User, on_delete=models.CASCADE)
	product_id = models.ForeignKey(Product,on_delete=models.CASCADE)
	qty = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.userid.id}-{self.product_id}"
	def total(self):
		return self.qty * self.product_id.discountprice()

class Address(models.Model):
	statename = [
        ("Andhra Pradesh", "Andhra Pradesh"),
        ("Arunachal Pradesh", "Arunachal Pradesh"),
        ("Assam", "Assam"),
        ("Bihar", "Bihar"),
        ("Chhattisgarh", "Chhattisgarh"),
        ("Goa", "Goa"),
        ("Gujarat", "Gujarat"),
        ("Haryana", "Haryana"),
        ("Himachal Pradesh", "Himachal Pradesh"),
        ("Jharkhand", "Jharkhand"),
        ("Karnataka", "Karnataka"),
        ("Kerala", "Kerala"),
        ("Madhya Pradesh", "Madhya Pradesh"),
        ("Maharashtra", "Maharashtra"),
        ("Manipur", "Manipur"),
        ("Meghalaya", "Meghalaya"),
        ("Mizoram", "Mizoram"),
        ("Nagaland", "Nagaland"),
        ("Odisha", "Odisha"),
        ("Punjab", "Punjab"),
        ("Rajasthan", "Rajasthan"),
        ("Sikkim", "Sikkim"),
        ("Tamil Nadu", "Tamil Nadu"),
        ("Telangana", "Telangana"),
        ("Tripura", "Tripura"),
        ("Uttar Pradesh", "Uttar Pradesh"),
        ("Uttarakhand", "Uttarakhand"),
        ("West Bengal", "West Bengal"),
    ]
	userid = models.ForeignKey(User,on_delete=models.CASCADE)
	name =  models.CharField(max_length = 50, blank = False)
	phonenumber = models.DecimalField(max_digits=10, decimal_places=0, default = None)
	address1 = models.CharField(max_length = 50, blank = False)
	address2 = models.CharField(max_length = 50, blank = False)
	city = models.CharField(max_length = 50, blank = False)
	state = models.CharField(max_length = 50, blank = False, choices = statename)
	zipcode = models.DecimalField(max_digits=6, decimal_places=0)

	def __str__(self):
		return f"{self.userid.username} {self.name}"

	
