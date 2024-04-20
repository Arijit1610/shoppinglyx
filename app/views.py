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
	products = Product.objects.all()
	carts = []

	User = get_user_model()
	if request.user.is_authenticated:
		user_instance = User.objects.get(id=request.user.id)
		carts = Addtocart.objects.filter(userid=user_instance)
	else:
		# Handle the case where the user does not exist
		user_instance = None
	context = {
		"products": products,
		"noofitems" : len(carts)
	}

	return render(request, 'app/home.html', context)

def product_detail(request,productid):
	product = Product.objects.get(id=productid)
	context = {
		"product" : product,
	}
	# print(product.product_type)


	return render(request, 'app/productdetail.html',context)

@login_required(login_url="login")
def add_to_cart(request):
	print(request.user)
	User = get_user_model()
	user_instance = User.objects.get(id=request.user.id)
	carts = Addtocart.objects.filter(userid=user_instance)
	# products = Product.objects.all()
	print(len(carts))
	total = 0
	shiping = 0
	for cart in carts:
		if cart.qty <= cart.product_id.qty:
			total = total + (cart.product_id.discountprice() * cart.qty)
			shiping = shiping + (cart.qty*40)
	alltotal = total+shiping
	context = {
		"items" : carts,
		"total" :total,
		"shiping": shiping,
		"alltotal": alltotal,
		"noofitems" : len(carts)
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
	return HttpResponse("Product added to cart")

def buy_now(request):
	return render(request, 'app/buynow.html')

def profile(request):
	return render(request, 'app/profile.html')

def address(request):
	return render(request, 'app/address.html')

def orders(request):
	# orders = Orders(product_type =  )
	return render(request, 'app/orders.html')

@login_required(login_url="login")
def change_password(request):
	
	return render(request, 'app/changepassword.html')

def mobile(request):
	return render(request, 'app/mobile.html')

def loginpage(request):
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
				messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
				print("login Sucessess")
				return redirect('home')
			except:
				print("block2")
				user = authenticate(
					request, username=username, password=password)
				print("block3")
				print(password)
				print(user.password)
				login(request, user)
				print("newblock")
				messages.success(request, f"Hello <b>{user.username}</b>! You have been logged in")
				print("login Sucessess")
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
					request, "Incorrect Password!!! Please Try Again")
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
			return render(request, 'app/customerregistration.html', {'form': form, 'errors': errors})
			username_error = None
			email_error = None
			password_error = None
			if 'username' in errors:
				username_error = errors['username'][0]
			if 'email' in errors:
				email_error = errors['email'][0]
			if 'password1' in errors or 'password2' in errors:
				password_error = "Password validation failed."
			return render(request, 'app/customerregistration.html', {'form': form, 'username_error': username_error, 'email_error': email_error, 'password_error': password_error})
	else:
		print("elseblock2")
		form = RegistrationForm()
	return render(request, 'app/customerregistration.html',{'form': form})

def checkout(request):
	User = get_user_model()
	user_instance = User.objects.get(id=request.user.id)
	carts = Addtocart.objects.filter(userid=user_instance)
	# products = Product.objects.all()
	print(len(carts))
	total = 0
	shiping = 0
	for cart in carts:
		if cart.qty <= cart.product_id.qty:
			total = total + (cart.product_id.discountprice() * cart.qty)
			shiping = shiping + (cart.qty*40)
	alltotal = total+shiping
	context = {
		"items" : carts,
		"total" :total,
		"shiping": shiping,
		"alltotal": alltotal,
		"noofitems" : len(carts),
		# "user" :user_instance
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
		'items' : items
	}
	
	return render(request, 'app/search_results.html', context)