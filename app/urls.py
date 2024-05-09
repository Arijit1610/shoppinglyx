from django.urls import path
from app import views
urlpatterns = [
    path('', views.home, name='home'),
    path('productdetail/<productid>', views.product_detail, name='productdetail'),
    path('cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/remove-item/', views.RemoveItem, name='removeitem'),
    path('cart/change-noof-item/', views.ChangenoofItem, name='change'),
	
    path('cart/<productid>', views.product_add_to_cart, name='product_add-to-cart'),
    # path('buy/', views.buy_now, name='buy-now'),
    path('profile/', views.profile, name='profile'),
    path('address/', views.address, name='address'),
    path('orders/', views.orders, name='orders'),
    path('changepassword/', views.change_password, name='changepassword'),
    # path('mobile/', views.mobile, name='mobile'),
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logoutpage, name='logout'),
    path('registration/', views.customerregistration, name='customerregistration'),
    path('checkout/', views.checkout, name='checkout'),
	path('activate/<uidb64>/<token>', views.activate, name='activate'),
	path('search/', views.searchProducts, name = 'search'),
	path('payment-status/', views.success, name = 'success'),
	path('order/cancel',views.cancel, name="ordercancel"),
	path('newsletter', views.NewsLetter,name='newsletter')
]
