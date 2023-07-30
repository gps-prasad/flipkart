from django.shortcuts import render,HttpResponse,redirect,get_object_or_404
from .forms import Registrationform, UserProfileForm, UserForm
from .models import Account,UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from cart.models import Cart, CartItem
from orders.models import Order,OrderProduct
from cart.views import _cart_id



# Create your views here.
def Register(request):
    if request.method == "POST":
        form = Registrationform(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.save()
            user_profile = UserProfile.objects.create(user=user)
            user_profile.save()
            user.phone_number = phone_number
            
            
            current_site = get_current_site(request)
            mail_subject = 'Please activate account'
            message = render_to_string('account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()            
            messages.success(request,'Account created successfully!')
            messages.success(request,'Please check your mail we send a user verification link')
            return redirect('register')
        else:
            print('invalid form')
            
    else:
        form = Registrationform()
    context ={
        'form':form,
    }
    return render(request,'register.html',context)


def Login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(email = email,password=password)
        if user is not None:
            try:
                cart =Cart.objects.get(cart_id = _cart_id(request))
                is_cartitem_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cartitem_exists:
                    cartitems = CartItem.objects.filter(cart=cart)
                    for item in cartitems:
                        item.user = user
                        item.save()
            except:
                pass
            auth.login(request,user)
            return redirect('dashboard')
        else:
            messages.error(request,'Invalid credentials')
            return redirect('login')
        
    return render(request,'signin.html')

@login_required(login_url='login')
def Logout(request):
    auth.logout(request)
    messages.success(request,'Logout successfully!')
    return redirect('login')

def Activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(id=uid)
    except (TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations yours account is activated')
    
        return redirect('login')
    else:
        messages.success(request,'Invalid activation link')
        return redirect('register')

@login_required(login_url='login')
def Dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id= request.user.id,is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count':orders_count,
    }
    return render(request,'dashboard.html',context)

@login_required(login_url='login')
def Forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email = email).exists():
            user = Account.objects.filter(email__exact = email).exists()
            current_site = get_current_site(request)
            mail_subject = 'Password reset mail'
            message = render_to_string('account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()            
            messages.success(request,'Password reset email has sent to your mail')
            return redirect('login')
        else:
            messages.error(request,'Invalid mail id')
            return redirect('forgotpassword')
            
    return render(request,'forgotpassword.html')


@login_required(login_url='login')
def Resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(id=uid)
    except (TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.success(request,'This link has been expired')
        return redirect('login')
    
@login_required(login_url='login')
def Resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password==confirm_password:
            uid = request.session['uid']
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset succesful')
        else:
            messages.error(request,'Password dont match')
            return redirect('resetpassword')
    else:
        return render(request,'resetpassword.html')

@login_required(login_url='login') 
def my_orders(request):
    orders = Order.objects.filter(user=request.user.id, is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders,
    }
    return render(request,'my_orders.html',context)

@login_required(login_url='login')        
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST" and userprofile:
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your Profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
    }
    return render(request,'edit_profile.html',context)

@login_required(login_url='login')
def change_password(request):
    if request.method =="POST":
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = Account.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful')
                return redirect('change_password')
            else:
                messages.error(request,"Please enter valid current password")
                return redirect('change_password')
        else:
            messages.error(request,"password does not match")
            return redirect('change_password')
    return render(request,'change_password.html')

@login_required(login_url='login')
def order_details(request,order_id):
    print(order_id)
    order_detail = OrderProduct.objects.filter(order__order_number = order_id)
    order = Order.objects.get(order_number = order_id)
    context = {
        "order_detail" : order_detail,
        'order' : order,
    }    
    
    return render(request,'order_detail.html',context)