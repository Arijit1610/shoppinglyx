from django.shortcuts import render, redirect 
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, UserLoginForm, PasswordChangeForm
import random
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib import messages
from .tokens import account_activation_token
from django.contrib.auth.models import User
from .models import *
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

client = razorpay.Client(
	auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def activateEmail(request, user, to_email):
	mail_subject = 'Activate your user account.'
	message = render_to_string('app/template_activate_account.html', {
		'user': user.username,
		'domain': get_current_site(request).domain,
		'uid': urlsafe_base64_encode(force_bytes(user.pk)),
		'token': account_activation_token.make_token(user),
		'protocol': 'https' if request.is_secure() else 'http'
	})
	email = EmailMessage(mail_subject, message, to=[to_email])
	if email.send():
		messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
				received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
	else:
		messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')

def home(request):
	fashion = Product.objects.filter(product_type__product_type ="Clothing")
	eletronices = Product.objects.filter(product_type__product_type="Electronices")
	sports = Product.objects.filter(product_type__product_type="Sports")
	schoolitems = Product.objects.filter(product_type__product_type="Readings and School")
	homeitems = Product.objects.filter(product_type__product_type="Home and Kitchen")
	cosmetics = Product.objects.filter(product_type__product_type="Cosmetics")
	carts = []
	print(homeitems)
	User = get_user_model()
	if request.user.is_authenticated:
		user_instance = User.objects.get(id=request.user.id)
		carts = Addtocart.objects.filter(userid=user_instance)
	else:
		user_instance = None
	context = {
		# "products": products,
		"noofitems" : len(carts),
		"electronices" : eletronices,
		"fashions" :fashion,
		"sports" : sports,
		"schoolitems" : schoolitems,
		"homeitems" : homeitems,
		"cosmetics" : cosmetics
	}

	return render(request, 'app/home.html', context)

def product_detail(request,productid):
	product = Product.objects.get(id=productid)
	carts = []

	User = get_user_model()
	if request.user.is_authenticated:
		user_instance = User.objects.get(id=request.user.id)
		carts = Addtocart.objects.filter(userid=user_instance)
	else:
		# Handle the case where the user does not exist
		user_instance = None
	context = {
		"product" : product,
		"noofitems" : len(carts)
	}
	# print(product.product_type)


	return render(request, 'app/productdetail.html',context)

@login_required(login_url="login")
def add_to_cart(request):
	print(request.user)
	User = get_user_model()
	user_instance = User.objects.get(id=request.user.id)
	carts = Addtocart.objects.filter(userid=user_instance)
	addreses = Address.objects.filter(userid = user_instance)
	# products = Product.objects.all()
	print(len(carts))
	total = 0
	shiping = 0
	for cart in carts:
		if cart.qty <= cart.product_id.qty:
			total = total + (cart.product_id.discountprice() * cart.qty)
			shiping = shiping + (cart.qty*40)
	alltotal = total+shiping
	if request.method == 'POST':
		addressid = request.POST.get('addressinput')
		print(addressid)
		for cart in carts:
			cart.addresssid = Address.objects.get(id = addressid)
			cart.save()
		return redirect('checkout')
	
	

	context = {
		"items" : carts,
		"total" :total,
		"shiping": shiping,
		"alltotal": alltotal,
		"noofitems" : len(carts),
		"addreses" : addreses 
	}
	return render(request, 'app/addtocart.html',context)
@login_required(login_url="login")
def product_add_to_cart(request,productid):
	User = get_user_model()
	user_instance = User.objects.get(id=request.user.id)
	product = Product.objects.get(id=productid)
	try:
		cart = Addtocart.objects.get(product_id=productid)
		cart.qty += 1
	except:
		cart = Addtocart(userid=user_instance, product_id = product, qty = 1)
	cart.save()
	messages.success(request,f"{cart.product_id.product_name[:10]} successfully added to your cart")
	return redirect('add-to-cart')
@login_required(login_url="login")
def buy_now(request):
	return render(request, 'app/buynow.html')
@login_required(login_url="login")
def profile(request):
	next = request.GET.get('next')
	User = get_user_model()
	if request.user.is_authenticated:
		user_instance = User.objects.get(id=request.user.id)
		carts = Addtocart.objects.filter(userid=user_instance)
	if request.method == 'POST':
		name = request.POST.get('name')
		phonenumber  = request.POST.get('phonenumber')
		address1  = request.POST.get('address1')
		address2  = request.POST.get('address2')
		city  = request.POST.get('city')
		state  = request.POST.get('state')
		zipcode  = request.POST.get('zipcode')
	try:
		address = Address(userid = user_instance, name = name, phonenumber = phonenumber, address1 = address1, address2 = address2, city = city, state = state, zipcode = zipcode)
		address.save()
		if next:
			return redirect(next)
		else:
			return redirect('address')
	except:
		pass
	context = {
		# "product" : product,
		"noofitems" : len(carts),
		"states" : Address.statename
	}

	return render(request, 'app/profile.html',context)
@login_required(login_url="login")
def address(request):
	carts = []
	addreses = []
	User = get_user_model()
	if request.user.is_authenticated:
		user_instance = User.objects.get(id=request.user.id)
		carts = Addtocart.objects.filter(userid=user_instance)
		addreses = Address.objects.filter(userid = user_instance)
	else:
		# Handle the case where the user does not exist
		user_instance = None
	context = {
		# "products": products,
		"noofitems" : len(carts),
		"addreses" : addreses

	}

	return render(request, 'app/address.html',context)
@login_required(login_url="login")
def orders(request):
	carts = []

	User = get_user_model()
	if request.user.is_authenticated:
		user_instance = User.objects.get(id=request.user.id)
		carts = Addtocart.objects.filter(userid=user_instance)
		orders = Orders.objects.filter(userid = user_instance).order_by('-created_at')
	else:
		# Handle the case where the user does not exist
		user_instance = None
	context = {
		# "products": products,
		"noofitems" : len(carts),
		"items" : orders,
		'now': timezone.now(),

	}

	# orders = Orders(product_type =  )
	return render(request, 'app/orders.html',context)

@login_required(login_url="login")
def change_password(request):
	
	return render(request, 'app/changepassword.html')

def mobile(request):
	carts = []

	User = get_user_model()
	if request.user.is_authenticated:
		user_instance = User.objects.get(id=request.user.id)
		carts = Addtocart.objects.filter(userid=user_instance)
	else:
		# Handle the case where the user does not exist
		user_instance = None
	context = {
		# "products": products,
		"noofitems" : len(carts)
	}

	return render(request, 'app/mobile.html',context)

def loginpage(request):
	messages.info(request,"Welcome to Prestocart. Please log in to access your account, access exclusive features and content." )
	next = request.GET.get('next')
	print(next)
	if request.user.is_authenticated:
		return redirect('home')
	form = UserLoginForm()
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		print(username)
		try:
			try:
				print("block1")
				user = User.objects.get(email=username)
				print(user.username)
				user = authenticate(
					request, username=user.username, password=password)
				print(password)
				print(user.password)
				login(request, user)
				messages.success(request, f"Hello {user.username}! You have been logged in")
				print("login Sucessess")
				if next:
					return redirect(next)
				else:
					return redirect('home')
			except:
				print("block2")
				user = authenticate(request, username=username, password=password)
				print("block3")
				print(password)
				print(user.password)
				login(request, user)
				print("newblock")
				messages.success(request, f"Hello {user.username}! You have been logged in")
				print("login Sucessess")
				if next:
					return redirect(next)
				else:
					return redirect('home')
		except:
			try:
				print("block4")
				try:
					print("block5")
					user = User.objects.get(email=username)
				except:
					print("block6")
					user = User.objects.get(username=username)
				print("block7")
				messages.error(
					request, "Incorrect Password!!! Please Try Again or your account is not acctivated yet please activate your account")
			except:
				print("block8")
				messages.error(
					request, "User Not Found!!! Please Create Your Account ")
			print("block9")
			print("login failure")
	context = { 'form': form}
	return render(request, "app/login.html", context)
@login_required(login_url="login")
def logoutpage(request):
	messages.info(request,"You have successfully logged out. Thank you for visiting. We look forward to welcoming you back soon. Have a great day!" )
	logout(request)
	return redirect('home')
def customerregistration(request):
	if request.user.is_authenticated:
		return redirect('home')
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		username = request.POST.get('username')
		firstname = request.POST.get('first_name')
		lastname = request.POST.get('last_name')
		email = request.POST.get('email')
		password1 = request.POST.get('password1')
		password2 = request.POST.get('password2')
		print(f"{username}{firstname}{lastname}{email}{password1}{password2}")
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = False
			user.save()
			print("saved")
			activateEmail(request, user, form.cleaned_data.get('email'))
			return redirect('login')
		else:
			print("else block")
			errors = form.errors
			print(errors)
			# return render(request, 'app/customerregistration.html', {'form': form, 'errors': errors})
			username_error = None
			email_error = None
			password_error = None
			if 'username' in errors:
				username_error = errors['username'][0]
				messages.error(request, username_error)
			if 'email' in errors:
				email_error = errors['email'][0]
				messages.error(request,email_error )
			if 'password1' in errors or 'password2' in errors:
				password_error = "Password validation failed."
				messages.error(request, password_error)
			return render(request, 'app/customerregistration.html', {'form': form, 'username_error': username_error, 'email_error': email_error, 'password_error': password_error})
	else:
		print("elseblock2")
		form = RegistrationForm()
	return render(request, 'app/customerregistration.html',{'form': form})

def checkout(request):
	User = get_user_model()
	user_instance = User.objects.get(id=request.user.id)
	carts = Addtocart.objects.filter(userid=user_instance)
	addreses = Address.objects.filter(userid = user_instance)
	# products = Product.objects.all()
	# print(len(carts))
	total = 0
	shiping = 0
	for cart in carts:
		if cart.qty <= cart.product_id.qty:
			total = total + (cart.product_id.discountprice() * cart.qty)
			shiping = shiping + (cart.qty*40)
	alltotal = total+shiping
	paisa = alltotal*100

	payment = client.order.create({
		"amount": paisa,
		"currency": "INR",
		"receipt": "receipt#1",
		"notes": {
			"key1": "value3",
			"key2": "value2"
		}
	})
	for cart in carts:
		cart.rozorpay_order_id = payment['id']
		cart.save()
	print(payment['id'])
	
	# allorder = client.order.fetch('order_O3eyrIuiNq7XkM')
	# print(allorder)

	context = {
		"items" : carts,
		"total" :total,
		"shiping": shiping,
		"alltotal": alltotal,
		"noofitems" : len(carts),
		"addreses" : addreses,
		"paisa" : paisa,
		"payment" : payment
	} 
	return render(request, 'app/checkout.html',context)



def activate(request, uidb64, token):
	User = get_user_model()
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		if user.is_active == True:
			messages.info(request, 'You have already activated your account')
		else:
			user.is_active = True
			user.save()

			messages.success(
				request, 'Thank you for your email confirmation. Now you can login your account.')
	else:
		messages.error(request, 'Activation link is invalid!')
	if request.user.is_authenticated:
		return redirect('home')

	return redirect('login')

def searchProducts(request):
	carts = []

	User = get_user_model()
	if request.user.is_authenticated:
		user_instance = User.objects.get(id=request.user.id)
		carts = Addtocart.objects.filter(userid=user_instance)
	else:
		# Handle the case where the user does not exist
		user_instance = None
	query = request.GET.get('q')
	if query == "":
		return redirect('home')
	print("query="+query)
	products = Product.objects.filter(product_name__icontains=query) | \
		Product.objects.filter(company_name__icontains=query) | \
		Product.objects.filter(product_section__icontains=query) | \
		Product.objects.filter(product_type__product_type__icontains=query)

	
	if products:
		items = True
	else:
		items = False
	context = {
		'products': products,
		'query': query,
		'items' : items,
		"noofitems" : len(carts)
	}
	
	return render(request, 'app/search_results.html', context)
@login_required(login_url="login")
@csrf_exempt
def success(request):
	order_id = request.GET.get('order_id')
	# print(order_id)
	checkorder = client.order.fetch(order_id)
	# print(checkorder)

	carts = Addtocart.objects.filter(rozorpay_order_id = order_id)
	# print(carts)
	if carts:
		for cart in carts:
			# # print(checkorder['status'])
			if checkorder['status'] == 'paid':
				cart.is_paid = True
				cart.save()
				User = get_user_model()
				print("hello")
				print(User)
				user_instance = User.objects.get(id=request.user.id)
				order = Orders(userid = user_instance, product_id = cart.product_id, qty = cart.qty, status = "Pending" , address= cart.addresssid)
				order.save()
				product = Product.objects.get(id =order.product_id.id)
				product.qty = product.qty - order.qty
				product.save()
				cart.delete()
			else:
				return HttpResponse("payment failed")
		messages.success(request,'"Thank you for your order! Your order has been placed.')
		return redirect('orders')
	else:
		return HttpResponse("Something went Wrong")
@login_required(login_url="login")
def cancel(request):
	orderid = request.GET.get('orderid')
	order = Orders.objects.get(id=orderid)
	if order.status == 'Delivered':
		order.status = 'Returned'
	else:
		order.status = 'Canceled'
	product = Product.objects.get(id =order.product_id.id)
	product.qty = product.qty + order.qty
	# order.product_id.qty = order.product_id.qty + 
	order.save()
	product.save()
	messages.success(request, "Your order has been successfully cancelled/Returned. If you have any questions, please feel free to contact us. Thank you for shopping with us.")
	return redirect('orders')
	
def RemoveItem(request):
	cartid = request.GET.get('cartid')
	cart = Addtocart.objects.get(id=cartid)
	cart.delete()
	messages.success(request, "Product has been removed from cart!! Add more products to cart")
	return redirect('add-to-cart')

def ChangenoofItem(request):
	changetype= request.GET.get('changetype')
	cartid = request.GET.get('cartid')
	cart = Addtocart.objects.get(id=cartid)
	if changetype == 'Increment':
		cart.qty += 1
	else:
		cart.qty -= 1
	cart.save()
	return redirect(add_to_cart)

def NewsLetter(request):
	to_email = request.GET.get('to_email')
	try:
		mail_subject = 'Subscription Confirmation'
		message = render_to_string('app/newsletter.html')
		email = EmailMessage(mail_subject, message, to=[to_email])
		email.content_subtype = 'html'  # Set the content type to HTML
		email.send()
		print('success')
		messages.success(request, f'Mail sent successfully to {to_email}.')
		return redirect(request.META.get('HTTP_REFERER', '/'))
	except Exception as e:
		print('failed')
		messages.error(request, f'Failed to send email: {e}.')
	return redirect(request.META.get('HTTP_REFERER', '/'))