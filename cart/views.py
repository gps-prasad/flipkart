from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from .models import Cart,CartItem
from store.models import Product

from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

def _cart_id(request):
    cart= request.session.session_key
    if cart==None:
        cart = request.session.create()
    return cart

def cart(request,total=0,quantity=0,cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total=total+(cart_item.product.price*cart_item.quantity)
            quantity = quantity + cart_item.quantity
        tax = (2*total)/100
        grand_total = tax + total            
    except ObjectDoesNotExist:
        pass
    context = {
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'tax':tax,
        'grand_total':grand_total,
    }
            
    return render(request,'cart.html',context)

def remove_cart(request,product_id):
    product=get_object_or_404(Product,id= product_id)
    cart = Cart.objects.get(cart_id = _cart_id)
    cart_item = CartItem.objects.get(cart=cart,product=product)
    if cart_item.quantity>1:
        cart_item.quantity = cart_item.quantity -1
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_item(request,product_id):
    product=get_object_or_404(Product,id= product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(cart=cart,product=product)
    cart_item.delete()
    return redirect('cart')
    

def add_cart(request,product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(product=product,user=current_user)
            cart_item.quantity = cart_item.quantity + 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product,user=current_user,quantity=1)
            cart_item.save()
        return redirect('cart')
    else:
        product = Product.objects.get(id=product_id)
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()       
        try:
            cart_item = CartItem.objects.get(product=product,cart=cart)
            cart_item.quantity = cart_item.quantity + 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product,cart=cart,quantity=1)
            cart_item.save()
        return redirect('cart')


def remove_cart(request,product_id):
    product = get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product,user=request.user)
    else:        
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity>1:
        cart_item.quantity = cart_item.quantity-1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def checkout(request,total=0,quantity=0,cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total=total+(cart_item.product.price*cart_item.quantity)
            quantity = quantity + cart_item.quantity
        tax = (2*total)/100
        grand_total = tax + total            
    except ObjectDoesNotExist:
        pass
    context = {
        'cart_items':cart_items,
        'total':total,
        'quantity':quantity,
        'tax':tax,
        'grand_total':grand_total,
    }
    return render(request,'checkout.html',context)
        
        
    
