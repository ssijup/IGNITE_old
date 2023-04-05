from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect
from .models import Userdetails,Products,Category,Cart,Wishlist,Useraddress,Coupon,BannerVedio,Order,GENDER_CHOICE,PAYMENT_METHOD_CHOICES,STATUS_CHOICES,Payment,Subcategory,Variants,Variantoptions,Productimages
from django.contrib.auth import authenticate,login,logout
from django.core.files.storage import FileSystemStorage
from django.views.decorators.cache import cache_control,never_cache
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.contrib import messages
import requests, random
from django.urls import reverse
import os
from django.db.models import Min,Max
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.cache import cache
import razorpay
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import csv
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
import json



# Create your views here.



@csrf_exempt
def search(request):
    if request.method == 'POST':
        query = request.POST.get('search')
        results = Products.objects.filter(name__icontains=query)
        data = {'results': [{'name': r.name, 'description': r.description} for r in results]}
        return JsonResponse(data)
    return render(request, 'search.html')

def view_404_error(request,exception):
    return render(request,'404_error.html')



def venue_csv(resquest):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="venue.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Product', 'Address', 'Payment Type', 'Order Status', 'Order Date'])

    venues = Order.objects.all()
    for venue in venues:
        writer.writerow([str(venue.name), venue.product.book_title, str(venue.address.street_address), str(venue.payment_type), str(venue.order_status), str(venue.order_date)])
    return response




def venue_pdf(request):
    if request.method=='POST':
        startdate= request.POST.get('startdate')
        enddate= request.POST.get('enddate')
        if enddate =='' and startdate =='':
            venues=Order.objects.all()
        elif startdate > enddate:
            error_date='The start date cannot be greater than the end date .Please choose the right date'
            return render(request,'admin_pdfdate.html',{'error_date':error_date})

            
        else:
            venues=Order.objects.filter(order_date__range=(startdate,enddate))

        # buf = io.BytesIO()
        # 
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter)


        data = []
        data.append(['Name', 'Product', 'Address', 'Payment Type', 'Order Status', 'Order Date'])
        for venue in venues:
            data.append([str(venue.name),
            venue.product.book_title,
            (str(venue.address.street_address)),
            (str(venue.payment_type)),
            (str(venue.order_status)),
            (str(venue.order_date))
            ])
            table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 14),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))

        elements = []
        elements.append(table)
        doc.build(elements)
        buf.seek(0)

        return FileResponse(buf,as_attachment=True, filename='venue.pdf')
    return render(request,'admin_pdfdate.html')



#user  siginup validation-
def user_signupvalidation(upassword1):
    if len(upassword1)<8:
        error="Password must be at least 8 characters long..."
        return error
    return None

def email_validation(uemail):
    validator=EmailValidator()
    try:
        validator(uemail)
        return None
    except ValidationError:
        email_error="Invalid email address.Please re enter......" 
        return email_error
    
def username_validation(uname):
    if uname == '':
        username_error='Please enter your  name'
        return username_error
    return None


def admin_updateuser(request):
    if request.method == 'POST':
        id=request.GET['uid']
        uname = request.POST.get('user_name')
        validate_username=username_validation(uname)
        if validate_username:
            return render(request,'admin_updateuser.html',{'validate_username' : validate_username})
        uemail = request.POST.get('user_email')
        upassword1 = request.POST.get('user_password1')
        upassword2 = request.POST.get('user_password2')
        if upassword1 != upassword2:
            error='Password mismaching'
            return render(request,'admin_updateuser.html',{'error' : error})
        else:
            Userdetails.objects.filter(id=id).update( 
                user_name = uname,
                user_email = uemail,
                user_password = upassword1
            )
            return redirect('admin_userlist')
    return render(request,'admin_updateuser.html')


#********USER REGIDTRATION***************************************
@cache_control(no_cache=True)
def user_signup(request):
    if 'num_verified' in request.session:
        del request.session['num_verified']     
        phone_number=request.session['u_phnum']
        ugender=request.session['ugender']
        uname=request.session['uname']
        uemail=request.session['uemail']
        upassword1=request.session['upassword1']

        my_user = Userdetails.objects.create(phone_number=phone_number,gender=ugender,user_name=uname,user_email=uemail,user_password=upassword1)
        my_user.save()
        # del().request.session['num_verified']
        
        return redirect('user_login')

    
    if request.method == 'POST':
        phone_number=request.POST.get('phone_number')
        # if request.POST.get('ugender')=="":
        #     user_nameerror="All fields to be filled...."
        #     return render(request,'user_signup.html',{'user_nameerror':user_nameerror})
        ugender=request.POST.get('ugender')
        # if request.POST.get('user_name')=='':
        #     user_nameerror="All fields to be filled...."
        #     return render(request,'user_signup.html',{'user_nameerror':user_nameerror})
        uname = request.POST.get('user_name')
        uemail = request.POST.get('user_email')
        if Userdetails.objects.filter(user_email=uemail).exists() :
            emailvalidation=("The email {} already Exits.Try another one.".format(uemail))
            return render(request,'user_signup.html',{'emailvalidation':emailvalidation})
        upassword1 = request.POST.get('user_password1')
        upassword2 = request.POST.get('user_password2')
        if upassword1 != upassword2:
            return HttpResponse('retype the password')
        else:
            # error_userpassword=user_signupvalidation(upassword1)
            # if error_userpassword:
            #     return render(request,'user_signup.html',{'error_userpassword':error_userpassword})
            # emailvalidation=email_validation(uemail)
            # if emailvalidation:
            #     return render(request,'user_signup.html',{'emailvalidation':emailvalidation})      
            
            request.session['u_phnum']=phone_number
            request.session['ugender']=ugender
            request.session['uname']=uname
            request.session['uemail']=uemail
            request.session['upassword1']=upassword1
            
            return redirect('otp_login')

            # my_user = Userdetails.objects.create(phone_number=phone_number,gender=ugender,user_name=uname,user_email=uemail,user_password=upassword1)
            # my_user.save()
            return redirect('user_login')
    else:
        print('not post')
        gender=GENDER_CHOICE

        return render(request,'user_signup.html',{'gender':gender})



######  admin   dashboard #####################################
def admin_dashboard(request):
    chart_prod=Variantoptions.objects.all()
    context={

        'chart_prod':chart_prod
    }
    return render(request,'admin_chart.html',context)




#*****USER LOGIN**********************************************************
@cache_control(no_cache=True)
def user_login(request):
    if 'user_email' in request.session:
        return redirect('index_3_home')
    
    if request.method == "POST":
        print('HHHHHHHHHHHHHHHHHHHHHHHHHHHHOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO  ')
        uemail=request.POST.get('user_email')
        if uemail == '' or len(uemail)<3:
            user_nameerror="Enter Username...."
            # return render(request,'user_login.html',{'user_nameerror':user_nameerror})
            return JsonResponse({'user_nameerror':user_nameerror})
            # return JsonResponse({'success': False, 'message': 'Invalid email or password.'})

        uemail=request.POST['user_email']
        upassword=request.POST['user_password']
        password_error=user_signupvalidation(upassword)
        if password_error:
            return JsonResponse({'password_error':password_error})
            
        try:
            user=Userdetails.objects.filter(user_email=uemail,user_password=upassword).first()
        except Userdetails.DoesNotExist:
            user=None
        if user is not None:
            if user.u_active:
                request.session['user_session'] = uemail        
                request.session['user_email'] = request.session['user_session']
                print('ttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt')
                return JsonResponse({'index_3_home':'index_3_home'})
            # otp_login
            else:
                u_blocked =' You are blocked !!!!!!!!!'
                return render(request,'user_login.html',{'u_blocked': u_blocked})
        else:
            return JsonResponse({'password_or_uname_error':'Invaild user name or password'})
            #return HttpResponse('PASSWORD INCORRECT')
    return render(request,'user_login.html')





def otp_login(request):
    print("!!!inside")
    global otp_sent
    global use
    if request.method=='POST':
        otp_rec = int(request.POST.get('c_otp'))
        if otp_rec==otp_sent:
            # request.session['user_email'] = request.session['user_session']
            request.session['num_verified']=otp_rec
            messages.success(request,"Login  Successfully Complete ")
            return redirect('user_signup')
        else:
            messages.warning(request, 'Incorrect OTP')
            return render(request,'otp_login.html')
    else:
        signup_user_num=request.session['u_phnum']
        print(signup_user_num)
        num = signup_user_num
        print(num,'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
        otp_sent = random.randint(1001, 9999)
       
        url = 'https://www.fast2sms.com/dev/bulkV2'
        payload = f'sender_id=TXTIND&message={otp_sent}&route=v3&language=english&numbers={num}'
        headers = {
            'authorization': "xoiObB7WLa4GvY0uPZ6J9KmS1kXQCA2MeRhpzfTHN5sy8dctVDo5mkyeX9CRJxBKzu8M7FZ0stfh2gdi",
            'Content-Type': "application/x-www-form-urlencoded"
            }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text) 
        print("Sent value::",otp_sent)
    return render(request,'otp_login.html')




def otp_login_inor(request):
    if request.method == 'POST':
        u_num=request.POST.get('u_num')
        print(u_num)
        print('ok')
        u_num_verification=Userdetails.objects.filter(phone_number=u_num).first()
        print(u_num_verification,'ok')
        if u_num_verification is not None:
            user_obj_ses=u_num_verification.user_email
            print(user_obj_ses)
            print('koiiii')
            
           
            # signup_user_num=request.session['u_phnum']
            print(u_num)
            num = u_num
            print(num,'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
            otp_sent = random.randint(1001, 9999)
            
            url = 'https://www.fast2sms.com/dev/bulkV2'
            payload = f'sender_id=TXTIND&message={otp_sent}&route=v3&language=english&numbers={num}'
            headers = {
                'authorization': "xoiObB7WLa4GvY0uPZ6J9KmS1kXQCA2MeRhpzfTHN5sy8dctVDo5mkyeX9CRJxBKzu8M7FZ0stfh2gdi",
                'Content-Type': "application/x-www-form-urlencoded"
                }
            response = requests.request("POST", url, data=payload, headers=headers)
            print(response.text) 
            print("Sent value::",otp_sent)
            request.session['user_sess_exchange']=user_obj_ses       
            request.session['login_otp']=otp_sent
        #     return render(request,'otp_login.html')
        # else:
        #     print('oooooooooo')
            
            return redirect('user_otp_check')
        print('hiiddddddddddddddddoo')
    return redirect('user_login')

def user_otp_check(request):
    print("!!!inside")
    global otp_sent
    global use
    otp_sent=request.session['login_otp']
    if request.method=='POST':
        otp_rec = int(request.POST.get('c_otp'))
        if otp_rec==otp_sent:
            user_obj_ses=request.session['user_sess_exchange']
            request.session['user_email'] = user_obj_ses
            # request.session['num_verified']=otp_rec
            messages.success(request,"Login  Successfully Completeted ")
            return redirect('index_3_home')
        else:
            messages.warning(request, 'Incorrect OTP')
            return render(request,'otp_login.html')
    return render(request,'otp_login.html')







#   222222222222    ORIGINAL OTP LOGIN   222222222
# def otp_login(request):
#     print("!!!inside")
#     global otp_sent
#     global use
#     if request.method=='POST':
#         otp_rec = int(request.POST.get('c_otp'))
#         if otp_rec==otp_sent:
#             request.session['user_email'] = request.session['user_session']
#             messages.success(request,"Login Completed Successfully")
#             return redirect('   ')
#         else:
#             messages.warning(request, 'Incorrect OTP')
#             return render(request,'otp_login.html')
#     else:
#         num = '7306286447'
#         otp_sent = random.randint(1001, 9999)
#         # use = request.session['user_session']
#         # #obj = Userdetails.objects.get(user_name=use)
#         # url = 'https://www.fast2sms.com/dev/bulkV2'
#         # payload = f'sender_id=TXTIND&message={otp_sent}&route=v3&language=english&numbers={num}'
#         # headers = {
#         #     'authorization': "xoiObB7WLa4GvY0uPZ6J9KmS1kXQCA2MeRhpzfTHN5sy8dctVDo5mkyeX9CRJxBKzu8M7FZ0stfh2gdi",
#         #     'Content-Type': "application/x-www-form-urlencoded"
#         #     }
#         # response = requests.request("POST", url, data=payload, headers=headers)
#         # print(response.text) 
#         print("Sent value::",otp_sent)
#     return render(request,'otp_login.html')
    







def user_logout(request):
    if 'user_email' in request.session:
        del request.session['user_email']
    return redirect('user_login')



@cache_control(no_cache=True)
def admin_login(request):
    error_msg = None
    if 'name' in request.session:
        return redirect('admin_dashboard')
    if request.method == 'POST':
            name = request.POST.get('name')
            password = request.POST.get('password')
            user = authenticate(request,username =name, password=password)
            if user is not None:
                request.session['name'] = name
                return redirect('admin_dashboard')
            else:
                error_msg = 'invalid Name or password..!'
    return render(request, 'admin_login.html', {'error': error_msg})


def user_manageaccount(request):
    if 'user_email' in request.session:
        user=request.session['user_email']
        user_obj=Userdetails.objects.filter(user_email=user).first()
        order_obj=len(Order.objects.filter(name=user_obj))
        contex= {
            'order_obj':order_obj,
            'user_obj':user_obj

                }
        return render(request,'user_manageaccount.html',contex)
    return redirect('user_login')


def user_addressbook(request):
    return render(request,'user_addessbook.html')






def user_profile(request):
    user=request.session['user_email']
    print(user,'ooooooooooooooooooooooooooooooooooooooooooo')
    uprofile=Userdetails.objects.filter(user_email=user).first()
    order_obj=len(Order.objects.filter(name=uprofile))

    contex= {

        'uprofile':uprofile,
        'order_obj':order_obj

            }
    return render(request,'user_profile.html',contex)


def user_editprofile(request):
    if request.method == "POST":
        u_name=request.POST.get('uname')
        # u_email=request.POST.get('u_email')
        u_gender=request.POST.get('u_gender')
        user=request.session['user_email']
        Userdetails.objects.filter(user_email=user).update(user_name=u_name,gender=u_gender)
        return redirect('user_profile')
    
    user=request.session['user_email']
    uprofile=Userdetails.objects.filter(user_email=user).first()
    print(uprofile.gender,'llllllllllllllllllllllllllllllllllllllllllllllllll')
    gender=GENDER_CHOICE
    contex= {
        'uprofile':uprofile,
        'gender':gender
            }
    return render(request,'user_editprofile.html',contex)



@cache_control(no_cache=True)
def admin_logout(request):
    if 'name' in request.session:
        del request.session['name']
        return redirect('admin_login')

        



@cache_control(no_cache=True)
def admin_logout(request):
        logout(request)
        return redirect('admin_login')



#@cache_control(no_cache=True)
def admin_userlist(request):
    #if request.user.is_authenticated:
    if request.method=='POST':
        pro_search=request.POST.get('Search')
        userlist=Userdetails.objects.filter(user_name=pro_search)
        return render(request,'admin_userlist.html',{'tablelist' : userlist})
    else:
        userlist = Userdetails.objects.all().order_by('id')
        paginator = Paginator(userlist,4)
        page = request.GET.get('page')
        try:
            userlist=paginator.page(page)
        except PageNotAnInteger:
            userlist = paginator.page(1)
        except EmptyPage:
            userlist = paginator.page(paginator.num_pages)
            
        return render(request,'admin_userlist.html',{'tablelist' : userlist,'page' : page})
    #return redirect('admin_login')


#


# @cache_control(no_cache=True)
# def admin_productssssslist(request):
#     if request.method=='post':
#         pro_search=request.POST.get('Search')
#         list=Products.objects.filter(book_title=pro_search)
#         if search_result is not None:
#             return render(request,'admin_productslist.html')
#     else:
#         return



# @cache_control(no_cache=True)
# def admin_addproducts(request):
#         if request.method == 'POST' :
#             book_title = request.POST.get('book_title')
#             author = request.POST.get('author')
#             stock=request.POST.get('product_stock')
#             # image = request.FILES.get('myfile')
#             # print(image,'sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss')
#             description = request.POST.get('description')
#             p_category = request.POST.get('category')
#             price = request.POST.get('price')
#             category = Category.objects.filter(cate_name=p_category).first()
#             #
#             pro_add=Products(
#                 book_title=book_title,
#                 author=author,
#                 product_stock=stock,
#                 # image=image,
#                 description=description,
#                 price=price,
#                 p_category=category
#             )
#             pro_add.save()
#                 #Products.objects.create(book_title=book_title,author=author,image=image,description=description,price=price,p_category=category)    
#             return redirect('admin_productslist')
#         else:
#             pr_cate=Category.objects.all()
#             return render(request,'admin_addproducts.html',{'pr_cate' : pr_cate})




#@cache_control(no_cache=True)
# def admin_productslist(request):
#     #if 'email' in request.session:
#     if request.method=='POST':
#         pro_search=request.POST.get('Search')
#         list=Products.objects.filter(book_title__icontains=pro_search).order_by(id)
#         return render(request,'admin_productslist.html',{'list' : list,'pro_search':pro_search})
#     else :
#         list =Products.objects.all()
#         paginator = Paginator(list,5)
#         page = request.GET.get('page')
#         try:
#             list=paginator.page(page)
#         except PageNotAnInteger:
#             list = paginator.page(1)
#         except EmptyPage:
#             list = paginator.page(paginator.num_pages)

#     return render(request,'admin_productslist.html',{'list' : list, 'page' : page})

        

def admin_deleteproduct(request):
    uid = request.GET['uid']
    del_pro = Products.objects.filter(id = uid)
    print(uid)
    del_pro.delete()
    return redirect('admin_productslist')




@cache_control(no_cache=True)
def shop_list_left_books(request): 
    list = Products.objects.all()
    varop_obj=Variantoptions.objects.all()
    print('ogogggggg')
    for i in varop_obj:
        if i.voption_prod_key.p_category.catewise_dicount_price:
            after_dis_amt=i.price - i.voption_prod_key.p_category.catewise_dicount_price
            uid=i.id
            print(i.discount_price,'before')
            Variantoptions.objects.filter(id=uid).update(discount_price=after_dis_amt)
            print(uid,'gggggggggggggggggggggggggggggggggggggggggggggggg')
            print(i.discount_price)
            # Variantoptions(pro_dict_price_by_cvate=after_dis_amt)


            
    print("!!Three")
    paginator = Paginator(list,4)
    page = request.GET.get('page')
    try:
        list=paginator.page(page)
    except PageNotAnInteger:
        list = paginator.page(1)
    except EmptyPage:
        list = paginator.page(paginator.num_pages)
    amount=0
    shipping_charge=40
    
    user=request.session['user_email']
    cartmini_user=Userdetails.objects.filter(user_email=user).first()
    cartmini_usersort=Cart.objects.filter(user=cartmini_user)
    cate_filter=Category.objects.all()
    minmax_price=Variantoptions.objects.aggregate(Min('price'),Max('price'))
    cart=len(Cart.objects.filter(user = cartmini_user)) 
    cart_len = Cart.objects.filter(user = cartmini_user)
    total_price = sum([i.subtotal for i in cart_len])
    subcate=Subcategory.objects.all()
    amount=total_price-40
    if cart>0:
        cart_len='good'
    else:
        cart_len=None
    
    context={ 
        'subcate':subcate,
        'cart_len':cart_len,
        'cart':cart,
        'list' : list,
        'minmax_price' : minmax_price,
        "cartmini_usersort":cartmini_usersort,
        'page':page,
        'cate_filter':cate_filter,
        "total_price":total_price
        }
    print('hasooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
    return render(request,'shop-list-left-books.html',context)


def filter_by_subcategory(request):

    sub_catname=request.GET.get('cate_proname')
    print(sub_catname,'uuuuuu')
    subcate_obj=Subcategory.objects.get(subcategory_name=sub_catname)
    filtered_prod=Products.objects.filter(p_subcategory_for=subcate_obj)
    product_list = []
    for product in filtered_prod:
        product_list.append({       
            'id': product.id,
            'book_title': product.book_title,
            'description': product.description,
            'image': str(product.image),
            'p_category':product.p_category.cate_name,
            'p_subcategory':product.p_subcategory_for.subcategory_name,


            
        })
        price={
        "price":product.get_variantoption_price()
        }
        product_list[-1].update(price)

        id_var={
        "id_var":product.get_variantoption_id()
        }
        product_list[-1].update(id_var)

        dis_price={
        "dis_price":product.get_variantoption_discount_by_cateprice()
        }
        product_list[-1].update(dis_price)
        print('00000000',dis_price)

        
    return JsonResponse(product_list,safe=False)




def filter_bycategory(request):
    cate_proname=request.GET.get('cate_proname')
    filtered_products_cate=Category.objects.get(cate_name=cate_proname)
    filtered_prod=Products.objects.filter(p_category=filtered_products_cate)
    product_list = []
    for product in filtered_prod:
        product_list.append({       
            'id': product.id,
            'book_title': product.book_title,
            'description': product.description,
            'image': str(product.image),
            'p_category':product.p_category.cate_name,
            'p_subcategory':product.p_subcategory_for.subcategory_name,
            
        })
        price={
        "price":product.get_variantoption_price()
        }
        product_list[-1].update(price)

        id_var={
        "id_var":product.get_variantoption_id()
        }
        product_list[-1].update(id_var)

        dis_price={
        "dis_price":product.get_variantoption_discount_by_cateprice()
        }
        product_list[-1].update(dis_price)
        print('00000000',dis_price)

        
    return JsonResponse(product_list,safe=False)






def filter_products_byprice(request):
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        print(min_price,'nnMINPONNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')
        print(max_price,'nnMAXPONNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')

        varop_obj = Variantoptions.objects.filter(price__gte=min_price, price__lte=max_price)
        print(varop_obj.first().price,'new')
        # prod_invarop=Variantoptions.objects.filter(voption_prod_key=varop_obj)
        productList = []

        for product in varop_obj:
            productList.append({       
                'id': product.voption_prod_key.id,
                'var_id':product.id,
                'book_title': product.voption_prod_key.book_title,
                'description': product.voption_prod_key.description,
                'image': str(product.voption_prod_key.image),
                'p_category':product.voption_prod_key.p_category.cate_name,
                'price':product.price,
                'dis_price':product.discount_price,
                'save_price':product.voption_prod_key.p_category.catewise_dicount_price,
                'p_subcategory':product.voption_prod_key.p_subcategory_for.subcategory_name,     
            })
            # price={
            # "price":product.get_variantoption_price()
            # }
            # product_list[-1].update(price)

        # data = {
        #     'products': list(varop_obj.values())
        # }
        return JsonResponse(productList,safe=False)

# def filter_bycategory(request):
#     fil_cat=request.GET.get('fil_cat')
#     cate_filter=Category.objects.get(cate_name=fil_cat)
#     list=Products.objects.filter(p_category=cate_filter)
#     return render(request,'shop-list-left-books.html',{'list':list})
    




@cache_control(no_cache=True)
def product_details(request):
    print('vvbgggggggggggggggggggggggggggggggg')
    uid=request.GET.get('uid')
    product_obj =Products.objects.get(id = uid)
    mul_img=Productimages.objects.filter(prod_img_key=product_obj)
    variantopt_obj=Variantoptions.objects.filter(voption_prod_key=product_obj)
    prod_variant_option_price=variantopt_obj.first().price
    prod_variant_option_dis_price=variantopt_obj.first().discount_price
    prod_variant_option_dis_id=variantopt_obj.first().id
    print(prod_variant_option_dis_id,'oo')


    prod_bot_dis=Products.objects.all().order_by('-id')[:10]
    return render(request,'product_details.html',{'prod_variant_option_dis_id':prod_variant_option_dis_id,'prod_bot_dis':prod_bot_dis,'prod_variant_option_dis_price':prod_variant_option_dis_price,'mul_img':mul_img,'list' : product_obj,'variantopt_obj':variantopt_obj,'prod_variant_option_price':prod_variant_option_price})



@cache_control(no_cache=True)
def index_3_home(request):
    if 'user_email' in request.session:
        ban=BannerVedio.objects.all()
        pro_obj=Products.objects.all()[:6]
        cate_obj=Category.objects.all()
        order_prod=Order.objects.all()[:8]
        pro_objs=Products.objects.all().order_by('-id')

        context={
            'pro_objs':pro_objs, 
            'order_prod':order_prod,
            'cate_obj':cate_obj,
            'pro_obj':pro_obj,
            'ban':ban
        }
        
        return render(request,"index_3_home.html",context)
    return redirect('user_login')




def admin_addcategory(request):
    if request.method == 'POST':
        if request.POST.get('category') == "":
            cate_nameerror="Enter a Category...."
            return render(request,'admin_addcategory.html',{'cate_nameerror':cate_nameerror})

        add_category = request.POST.get('category')
        if Category.objects.filter(cate_name__iexact=add_category).exists() :
            cate_nameerror="Category Already Exits...."
            return render(request,'admin_addcategory.html',{'cate_nameerror':cate_nameerror})
        Category.objects.create(cate_name = add_category)
        return redirect('admin_categorylist')
    pr_cate = Category.objects.all()
    return render(request,'admin_addcategory.html',{'pr_cate' : pr_cate})




def admin_editcategory(request):
    if request.method =='POST':
        uid =request.GET['uid']
        category = request.POST.get('category')
        category_offer = request.POST.get('category_offer')


        if category == "":
            error='Please enter category'
            return render(request,'admin_editcategory.html',{'error':error})
        if category_offer== "":
            category_offer= None
        Category.objects.filter(id=uid).update(cate_name=category,catewise_dicount_price=category_offer)
        return redirect('admin_categorylist')
    else:
        uid =request.GET['uid']
        cate=Category.objects.filter(id=uid)
        return render(request,'admin_editcategory.html',{'cate':cate})




def admin_deletecategory(request):
    uid =request.GET['uid']
    cat_del = Category.objects.filter(id=uid)
    cat_del.delete()
    return redirect('admin_categorylist')





def admin_categorylist(request):
    p_cate = Category.objects.all()
    return render(request,'admin_categorylist.html',{'p_cate' : p_cate})


def admin_addcategory_discount(request):
    uid=request.GET.get('uid')
    if request.method == 'POST':
        off_price=request.POST.get('off_price')
        uid=request.GET.get('uid')
        Category.objects.filter(id=uid).update(catewise_dicount_price=off_price)
        return redirect('admin_categorylist')
    
    cat_obj=Category.objects.filter(id=uid).first()
    return render(request,'admin_addcategory_discount.html',{'cat_obj':cat_obj})


def userblock(request):
    print("!!!!Inside")
    uid = request.GET['uid']
    should_block = Userdetails.objects.filter(id=uid)
    for i in should_block:
        if i.u_active:
            Userdetails.objects.filter(id = uid).update(u_active = False)
        else:
             Userdetails.objects.filter(id = uid).update(u_active = True)
    return redirect('admin_userlist')



def admin_updateuser(request):
    if request.method == 'POST':
        id=request.GET['uid']
        uname = request.POST.get('user_name')
        validate_username=username_validation(uname)
        if validate_username:
            return render(request,'admin_updateuser.html',{'validate_username' : validate_username})
        uemail = request.POST.get('user_email')
        upassword1 = request.POST.get('user_password1')
        upassword2 = request.POST.get('user_password2')
        if upassword1 != upassword2:
            error='Password mismaching'
            return render(request,'admin_updateuser.html',{'error' : error})
        else:
            Userdetails.objects.filter(id=id).update( 
                user_name = uname,
                user_email = uemail,
                user_password = upassword1
            )
            return redirect('admin_userlist')
    return render(request,'admin_updateuser.html')


# def admin_editproducts(request):

#     if request.method == 'POST':
#         uid = request.GET['uid']
#         uid_pro=Products.objects.get(id=uid)
#         if len(request.FILES) !=0:
#             if len(uid_pro.image) >0:
#                 os.remove(uid_pro.image.path)
#             image = request.FILES.get('myfile')
#         book_title = request.POST.get('book_title')
#         author = request.POST.get('author')
#         description = request.POST.get('description')
#         p_category = request.POST.get('category')
#         price = request.POST.get('price')
#         category = Category.objects.filter(cate_name=p_category).first()
#         Products.objects.filter(id=uid).update(
#             book_title = book_title,
#             author = author,
#             description = description,
#             price =price,
#             image = image,
#             p_category =category
#         )
#         return redirect('admin_productslist')
#     else:
#         pro_id=request.GET['uid']
#         pro_serch=Products.objects.filter(id=pro_id)
#         p_cate = Category.objects.all()
#         return render(request,'admin_editproducts.html',{'p_cate' : p_cate, 'pro_serch' : pro_serch})




def admin_editproducts(request):
    if 'editprod_id' in request.session:
        
        uid=request.session['editprod_id']
        print(uid,'lllllllllllllllllllllll')
    else:
        uid = request.GET['uid']
    uid_pro=Products.objects.get(id=uid)
    if request.method == 'POST':
        if 'editprod_id' in request.session:
            uid=request.session['editprod_id']
        else:
            uid = request.GET['uid']
        uid_pro=Products.objects.get(id=uid)
        imagee = request.FILES.get('myfile')
        #if len(request.FILproductsES) !=0:
        
        
        uid_pro.book_title = request.POST.get('book_title')
        uid_pro.description = request.POST.get('description')
        c = request.POST.get('category')
        cat_obj=Category.objects.filter(cate_name=c).first()
        print(c,cat_obj,'555555555555pppppppppppppppppppppp')
        uid_pro.p_category=cat_obj

        oo= request.POST.get('product_subcategory')
        sub_obj=Subcategory.objects.filter(subcategory_name=oo).first()
        print(oo,'hhhhhhhhhhhhhhhhhhhhhhhhhh')
        uid_pro.p_subcategory_for=sub_obj





        # p_cate = Category.objects.filter(cate_name=uid_pro.p_category.cate_name).first()

        if len(imagee) !=0:
            if len(uid_pro.image) >0:
                print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
                os.remove(uid_pro.image.path)
            uid_pro.image = request.FILES.get('myfile')
        uid_pro.save()
        uid=request.session['editprod_id']
        print(uid,'lllllllllllllllllllllll')
        # del request.session['editprod_id']
        # uidd=request.session['editprod_id']
        print(uid,'2lllllllllllllllllllllll')
        return redirect('admin_productslist')
    
    if 'editprod_id' in request.session:
        uid=request.session['editprod_id']
    else:
        uid = request.GET['uid']
    pro_serch=Products.objects.get(id=uid)
    multi_img=Productimages.objects.filter(prod_img_key=pro_serch)
    categor=Category.objects.all()
    prod_cat=pro_serch.p_category.cate_name
    subcate=Subcategory.objects.all()
    variant=Variants.objects.all()
    variant_option=Variantoptions.objects.filter(voption_prod_key=uid_pro)
    variant_option_prod=uid_pro.p_variant_for
    

    context={
        'prod_cat':prod_cat,
        'multi_img':multi_img,
        'variant_option_prod':variant_option_prod,
        'pro_serch' : pro_serch,
        'categor':categor,
        'subcate':subcate,
        'variant':variant,
        'variant_option':variant_option,

    }
    request.session['editprod_id']=uid
    return render(request,'admin_editproducts.html', context)



def admin_editproduct_variantoptions(request):
    uid=request.GET.get('uid')
    if request.method == "POST":
        prod_obj=Variantoptions.objects.filter(id=uid)
        voption_name=request.POST.get('variantoption_name')
        voption_price=request.POST.get("variantoption_price")
        voption_stock=request.POST.get('variantoption_stock')
        voption_unit=request.POST.get('variantoption_unit')
        prod_obj.update(unit=voption_unit,variantoption_name=voption_name,price=voption_price,product_stock=voption_stock)
        return redirect('admin_editproducts')
    
    var_pp=Variantoptions.objects.get(id=uid)
    print(var_pp,'popopopopopopopopo')
    # var_pp=Variantoptions.objects.filter(id=uid)
    var_all=Variants.objects.all()
    return render(request,'admin_editproduct_variantoptions.html',{"var_pp":var_pp,'var_all':var_all})



def admin_deleteproduct_variantoptions(request):
    uid=request.GET.get('uid')
    var_obj=Variantoptions.objects.get(id=uid)
    var_obj.delete()
    return redirect('admin_editproducts')
#----------------CART----------------------------------#



def create_cart(request):
    user = request.session['user_email']
    variant_option_id =request.GET.get('variant_option_id')
    pro_id = request.GET.get('uid')
    
    cart_pro = Products.objects.get(id=pro_id)
    variant_option_obj=Variantoptions.objects.filter(voption_prod_key=cart_pro)
    vartant_obj=variant_option_obj.get(id=variant_option_id)
    #vartant_obj=Variantoptions.objects.get(id=variant_option_id)

    cart_user = Userdetails.objects.get(user_email = user )
    if vartant_obj.product_stock == 0 or vartant_obj.product_stock<0 :
            msg='The Product is out of stock'
            messages.success(request,msg)
            print('ooooooooggggggtttthhhh')
            return redirect('shop_list_left_books')
    try:
        userprod_cart=Cart.objects.filter(user=cart_user)
    except Cart.DoesNotExist:
        userprod_cart=Cart.objects.create(user=cart_user,product=cart_pro,c_product_vatiantoption_key=vartant_obj,quantity=1)
        vartant_obj.product_stock-=1
        Variantoptions.objects.filter(id=variant_option_id).update(product_stock=vartant_obj.product_stock)


    try:
        user_pro=Cart.objects.get(product=cart_pro,user=cart_user,c_product_vatiantoption_key=vartant_obj)
    except Cart.DoesNotExist:
        user_pro=None
    if user_pro is None:
        Cart.objects.create(user=cart_user,product=cart_pro,c_product_vatiantoption_key=vartant_obj,quantity=1)
        vartant_obj.product_stock-=1
        Variantoptions.objects.filter(id=variant_option_id).update(product_stock=vartant_obj.product_stock)

    else:
    #     if vartant_obj.product_stock == 0 or vartant_obj.product_stock<0 :
    #         messages.success(request,'The Product is out of stock')
    #         return redirect('shop_list_left_books')
           
        user_pro.quantity+=1
        Cart.objects.filter(product=cart_pro,c_product_vatiantoption_key=vartant_obj).update(quantity=user_pro.quantity)
        vartant_obj.product_stock-=1
        try:
            variant_option_obj=Variantoptions.objects.filter(id=variant_option_id).update(product_stock=vartant_obj.product_stock)
        except IntegrityError:
            for i in variant_option_obj:
                var_pro=i.variantoption_name
                print(var_pro,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
            msg='The Product "{}" is out of stock'.format(var_pro)
            messages.success(request,msg,'The Product is out of stock')
            return redirect('cart_table')
            
    return redirect('cart_table')
        


    #userproduct_idcheck=Products.objects.get(id=pro_id)
    #ry:
        #userproduct_idcheck_incart=Cart.objects.get(product=userproduct_idcheck)
        #print(userproduct_idcheck_incart,'gggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg')
    #except Cart.DoesNotExist:
        #userproduct_idcheck_incart=None
    # if user_pro is None:
    #     cart_user = Userdetails.objects.get(user_email = user )
    #     cart_pro = Products.objects.get(id=pro_id)
    #     Cart.objects.create(product = cart_pro,user = cart_user)
    #     return redirect('shop_list_left_books')
    # else:
    #     cart_user = Userdetails.objects.get(user_email = user )
    #     Cart.objects.get(user=cart_user)
    #     #cart_pro = Products.objects.get(id=pro_id)
        # cart_incrementquantity=Cart.objects.get(product=userproduct_idcheck)
    
        
        


def cart_table(request):
    amount=0
    shippingcharge=40
    loginuser = request.session['user_email']
    user1 = Userdetails.objects.get(user_email = loginuser )
    cart = Cart.objects.filter(user = user1)
    cart_len = len(Cart.objects.filter(user = user1))
    if cart_len >0:
        pass
    else:
        cart_len=None

    cart_len = len(Cart.objects.filter(user = user1))
    total_price = sum([i.subtotal for i in cart])
    amount=total_price-40
    

    # for i in cart:
    #     value= i.quantity*i.product.p_variantoption_for.price
    #     amount=value+amount
    # totalamount=amount+shippingcharge    'totalamount':totalamount
    return render(request,'cart_table.html',{"amount":amount,'cart':cart,'total_price':total_price,'cart_len':cart_len,})


def clear_cart(request):
    user=request.session['user_email']
    user_obj=Userdetails.objects.filter(user_email=user).first()
    user_cart=Cart.objects.filter(user=user_obj)
    user_cart.delete()
    return redirect('shop_list_left_books')


def pluscart(request):
    if request.method == "GET":
        prod_id=request.GET['prod_id']
        login_user = request.session['user_email']
        logged_user=Userdetails.objects.filter(user_email=login_user).first()
        obj_id=Variantoptions.objects.get(id=prod_id)
        c=Cart.objects.get(Q(c_product_vatiantoption_key=obj_id) & Q(user=logged_user))
        
        if obj_id.product_stock <1:
            prod_name=obj_id.voption_prod_key.book_title
            data={
                'prod_name':'stock limited',
                'disp':'Out of stock'
            }
            quantity_increment_del=c.quantity
            request.session['quantity_increment_del']=quantity_increment_del
            return JsonResponse(data)
        else:
            c.quantity+=1
            c.save()

            obj_id.product_stock-=1
            
            print(obj_id.product_stock,'oooooooooooooooo')

            Variantoptions.objects.filter(id=prod_id).update(product_stock=obj_id.product_stock)
            loginuser = request.session['user_email']
            loged_user=Userdetails.objects.filter(user_email=loginuser).first()
            cart=Cart.objects.filter(user=loged_user)
            for i in cart:
                totalamount = sum([i.subtotal for i in cart])
            amount=totalamount-40
        
            data={
                
                "quantity":c.quantity,
                "amount":amount,
                "totalamount":totalamount,
            }
            quantity_increment_del=c.quantity
            request.session['quantity_increment_del']=quantity_increment_del
            return JsonResponse(data)
    



# product details plus
def product_pluscart(request):
    if request.method == "GET":
        prod_id=request.GET['prod_id']
        login_user = request.session['user_email']
        logged_user=Userdetails.objects.filter(user_email=login_user).first()
        obj_id=Variantoptions.objects.get(id=prod_id)
        c=Cart.objects.get(Q(c_product_vatiantoption_key=obj_id) & Q(user=logged_user))
        
        if obj_id.product_stock <1:
            prod_name=obj_id.voption_prod_key.book_title
            data={
                'prod_name':'stock limited',
                'disp':'Out of stock'
            }
            quantity_increment_del=c.quantity
            request.session['quantity_increment_del']=quantity_increment_del
            return JsonResponse(data)
        else:
            c.quantity+=1
            c.save()

            obj_id.product_stock-=1
            
            print(obj_id.product_stock,'oooooooooooooooo')

            Variantoptions.objects.filter(id=prod_id).update(product_stock=obj_id.product_stock)
            loginuser = request.session['user_email']
            loged_user=Userdetails.objects.filter(user_email=loginuser).first()
            
        
            data={
                
                "quantity":c.quantity,
            }
            return JsonResponse(data)


# products details minus 
def product_minuscart(request):
    if request.method == "GET":
        prod_id=request.GET['prod_id']
        print(prod_id,'jkljkl')
        login_user = request.session['user_email']
        logged_user=Userdetails.objects.filter(user_email=login_user).first()
        obj_id=Variantoptions.objects.get(id=prod_id)
        c=Cart.objects.get(Q(c_product_vatiantoption_key=obj_id) & Q(user=logged_user))
        c.quantity-=1
        if c.quantity<1:
            obj_id.product_stock+=1
            Variantoptions.objects.filter(id=prod_id).update(product_stock=obj_id.product_stock)
            print('hhhhhhhh')
            # c.delete()
            data = {
                'removed': True,
            }
        # if c.quantity<1:
        #     pass
        # else:
        else:
            print(c.quantity,'ppppppppppppppkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
            c.save()  

            obj_id.product_stock+=1
            # print(obj_id.product_stock,'oooooooooooooooo')
            Variantoptions.objects.filter(id=prod_id).update(product_stock=obj_id.product_stock)
            loginuser = request.session['user_email']
            loged_user=Userdetails.objects.filter(user_email=loginuser).first()
            cart=Cart.objects.filter(user=loged_user)
            shippingcharge=40
            amount=0
            for i in cart:
                value= i.quantity*i.c_product_vatiantoption_key.price
                amount=value+amount
            totalamount=amount+shippingcharge
            data={
                "quantity":c.quantity,
                "amount":amount,
                "totalamount":totalamount,
            }
        
        
        return JsonResponse(data)






def minuscart(request):
    if request.method == "GET":
        prod_id=request.GET['prod_id']
        print(prod_id,'jkljkl')
        login_user = request.session['user_email']
        logged_user=Userdetails.objects.filter(user_email=login_user).first()
        obj_id=Variantoptions.objects.get(id=prod_id)
        c=Cart.objects.get(Q(c_product_vatiantoption_key=obj_id) & Q(user=logged_user))
        c.quantity-=1
        if c.quantity<1:
            obj_id.product_stock+=1
            Variantoptions.objects.filter(id=prod_id).update(product_stock=obj_id.product_stock)
            print('hhhhhhhh')
            c.delete()
            data = {
                'removed': True,
            }
        # if c.quantity<1:
        #     pass
        # else:
        else:
            print(c.quantity,'ppppppppppppppkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
            c.save()  

            obj_id.product_stock+=1
            # print(obj_id.product_stock,'oooooooooooooooo')
            Variantoptions.objects.filter(id=prod_id).update(product_stock=obj_id.product_stock)
            loginuser = request.session['user_email']
            loged_user=Userdetails.objects.filter(user_email=loginuser).first()
            cart=Cart.objects.filter(user=loged_user)
            shippingcharge=40
            amount=0
            for i in cart:
                value= i.quantity*i.c_product_vatiantoption_key.price
                amount=value+amount
            totalamount=amount+shippingcharge
            data={
                "quantity":c.quantity,
                "amount":amount,
                "totalamount":totalamount,
            }
        
        
        return JsonResponse(data)




def cart_deleteproduct(request):
    user=request.session['user_email']
    user_obj=Userdetails.objects.filter(user_email=user).first()
    uid=request.GET['uid']
    cart_obj=Cart.objects.filter(user=user_obj)
    delcart_id = cart_obj.get(id=uid)
    restock=delcart_id.c_product_vatiantoption_key.product_stock
    quan=delcart_id.quantity
    variant_stock=delcart_id.c_product_vatiantoption_key
    variant_stock.product_stock+=quan
    variant_stock.save()


    
    # del_stock=request.session['quantity_increment_del']
    # delcart_id.del_stock
    print(restock,'stock')
    print(delcart_id,'id')
    delcart_id.delete()
    return redirect('cart_table')
    
   
    

    #---------USER ADDRESS------------------------------------------------


# def address_checkout(request):
#     ad_user = request.session['user_email']
#     filter_user=Userdetails.objects.get(user_email = ad_user)
#     adresslist_user = Useraddress.objects.filter(mainuser = filter_user )
#     return render(request,'address_checkout.html',locals())


def adress_validation(self,adress_validationn):
    if self.name ==''  :
        error_name="Please fill the field"
        return error_name
    else:
        return None

def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name =='' or len(name)<3 :
            error="Please enter a name and should be more than three letters"
            return render(request,'add_address.html',{'error':error})
    
        mobnumber = request.POST.get('mobnumber')
        if mobnumber =='' or len(mobnumber)<9  :
            error_mob="Please enter a valid number to contact you "
            return render(request,'add_address.html',{'error_mob':error_mob})
        street_address = request.POST.get('street_address')
        if street_address =='' or len(street_address)<4:
            error_ad="Please enter your street address"
            return render(request,'add_address.html',{'error_ad':error_ad})
        city =  request.POST.get('city')
        if city =='' or len(city)<3 :
            error_city="Please enter your city"
            return render(request,'add_address.html',{'error_city':error_city})
        state = request.POST.get('state')
        if state =='' or len(state)<2 :
            error_state="Please enter your State"
            return render(request,'add_address.html',{'error_state':error_state})
        landmark =  request .POST.get('landmark')
        if landmark ==''  :
            error_mark="Please enter a landmark"
            return render(request,'add_address.html',{'error_mark':error_mark})
        pincode = request.POST.get('pincode')
        if pincode =='' or len(pincode)!=6  :
            pincode_error="Please enter a valid pincode "
            return render(request,'add_address.html',{'pincode_error':pincode_error})
        ad_user = request.session['user_email']

        filterad_user =Userdetails.objects.get(user_email = ad_user)
        Useraddress.objects.create(
            mainuser = filterad_user,
            name = name,
            mobnumber = mobnumber,
            street_address = street_address,
            city = city,
            state = state,
            landmark = landmark,
            pincode = pincode,
        )
        return redirect('address_checkout')
    return render(request,'add_address.html')


# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def address_checkout(request):
    if request.method=='POST':
        iid=request.POST.get('adressRadios')
        loginuser = request.session['user_email']
        #user_addressship=Useraddress.objects.get(id=user_addressid)
        #user1 = Userdetails.objects.get(user_email = loginuser )
        # summmary_pro = Cart.objects.filter(user = user1)
        # amount=0
        # shipping_charge=40
        # for i in summmary_pro:
        #     value=i.product.p_variantoption_for.price*i.quantity
        #     amount= value+amount
        # total_amount=amount+shipping_charge
        # global val
        # def val():
        #     return  iid
        request.session['address_id']=iid

        #return render(request,'checkout_summary.html',{'summmary_pro':summmary_pro,'total_amount':total_amount,'user_addressship':user_addressship})
        #url=reverse('checkout_summary',args=[iid])
        return redirect('checkout_summary')
    else:
        ad_user = request.session['user_email']
        filter_user=Userdetails.objects.get(user_email = ad_user)
        adresslist_user = Useraddress.objects.filter(mainuser = filter_user )
        return render(request,'address_checkout.html',locals())



# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def checkout_summary(request):
        # iid=val()
        # total_amount=0
        iid=request.session['address_id']
        user_address=Useraddress.objects.get(id=iid)
        loginuser = request.session['user_email']
        address_id=request.GET.get('address_id')
        user1 = Userdetails.objects.get(user_email = loginuser )
        summmary_pro = Cart.objects.filter(user = user1)
        for i in summmary_pro:
            total_amount=sum([i.subtotal for i in summmary_pro ])
        # total_amount=total_amount
       
        try:
            razorpay_amount=int(total_amount)*100
        except UnboundLocalError :
            return redirect('shop_list_left_books')
       
        payment_methods=PAYMENT_METHOD_CHOICES
        try:
            coupon_obj=Coupon.objects.filter(coupon_minmun_amount__lte=total_amount).first()
            dis_amt=coupon_obj.coupon_dis_amount

        except:
            coupon_obj=None
        if request.method=='POST':
            coupon_name=request.POST.get('coupon_name')
            cou_ex=Coupon.objects.filter(coupon_name=coupon_name).first()
            if cou_ex is not None :
                dis_amt= cou_ex.coupon_dis_amount            
                total_amount=total_amount-dis_amt
                razorpay_amount=int(total_amount)*100
                cou_applied='Coupon Applied Sucessfully'
                return render(request,'checkout_summary.html',{'dis_amt':dis_amt,'cou_applied':cou_applied,'coupon_obj':coupon_obj,'razorpay_amount':razorpay_amount,'total_amount':total_amount,'payment_methods':payment_methods,'summmary_pro':summmary_pro,'user_address':user_address})
            if cou_ex is None:
                coup_error='Invalid Coupon'
                return render(request,'checkout_summary.html',{'coup_error':coup_error,'coupon_obj':coupon_obj,'razorpay_amount':razorpay_amount,'total_amount':total_amount,'payment_methods':payment_methods,'summmary_pro':summmary_pro,'user_address':user_address})
           
        return render(request,'checkout_summary.html',{'coupon_obj':coupon_obj,'razorpay_amount':razorpay_amount,'total_amount':total_amount,'payment_methods':payment_methods,'summmary_pro':summmary_pro,'user_address':user_address})




def coupon_dis_total(request):
    pass







# def checkout_summary(request):
#     user_addressid=request.POST.get('adressRadios')
#     user_addressidd=request.GET.get('uid')
#     loginuser = request.session['user_email']
#     user1 = Userdetails.objects.get(user_email = loginuser )
#     summmary_pro = Cart.objects.filter(user = user1)
#     print(user_addressid,'iddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd')
#     print(user_addressidd,'iddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd')

#     amount=0
#     shipping_charge=40
#     for i in summmary_pro:
#         value=i.product.p_variantoption_for.price*i.quantity
#         amount= value+amount
#     total_amount=amount+shipping_charge

#     return render(request,'checkout_summary.html',{'summmary_pro':summmary_pro,'total_amount':total_amount})



#ooooooooooooooooooooooouser    ORIGINAL ORDERRRRRRRRRRRRLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def place_order(request):
#     # if cache.get('place_order'):
#     #     return redirect('shop_list_left_books')
    
#     # else:
#         iid=val()
#         cache.set('test_key', 'test_value')
#         print(cache.get('test_key'))    
#         user_login=request.session['user_email']        
#         ordered_user=Userdetails.objects.get(user_email=user_login)
#         usercart_product=Cart.objects.filter(user=ordered_user)
#         selected_address= Useraddress.objects.get(id=iid)  
#         for i in usercart_product:
#             Order.objects.create(
#                 name=ordered_user,
#                 product=i.product,
#                 address=selected_address,
#             )
#             del_cart=Cart.objects.all()
#             del_cart.delete()

#         # cache.set('place_order',True)

#         response= redirect('order_thanku')
#         response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
#         response['Pragma'] = 'no-cache'
#         response['Expires'] = '0'
#         return response




@never_cache
def place_order(request): 
    if request.method=="POST" :  
        # iid=val()
        iid=request.session['address_id']

        
        user_login=request.session['user_email']    
        totalamount=request.GET.get('amount') 
        ordered_user=Userdetails.objects.get(user_email=user_login)
        usercart_product=Cart.objects.filter(user=ordered_user)
        selected_address= Useraddress.objects.get(id=iid) 

        # 'user_login':user_login,'totalamount':totalamount,'ordered_user':ordered_user,

        #payment_amount=request.POST.get('payment_amount')
        payment_method=request.POST.get('payment_method')
        # order_pay_details=Payment.objects.filter(id ='1')
        # order_pay_details.payment_status = True

        if payment_method == 'Cash on Delivery':
            order_pay_details=Payment.objects.create(
                payment_user=ordered_user,
                payment_amount=totalamount,
                payment_method=payment_method,
            )
            order_pay_details.payment_status=True
            order_pay_details.save()

        elif payment_method == 'PayPal':
            order_pay_details=Payment.objects.create(
                payment_user=ordered_user,
                payment_amount=totalamount,
                payment_method=payment_method,
                payment_status=True
            )
            
           
        elif payment_method=='Razor Pay':
                razorpay_amount=int(totalamount)*100
                return render(request,'razorpay_payment.html',{'razorpay_amount':razorpay_amount,'payment_method':payment_method})
                
                
        try:
            if order_pay_details.payment_status==True:
                print(order_pay_details.payment_status,'sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss')
                for i in usercart_product:
                    order=Order.objects.create(

                        name=ordered_user,
                        product=i.product,
                        address=selected_address,
                        payment_type=payment_method,
                         # order_status=True,
                        order_payment_key=order_pay_details,
                        ordered_product_quantity=i.quantity,
                        
                        ordered_product_price=i.c_product_vatiantoption_key.price

                    )
                    if i.product.p_category.catewise_dicount_price:
                        uid=i.product.id
                        # Order.objects.filter(order=order,product__id=uid).update(ordered_product_price=i.c_product_vatiantoption_key.discount_price)
                        order.ordered_product_price=i.c_product_vatiantoption_key.discount_price
                        order.save()
                    del_cart=Cart.objects.all()
                    del_cart.delete()

                return redirect('order_thanku')
        except UnboundLocalError:  
            return redirect('checkout_summary')
    return redirect('checkout_summary')

@never_cache          
def razorpay_payment(request):

    # iid=val()
    iid=request.session['address_id']
    user_login=request.session['user_email'] 
    ordered_user=Userdetails.objects.get(user_email=user_login)
    usercart_product=Cart.objects.filter(user=ordered_user)
    selected_address= Useraddress.objects.get(id=iid) 
    for i in usercart_product:
        total_amount=sum([i.subtotal for i in usercart_product ])
        total_amount=total_amount
        razorpay_amount=int(total_amount)*100   
    
    #payment_method=request.POST.get('payment_method')
    payment_method='Razor Pay'
    print(payment_method,'llllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll')
   
    #totalamount=request.GET.get('amount') 
    
    #razorpay_amount=int(totalamount)*100
    client = razorpay.Client(auth=("rzp_test_RRhMTrJphOc3D7", "cUn8l52mELGhaXlORvWpzADe"))
    DATA = {
        "amount": total_amount ,
        "currency": "INR",
        "receipt": "receipt#1",
        "notes": {
            "key1": "value3",
            "key2": "value2"
        }
    }

    razorpay_response=client.order.create(data=DATA)
    print(razorpay_response,'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT')
    # 
    # 
    # {'id': 'order_LQBQJ5LWCQZ2eG', 'entity': 'order', 'amount': 29900,
    #  'amount_paid': 0, 'amount_due': 29900, 'currency': 'INR', 'receipt': 'receipt#1',
    #  'offer_id': None, 'c': 'created', 'attempts': 0, 'notes': {'key1': 'value3', 'key2': 'value2'},
    #  'created_at': 1678530292}
    reazorpay_status=razorpay_response['status']
    if reazorpay_status == 'created':
        print('razorpay created ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
        order_pay_details=Payment.objects.create(
            payment_user=ordered_user,
            payment_amount=total_amount,
            payment_method=payment_method,
            payment_status=True
        )
        try:
            if order_pay_details.payment_status==True:
                print(order_pay_details.payment_status,'sssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss')
                for i in usercart_product:
                    order=Order.objects.create(

                        name=ordered_user,
                        product=i.product,
                        address=selected_address,
                        payment_type=payment_method,
                        # order_status=True,
                        order_payment_key=order_pay_details,
                        ordered_product_quantity=i.quantity,
                        ordered_product_price=i.c_product_vatiantoption_key.price

                    )
                    if i.product.p_category.catewise_dicount_price:
                        uid=i.product.id
                        # Order.objects.filter(order=order,product__id=uid).update(ordered_product_price=i.c_product_vatiantoption_key.discount_price)
                        order.ordered_product_price=i.c_product_vatiantoption_key.discount_price
                        order.save()
                    del_cart=Cart.objects.all()
                    del_cart.delete()

                return redirect('order_thanku')
        except UnboundLocalError:
            return redirect('checkout_summary')
    return redirect('checkout_summary')



def user_order(request):
    user_login=request.session['user_email']
    ordered_user=Userdetails.objects.get(user_email=user_login)
    uoders=Order.objects.filter(name=ordered_user)
    len_order=len(Order.objects.filter(name=ordered_user))
    cart_len = len(Cart.objects.filter(user = ordered_user))
    return render(request,'user_order.html',{'ordered_user':ordered_user,'uoders':uoders,'len_order':len_order,'cart_len':cart_len})
    
#`cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def order_thanku(request):
    return render(request,'order_thanku.html')


def admin_orderlist(request):
    adorders=Order.objects.all().order_by("id")
    return render(request,'admin_orderlist.html',{'adorders':adorders})


def admin_updateorderstatus(request):
    if request.method == "POST":
        uid=request.GET.get('uid')
        order_stat=request.POST.get('order_stat')
        Order.objects.filter(id=uid).update(order_status=order_stat)
        return redirect('admin_orderlist')
    order_status={'statuschoice':STATUS_CHOICES}
    return render(request,'admin_updateorderstatus.html',order_status)

    

def user_cancellation(request):
    uid=request.GET.get('uid')
    if request.method == 'POST':
        order_stat='Order Cancelled'
        Order.objects.filter(id=uid).update(order_status=order_stat)
        messages.success(request,'Order Cancelled Sucessfully....')
        return redirect('user_order')
    ucancel_id=request.GET.get('uid')
    print(ucancel_id,'hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
    user_cancellingorder=Order.objects.filter(id=ucancel_id)
    user=request.session['user_email']
    user_obj=Userdetails.objects.get(user_email=user)
    order_len=len(Order.objects.filter(name=user_obj))
    
    return render(request,'user_cancellation.html',{'user_obj':user_obj,'order_len':order_len,'user_cancellingorder':user_cancellingorder})


def user_returnproduct(request):
    uid=request.GET.get('uid')
    if request.method=='POST':
        order_stat='Return'
        Order.objects.filter(id=uid).update(order_status=order_stat)
        messages.success(request,'Return Sucessfully....')
        return redirect('user_order')
    return_id=request.GET.get('uid')
    print(return_id,'hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
    user_returningorder=Order.objects.filter(id=return_id)
    user=request.session['user_email']
    user_obj=Userdetails.objects.get(user_email=user)
    order_len=len(Order.objects.filter(name=user_obj))
    return render(request,'user_returnproduct.html',{'user_obj':user_obj,'order_len':order_len,'user_returningorder':user_returningorder})



def filter_byprice(request):
    minmax_price=Products.objects.aggregate(Min('price'),Max('price'))
    print(minmax_price,'ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd')
    return render(request,'user_cancellation.html',{'minmax_price':minmax_price})
    
def admin_chart(request):
    chart_prod=Variantoptions.objects.all()
    context={

        'chart_prod':chart_prod
    }
    return render(request,'admin_chart.html',context)



def admin_subcategorylist(request):
    subcate=Subcategory.objects.all()

    return render(request,'admin_subcategorylist.html',{'subcate':subcate})

def admin_addsubcategory(request):
    uid=request.GET.get('uid')
    if request.method == 'POST':
        cate_obj=Category.objects.get(id=uid)
        sub_cate=request.POST.get('sub_cate')
        Subcategory.objects.create(subcategory_name=sub_cate,sub_catefor=cate_obj)
        return redirect('admin_subcategorylist')
    cate_obj=Category.objects.filter(id=uid)
    return render(request,'admin_addsubcategory.html',{'cate_obj':cate_obj})
    


def admin_variantlist(request):
    varient=Variants.objects.all()
    variant_option=Variantoptions.objects.all()
    return render(request,'admin_variantlist.html',{'varient':varient,'variant_option':variant_option})


def admin_addvarient(request):
    uid=request.GET.get('uid')
    if request.method == "POST":
        varient=request.POST.get('varient')
        if varient == '' :
            error_v='Please enter a variant'
            sub_cate=Subcategory.objects.filter(id=uid)
            return render(request,'admin_addvariant.html',{'error_v':error_v,'sub_cate':sub_cate})
        Variants.objects.create(varient_name=varient)
        return redirect('admin_variantlist')
    sub_cate=Subcategory.objects.filter(id=uid)
    return render(request,'admin_addvariant.html',{'sub_cate':sub_cate})

def admin_editvariant(request):
    uid=request.GET.get('uid')
    if request.method == 'POST':
        vart=request.POST.get('variant_name')
        Variants.objects.filter(id=uid).update(varient_name=vart)
        return redirect('admin_variantlist')
    var_objj=Variants.objects.get(id=uid)
    return render(request,'admin_editvariant.html',{'var_objj':var_objj})


def admin_deletevariant(request):
    uid=request.GET.get('uid')
    var_objj=Variants.objects.get(id=uid)
    var_objj.delete()
    return redirect('admin_variantlist')



def admin_variantoptionlist(request):
    varient=Variants.objects.all()
    categor=Category.objects.all()
    subcate=Subcategory.objects.all()
    variant_list=Variants.objects.all()
    variant_option=Variantoptions.objects.all()
    context={
        'varient':varient,
        'categor':categor,
        'subcate':subcate,
        'variant_list':variant_list,
        'variant_option':variant_option,

    }
    return render(request,'admin_variantoptionlist.html',context)

def admin_delete_variantoption(request):
    uid=request.GET.get('uid')
    variant_option=Variantoptions.objects.get(id=uid)
    variant_option.delete()
    return redirect('admin_variantoptionlist')



#@@@@@@@@@@@@@@@@@@@@@@@@@ ORIGINAL
# def admin_addvariantoptions(request):
#     uid=request.GET.get('uid')
#     if request.method == 'POST':
#         varient_obj=Variants.objects.get(id=uid)
#         variantoption_name=request.POST.get('variantoption_name')
#         variantoption_stock=request.POST.get('variantoption_stock')
#         variantoption_price=request.POST.get('variantoption_price')
#         Variantoptions.objects.create(variantoption_for=varient_obj,variantoption_name=variantoption_name,price=variantoption_price,product_stock=variantoption_stock)
#         return redirect('admin_variantoptionlist')
#     varient=Variants.objects.filter(id=uid)
#     return render(request,'admin_addvariantoptions.html',{'varient':varient})


###################        ORIGINAL                @@@@@@@@@@@@@@@@@@@@@@@@@@@@
# def admin_addproducts(request):
#     if request.method == "POST":
#         product_name=request.POST.get('product_name')
#         product_description=request.POST.get('product_description')
#         product_image=request.FILES.get('product_image')
#         product_category=request.POST.get('product_category')
#         product_subcategory=request.POST.get('product_subcategory')
#         product_variant=request.POST.get('product_variant')
#         product_variantoption=request.POST.getlist('product_variantoption')
#         print(product_variantoption,'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')


#         prod_cate=Category.objects.get(cate_name=product_category)
#         prod_subcate=Subcategory.objects.get(subcategory_name=product_subcategory)
#         prod_variant=Variants.objects.get(varient_name=product_variant)
#         #prod_variantoption=Variantoptions.objects.filter(variantoption_name__in=product_variantoption)
        
#         product_obj=Products.objects.create(
#             book_title=product_name,
#             description=product_description,
#             image=product_image,
#             p_category=prod_cate,
#             p_subcategory_for=prod_subcate,
#             p_variant_for=prod_variant,
#         )
        
#         # for i in product_variantoption:
            
#         #     variant_obj=Variantoptions.objects.get(variantoption_name=i)
#         #     print(variant_obj,'ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
#         #     # for i in variant_obj:
#         #     #     variant_objoption=Variantoptions.objects.filter(variantoption_name__in=i)
#         #     #product_obj.p_variantoption_for.add(variant_obj)
#         #     # product_obj.save()
#         #     product_obj.p_variantoption_for=variant_obj
#         #     product_obj.p_variantoption_for.save()
#         return redirect('admin_productslist')
    
#     categor=Category.objects.all()
#     subcate=Subcategory.objects.all()
#     variant=Variants.objects.all()
#     variant_option=Variantoptions.objects.all()
#     context={
#         'categor':categor,
#         'subcate':subcate,
#         'variant':variant,
#         'variant_option':variant_option,

#     }
#     return render(request,'admin_addproducts.html',context)



#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    original      @@@@@@@@@@@@@@@@@@@@@@@@@@@
# def admin_productslist(request):
#     #if 'email' in request.session:
#     if request.method=='POST':
#         pro_search=request.POST.get('Search')
#         list=Products.objects.filter(book_title__icontains=pro_search)
#         return render(request,'admin_productslist.html',{'list' : list,'pro_search':pro_search})
#     else :
#         list =Products.objects.all()
#         #variant_opt=list.p_variantoption_for.all()
#         paginator = Paginator(list,5)
#         page = request.GET.get('page')
#         try:
#             list=paginator.page(page)
#         except PageNotAnInteger:
#             list = paginator.page(1)
#         except EmptyPage:
#             list = paginator.page(paginator.num_pages)

#     return render(request,'admin_productslist.html',{'list' : list, 'page' : page})





def admin_productslist(request):
    #if 'email' in request.session:
    if 'editprod_id' in request.session:
        del request.session['editprod_id']
    if request.method=='POST':
        pro_search=request.POST.get('Search')
        list=Products.objects.filter(book_title__icontains=pro_search)
        return render(request,'admin_productslist.html',{'list' : list,'pro_search':pro_search})
    else :
        list =Products.objects.all()
        #variant_opt=list.p_variantoption_for.all()
        paginator = Paginator(list,5)
        page = request.GET.get('page')
        try:
            list=paginator.page(page)
        except PageNotAnInteger:
            list = paginator.page(1)
        except EmptyPage:
            list = paginator.page(paginator.num_pages)

    return render(request,'admin_productslist.html',{'list' : list, 'page' : page})


def admin_addmultiple_image(request):
    prod_id=request.GET.get("prod_id")
    if request.method =="POST":
        prod_id=request.GET.get("prod_id")
        multi_imge=request.FILES.getlist('multi_imge')
        print(multi_imge,'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
        prod_id=request.GET.get("prod_id")
        prod_obj=Products.objects.get(id=prod_id)
        print('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        for i in multi_imge:
            print('kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
            Productimages.objects.create(

                prod_img_key=prod_obj,
                multiple_image=i,
                )
        return redirect('admin_editproducts')
    return render(request,'admin_addmultiple_image.html')


def admin_editmultiple_image(request):
    uid = request.GET.get('uid')
    if request.method=="POST":
        multi_imge_obj=Productimages.objects.get(id=uid)

        mul_img_obj=request.FILES.get('mul_img_obj')
        if len(mul_img_obj) !=0:
            if len(multi_imge_obj.multiple_image) >0:
                os.remove(multi_imge_obj.multiple_image.path)
            multi_imge_obj.multiple_image = request.FILES.get('mul_img_obj')
            multi_imge_obj.save()
        return redirect('admin_editproducts')
    multi_imge_obj=Productimages.objects.get(id=uid)   
    return render(request,'admin_editmultiple_image.html',{'multi_imge_obj':multi_imge_obj})


def admin_delete_multipleimage(request):
    uid=request.GET.get('uid')
    mulimg=Productimages.objects.get(id=uid)
    mulimg.delete()
    return redirect('admin_editproducts')





def admin_addproducts(request):
    if request.method == "POST":
        product_name=request.POST.get('product_name')
        product_description=request.POST.get('product_description')
        product_image=request.FILES.get('product_image')
        product_category=request.POST.get('product_category')
        product_subcategory=request.POST.get('product_subcategory')
        # product_variant=request.POST.get('product_variant')
        # product_variantoption=request.POST.getlist('product_variantoption')
        # print(product_variantoption,'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')


        prod_cate=Category.objects.get(cate_name=product_category)
        prod_subcate=Subcategory.objects.get(subcategory_name=product_subcategory)
        #prod_variant=Variants.objects.get(varient_name=product_variant)
        #prod_variantoption=Variantoptions.objects.filter(variantoption_name__in=product_variantoption)
        
        product_obj=Products.objects.create(
            book_title=product_name,
            description=product_description,
            image=product_image,
            p_category=prod_cate,
            p_subcategory_for=prod_subcate,
            #p_variant_for=prod_variant,
        )
        
        # for i in product_variantoption:
            
        #     variant_obj=Variantoptions.objects.get(variantoption_name=i)
        #     print(variant_obj,'ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')
        #     # for i in variant_obj:
        #     #     variant_objoption=Variantoptions.objects.filter(variantoption_name__in=i)
        #     #product_obj.p_variantoption_for.add(variant_obj)
        #     # product_obj.save()
        #     product_obj.p_variantoption_for=variant_obj
        #     product_obj.p_variantoption_for.save()
        return redirect('admin_productslist')
    
    categor=Category.objects.all()
    subcate=Subcategory.objects.all()
   
    context={
        'categor':categor,
        'subcate':subcate,
        #'variant':variant,
        #'variant_option':variant_option,
    }
    return render(request,'admin_addproducts.html',context)


def admin_addvariantoptions(request):
    variant=Variants.objects.all()
    uid = request.GET.get('uid')
    prod_varoption=Products.objects.get(id =uid)
    if request.method== 'POST':
        uid = request.GET.get('uid')
        prod_varoption=Products.objects.get(id =uid)
        varop_unit=request.POST .get('variantoption_unit')
        coressponding_variant_name=request.POST.get('product_variant')
        if coressponding_variant_name == '' :
            error_vo='Please select a variant'
            return render(request,'admin_addvariantoptions.html',{'error_vo':error_vo,'prod_varoption':prod_varoption,'variant':variant})
        
        var_obj=Variants.objects.get(varient_name=coressponding_variant_name)
        variantoption_name=request.POST.get('variantoption_name')
        if variantoption_name == '' :
            error_von='Please enter  a Name'
            return render(request,'admin_addvariantoptions.html',{'error_von':error_von,'prod_varoption':prod_varoption,'variant':variant})
        variantoption_stock=request.POST.get('variantoption_stock')
        if variantoption_stock == '' or not variantoption_stock.isnumeric() :
            error_vos='Please enter valid stock quantity'
            return render(request,'admin_addvariantoptions.html',{'error_vos': error_vos,'prod_varoption':prod_varoption,'variant':variant })
        variantoption_price=request.POST.get('variantoption_price')
        if variantoption_price == '' or not variantoption_price.isnumeric() :
            error_vop='Please enter valid Price'
            return render(request,'admin_addvariantoptions.html',{'error_vop': error_vop,'prod_varoption':prod_varoption,'variant':variant })
        
        
        Variantoptions.objects.create(unit=varop_unit,voption_vartaint_key=var_obj,voption_prod_key=prod_varoption,variantoption_name=variantoption_name,price=variantoption_price,product_stock=variantoption_stock)
        return redirect('admin_editproducts')

    variant=Variants.objects.all()
    uid = request.GET.get('uid')
    prod_varoption=Products.objects.get(id =uid)
    return render(request,'admin_addvariantoptions.html',{'prod_varoption':prod_varoption,'variant':variant})




#product_variantoption_selecting
def product_variantoption_selecting(request):
    if request.method =='GET':
        variantoption_id=request.GET.get('variantoption_id')
        product_variant_obj=Variantoptions.objects.get(id=variantoption_id)
        product_variant_price=product_variant_obj.price
        product_variant_dis_price=product_variant_obj.discount_price
        product_variant_dis_amt=product_variant_obj.voption_prod_key.p_category.catewise_dicount_price


        data={
            "product_variant_price":product_variant_price,
            'product_variant_dis_price':product_variant_dis_price,
            'product_variant_dis_amt':product_variant_dis_amt
        }   
    return JsonResponse(data)


# final stual of ajax by seeing vedio

# def search_products(request):
#     # print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
#     query = request.GET.get('ser_name')
#     list_pro=list()
#     if query != '':
#         results = Products.objects.filter(Q(book_title__icontains=query) | Q(description__icontains=query))
#         for i in results:
#             ser=ProductsSerializer(i)
#             list_pro.append(ser.data)
        #     print(ser.data,'gggggggg')
        # print(list_pro,'oooooooooooooooooooooooooooooooooooooooo')
        
        
    #     return HttpResponse(json.dumps(list_pro))
    # return HttpResponse('NUll')
    # return JsonResponse({'products': products})
    # return JsonResponse('TRUE')





# def search_products(request):
#     print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
#     query = request.GET.get('query')
#     results = Products.objects.filter(Q(book_title__icontains=query) | Q(description__icontains=query))
#     products = []
#     for product in results:
#         products.append({
#             'id': product.id,
#             'image_url': product.image.url,
#             'book_title': product.book_title,
#             'price': product.get_default_price.price,
#             'category': product.p_category,
#             'description': product.description
#         })
#     return JsonResponse({'products': products})


def search_products(request):
    search_term = request.GET.get('search', '')
    filtered_products = Products.objects.filter(book_title__icontains=search_term)
    product_list = []
    for product in filtered_products:
        product_list.append({
            'id': product.id,
            'book_title': product.book_title,
            'description': product.description,
            'image': str(product.image),
            'p_category':product.p_category.cate_name,
            'save_price':product.p_category.catewise_dicount_price
           
        })
        price={
        "price":product.get_variantoption_price()
        }
        product_list[-1].update(price)

        id_var={
        "id_var":product.get_variantoption_id()
        }
        product_list[-1].update(id_var)

        dis_price={
        "dis_price":product.get_variantoption_discount_by_cateprice()
        }
        product_list[-1].update(dis_price)
        print('00000000',dis_price)

    return JsonResponse(product_list, safe=False)

def admin_addcoupon(request):
    if request.method == 'POST':
        coupon_name=request.POST.get('coupon_name')
        coupon_dis_amount=request.POST.get('coupon_dis_amount')
        coupon_min_amount_req=request.POST.get('coupon_min_amount_req')
        Coupon.objects.create(
            coupon_name=coupon_name,
            coupon_dis_amount=coupon_dis_amount,
            coupon_minmun_amount=coupon_min_amount_req
        )
        return redirect('admin_couponlist')
    return render(request,'admin_addcoupon.html')


def admin_couponlist(request):
    coupon_obj=Coupon.objects.all()
    return render(request,'admin_couponlist.html',{'coupon_obj':coupon_obj})


def delete_coupon(request):
    uid= request.GET.get('uid')
    coup_obj=Coupon.objects.get(id=uid)
    coup_obj.delete()
    return redirect('admin_couponlist')


def admin_salesreport(request):
    return render(request,"admin_salesreport.html")

# def coupon_dis_totalamount(request):
#     if request.method == 'POST':
#         loginuser = request.session['user_email']
#         user1 = Userdetails.objects.get(user_email = loginuser )
#         cart = Cart.objects.filter(user = user1)
#         cart_len = len(Cart.objects.filter(user = user1))
#         total_price = sum([i.subtotal for i in cart])
#         amount=total_price-40
#         print('hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
#     return redirect('checkout_summary')



def adnin_VedioBannerList(request):
    banVedio=BannerVedio.objects.all()
    context={
        'banVedio':banVedio
            }
    return render(request,'admin_bannerlist.html',context)



def admin_addVedioBanner(request):
    if request.method =="POST":
        banVedio=request.FILES.get('banVedio')
        banDes=request.POST.get('banDes')
        banObj=BannerVedio(banVedio=banVedio,description=banDes)
        banObj.save()
        return redirect('adnin_VedioBannerList')
    return render(request,'admin_addVediobanner.html')


def admin_editbanner(request):

    if request.method == "POST":
        uid=request.GET.get('uid')
        ban_obj=BannerVedio.objects.get(id=uid)
        ban_obj.description=request.POST.get('des')
        img = request.FILES.get('img')

        if len(img) !=0:
            if len(ban_obj.banVedio) >0:
                os.remove(ban_obj.banVedio.path)
            ban_obj.banVedio = request.FILES.get('img')
        ban_obj.save()
        return redirect('adnin_VedioBannerList')
    uid=request.GET['uid']
    ban=BannerVedio.objects.get(id=uid)
    return render(request,'admin_editVedioBanner.html',{'ban':ban})




def user_aboutus(request):
    return render(request,'user_aboutus.html')

def user_contact(request):
    return render(request,'user_contact.html')

def user_wishlist(request):
    user=request.session['user_email']
    prod_id=request.GET['uid']
    varop_id=request.GET['variant_option_id']
    user_obj=Userdetails.objects.get(user_email=user)
    prod_obj=Products.objects.get(id=prod_id)   
    varop_obj=Variantoptions.objects.get(id=varop_id)
    try:
        u_create=Wishlist.objects.filter(wish_user_key=user_obj)
    except Wishlist.DoesNotExist:
        Wishlist.objects.create(wish_user_key=user_obj,wish_varoptio_key=varop_obj,wish_prod_key=prod_obj)
        # wish_obj=Wishlist.objects.all()
        # context={
        #     'wish_obj':wish_obj
        #         }
        # return render(request,'user_wishlist.html',context)
    try:
        prod_obj_inwish=u_create.get(wish_user_key=user_obj,wish_varoptio_key=varop_obj,wish_prod_key=prod_obj)
    except Wishlist.DoesNotExist:
        Wishlist.objects.create(wish_user_key=user_obj,wish_varoptio_key=varop_obj,wish_prod_key=prod_obj)

    wish_obj=Wishlist.objects.all()
    context={
        'wish_obj':wish_obj
    }
    return redirect('total_wishlist')

def total_wishlist(request):
    user=request.session['user_email']
    user_obj=Userdetails.objects.get(user_email=user)
    wish_obj=Wishlist.objects.filter(wish_user_key=user_obj)
    context={
        'wish_obj':wish_obj
    }
    return render(request,'user_wishlist.html',context)

def remove_product_inwish(request):
    user=request.session['user_email']
    uid=request.GET.get('uid')
    prod_obj=Variantoptions.objects.get(id=uid)
    user_obj=Userdetails.objects.get(user_email=user)
    wish_obj=Wishlist.objects.get(wish_varoptio_key=prod_obj,wish_user_key=user_obj)
    wish_obj.delete()

    return redirect('total_wishlist')




def discount_showing(request):
    return JsonResponse