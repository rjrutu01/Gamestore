from django.shortcuts import render,HttpResponse,redirect
from gamestopapp.models import product,cart,orders,review
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.core.mail import get_connection,EmailMessage
from django.conf import settings
import random

# Create your views here.
def index(request):
    
        return render(request, 'index.html')
 
def createproduct(request):
    if request.method=='GET':
        return render(request, 'createproduct.html')
    else:
        name=request.POST['name']
        description=request.POST['description']
        manufacturer=request.POST['manufacturer']
        category=request.POST['category']
        price=request.POST['price']
        image=request.FILES['image']
        
        p=product.objects.create(name=name,description=description,manufacturer=manufacturer,category=category,price=price,image=image)
        p.save()
        return redirect('/readproduct')       
    
def readproduct(request):
    if request.method == 'GET':
        p=product.objects.all()
        context={}
        context['data']=p
        return render(request,'readproduct.html',context)
    else:
        name=request.POST['search']
        p=product.objects.get(name=name)
        return redirect(f'read_product_detail/{p.id}')

def delete(request,rid):
    p=product.objects.filter(id=rid)
    p.delete()
    return redirect('/readproduct')

def update(request,rid):
    if request.method=='GET':
        p=product.objects.filter(id=rid)
        context={}
        context['data']=p
        return render(request,'updatedata.html',context)
    else:
        name=request.POST['uname']
        description=request.POST['udescription']
        manufacturer=request.POST['umanufacturer']
        category=request.POST['ucategory']
        price=request.POST['uprice']

        p=product.objects.filter(id=rid)
        p.update(name=name,description=description,manufacturer=manufacturer,category=category,price=price)
        
        return redirect('/readproduct')

def register(request):
    if request.method=='GET':
        return render(request,'register.html')
    else:
        username=request.POST['username']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email=request.POST['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        
        if password==confirm_password:
            u=User.objects.create(username=username,email=email,first_name=first_name,last_name=last_name)
            u.set_password(password)
            u.save()
            return redirect('/login')
        else:
            context={}
            context['error']='password and confirm password does not match'
            return render(request,'register.html',context)

def user_login(request):
    if request.method =='GET':
        return render(request,'login.html')
    else:
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            context={}
            context['error']='Username and password not found'
            return render(request,'login.html',context)
        
def user_logout(request):
    logout(request)
    return redirect('/')

@login_required(login_url='/login')
def create_cart(request,rid):
    prod=product.objects.get(id=rid)
    Cart=cart.objects.filter(product=prod,user=request.user).exists()  #hthis exists method use for check the user and product is true
    if Cart:
        return redirect('/readcart')
    else:
        user=User.objects.get(username=request.user)
        total_price=prod.price
        c=cart.objects.create(user=user,product=prod,total_price=total_price,quantity=1)
        c.save()
        
        return redirect('/login')

@login_required(login_url='/login')
def read_cart(request):
    c=cart.objects.filter(user=request.user)
    context={}
    context['data']=c
    
    total_quantity=0
    total_price=0
    for x in c:
        total_quantity+=x.quantity
        total_price+=x.total_price
    context['total_quantity']=total_quantity
    context['total_price']=total_price
        
    return render(request,'readcart.html',context)

def delete_cart(request,rid):
    Cart=cart.objects.filter(id=rid)
    Cart.delete()
    return redirect('/readcart')

def update_cart(request,rid,q):
    Cart=cart.objects.filter(id=rid)
    c=cart.objects.get(id=rid)
    quantity=int(q)
    price=int(c.product.price) *quantity
    Cart.update(quantity=q,total_price=price)
    return redirect('/readcart')

def create_orders(request,rid):
    Cart=cart.objects.get(id=rid)
    order=orders.objects.create(product=Cart.product,user=request.user,quantity=Cart.quantity,total_price=Cart.total_price)
    order.save()
    Cart.delete()
    return redirect('/readorder')

def read_order(request):
    order=orders.objects.filter(user=request.user)
    context={}
    context['data']=order
    return render(request,'readorder.html',context)

def create_review(request,rid):
    prod=product.objects.get(id=rid)
    rev=review.objects.filter(user=request.user,product=prod).exists()
    if rev:
        return HttpResponse('review already exist')
    else:
        if request.method =='GET':
            return render(request,'createreview.html')
        else:
            title=request.POST['title']
            content=request.POST['content']
            rating=request.POST['rate']
            image=request.FILES['image']
            
            p=product.objects.get(id=rid)
            Review=review.objects.create(product=p,title=title,content=content,rating=rating,image=image,user=request.user)
            Review.save()
            
            return HttpResponse('Review Added')
        
def read_product_detail(request,rid):
    prod=product.objects.filter(id=rid)
    p=product.objects.get(id=rid)
    n=review.objects.filter(product=p).count()
    rev=review.objects.filter(product=p)
    sum=0
    for x in rev:
        sum+=x.rating
    
    try:
        avg=int(sum/n)
        avg_r=sum/n
    except:
        print('No review')
        
    context={}
    context['data']=prod
    if n==0:
        context['avg']='No review'
    else:
        context['avg_rating']=avg
        context['avg']=avg_r
    return render(request,'readproductdetail.html',context)
        
        
def forget_password(request):
    if request.method=='GET':
        return render(request,'forgetpassword.html')
    else:
        email=request.POST['email']
        request.session['email']=email
        user=User.objects.filter(email = email).exists()
        if user:
            otp=random.randint(1000,9999)
            request.session['otp']=otp
            with get_connection(
                host =settings.EMAIL_HOST,
                port =settings.EMAIL_PORT,
                username =settings.EMAIL_HOST_USER,
                password =settings.EMAIL_HOST_PASSWORD,
                use_tls =settings.EMAIL_USE_TLS
                
            ) as connection:
                subject ="OTP Verificaton"
                email_from=settings.EMAIL_HOST_USER
                recipient_list=[email]
                message = f"OTP is {otp}"
                
                EmailMessage(subject,message,email_from,recipient_list,connection=connection).send()
            
            return redirect('/otp_verification')
        else:
            context={}
            context['error']='User does not exist'
            return render(request,'forgetpassword.html',context)
    
def otp_verification(request):
    if request.method=='GET':
        return render(request,'otp.html')
    else:
        otp=int(request.POST['otp'])
        email_otp=int(request.session['otp'])
        
        if otp == email_otp:
            return redirect('/new_password')
        else:
            return HttpResponse('not ok')
        
def new_password(request):
    if request.method == "GET":
        return render(request,'new_password.html')
    else:
        email=request.session['email']
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        user=User.objects.get(email=email)
        if password == confirm_password:
            user.set_password(password)
            user.save()
            return redirect('/login')
        else:
            context={}
            context['error']='Password and confirm password does not match'
            return render(request,'new_password.html',context)
        

    

        