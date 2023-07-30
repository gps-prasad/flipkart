from django.shortcuts import render,get_object_or_404,HttpResponse,redirect
from category.models import Category
from .models import Product,ReviewRating
from cart.models import CartItem
from cart.views import _cart_id
from .forms import ReviewForm
from orders.models import OrderProduct

from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

# Create your views here.
def store(request,category_slug=None):
    if category_slug==None:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products,4)
        page_number = request.GET.get("page")
        paged_products = paginator.get_page(page_number)
        count = products.count()
    else:
        category=get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=category).order_by('id')
        paginator = Paginator(products,4)
        page_number = request.GET.get("page")
        paged_products = paginator.get_page(page_number)
        count=products.count()
    context={'products':paged_products,'count':count}
    return render(request,'store.html',context)

def product_details(request,category_slug=None,product_slug=None):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:   
        raise e
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user,product_id = single_product.id).exists()
            in_cart = CartItem.objects.filter(user=request.user,product=single_product).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = False
    else:
        orderproduct = False
    reviews = ReviewRating.objects.filter(product_id =single_product, status=True)
    context={
        'orderproduct':orderproduct,
        'single_product':single_product,
        'in_cart':in_cart,
        'reviews':reviews,
    }
    print(single_product.images.url)
    return render(request,'product-detail.html',context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET.get('keyword')
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            count = products.count()
    context={'products':products,'count':count}
    return render(request,'store.html',context)

def submit_review(request,product_id):
    url= request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thanks you! your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                #data.ip = form.cleaned_data['REMOTE_ADDR']
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thanks you! Your review has been updated')
                return redirect(url)
            
            

