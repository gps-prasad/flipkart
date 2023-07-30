from django.shortcuts import render,redirect
from django.http import JsonResponse
from cart.models import CartItem
from .forms import OrderForm
from .models import Payment,Order,OrderProduct
from store.models import Product
import datetime
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url='login')
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count<=0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    total= 0
    quantity = 0
    for cartitem in cart_items:
        total += (cartitem.product.price*cartitem.quantity)
        quantity += cartitem.quantity
    
    tax = (2*total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
        
            yr = int(datetime.date.today().strftime('%y'))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime('%m'))
            yr = 2000
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
        order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
        context={
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':grand_total
        }
        
        return render(request,'payments.html',context)
    return redirect('checkout')


def payments(request):
    print(request.user)
    print('request.user')
    body = json.loads(request.body)
    order = Order.objects.get(user = request.user,is_ordered = False,order_number=body['orderID'])
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    cartitems = CartItem.objects.filter(user = request.user)
    for item in cartitems:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        
        product = Product.objects.get(id=item.product_id)
        product.stock = product.stock - item.quantity
        product.save()
    CartItem.objects.filter(user = request.user).delete()
    mail_subject = 'Thanks for making order'
    message = render_to_string('order_recieve_email.html',{
        'user':request.user,
        'order':order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send() 
    
    data = {
        'order_number': order.order_number,
        'trans_ID': payment.payment_id,
    }
    
    return JsonResponse(data)

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('paymentID')
    print(order_number,transID)
    try:
        order = Order.objects.get(order_number=order_number,is_ordered= True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)
        payment = Payment.objects.get(payment_id = transID)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price*i.quantity 
        context = {
            'order':order,
            'order_number':order.order_number,
            'ordered_products':ordered_products,
            'transID':payment.payment_id,
            'payment':payment,
            'subtotal':subtotal,
        }
        return render(request,'order_complete.html',context)
    except (Order.DoesNotExist):
        return redirect('home')