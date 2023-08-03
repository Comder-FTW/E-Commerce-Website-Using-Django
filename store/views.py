from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from .models import *
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
import json
def store(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}
		cartItems=order['get_cart_items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)

def cart(request):
	
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}
		cartItems=order['get_cart_items']


	context = {'items':items, 'order':order,'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		#Create empty cart for now for non-logged in user
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0}
		cartItems=order['get_cart_items']

	context = {'items':items, 'order':order,'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)
	
	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):

	data = json.loads(request.body)
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		total = float(data['shipping']['total'])

		if total == order.get_cart_total:
			order.complete = True
		order.save()

		ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
			)

	return JsonResponse("Payment complete", safe=False)
	

def registerPage(request):
	form = CreateUserForm()
	

	if request.method == "POST":
		form = CreateUserForm (request.POST)
		if form.is_valid():
			
			u = form.save()
			customer, created = Customer.objects.get_or_create(user=u)
			customer.name = form.cleaned_data.get('username')
			customer.email = form.cleaned_data.get('email')
			
			customer.save()
			u.save()
			user = form.cleaned_data.get('username')
			
			messages.success(request, 'Account was created for '+user)
			return redirect('login')

	context = {'form':form}
	return render(request, 'store/register.html',context)

def loginPage(request):

	if request.method == 'POST':
		username = request.POST.get("username")
		password = request.POST.get("password")
		user = authenticate(username = username, password= password)

		if user is not None:
			login(request, user)
			return redirect('store')
		else:
			messages.info(request, "username or password is incorrect!")

	context = {}
	return render(request,'store/login.html',context)

def logoutUser(request):
	logout(request)
	return redirect('store')