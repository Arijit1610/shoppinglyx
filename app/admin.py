from django.contrib import admin
from .models import Product, Addtocart, Orders, Category, Address
from django.utils.safestring import mark_safe
   

class BaseProductAdmin(admin.ModelAdmin):

    def preview_photo1(self, obj):
        if obj.photo1:
            return mark_safe('<img src="{url}" width="100px" />'.format(url=obj.photo1.url))
        else:
            return 'No Image'

    preview_photo1.short_description = 'Image Preview'


class ProductAdmin(BaseProductAdmin):
    list_display = ['product_name', 'price', 'qty', 'discount','preview_photo1']

admin.site.register(Product, ProductAdmin)
class OrderAdmin(admin.ModelAdmin):
	list_display = ["userid","product_id","qty","status"]
admin.site.register(Orders,OrderAdmin)
class AddtocartAdmin(admin.ModelAdmin):
	list_display = ["userid","product_id","qty"]
admin.site.register(Addtocart,AddtocartAdmin)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ["product_type"]
admin.site.register(Category,CategoryAdmin)

class AddressAdmin(admin.ModelAdmin):
	list_display = ["userid","name","address1","state","city","zipcode"]
admin.site.register(Address, AddressAdmin)

admin.site.site_header = "Prestocart Admin Panel"
admin.site.site_title = "Prestocart Admin Portal"
admin.site.index_title = "Welcome to Prestocart Ecommerce"
