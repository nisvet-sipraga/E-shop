from decimal import Context
from functools import reduce
from logging import raiseExceptions
from typing import get_args
from django import contrib
import django
from django.contrib.auth import tokens
from django.core.checks import messages
from django.db.models.query import prefetch_related_objects
from django.forms.utils import pretty_name
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate,logout
from django.http import HttpResponse, request
from django.urls.conf import path
from django.views.generic.base import TemplateView 
from .models import Account, Computers,Kategorije,Periferija_i_memorija ,ShopCart ,SlideShow,Reklama1,Reklama2,Customer,Kmesages
from aplikacija import models
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistrationForm, LoginAutentForm, ProizvodForma ,ShopSlide,Reklam2,Reklam1,PayCart,Mesage
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,force_text, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import generate_token
from django.core.mail import EmailMessage, message
from django.conf import settings
from django.views.generic import View
from validate_email import validate_email
import os
import random
import string
from datetime import date
from datetime import datetime, timedelta
import datetime
import stripe
from django.db import connection,transaction
from django.db.models import Sum
from django.http import JsonResponse
from collections import OrderedDict
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from rest_framework.views import APIView
from rest_framework.response import Response

### NAVBAR KATEGORIJE DROPDOWN MENU
def dropDow():
    cate2 = Kategorije.objects.all()
    cate3 = Periferija_i_memorija.objects.all()

    return cate2, cate3


### BROJA ARTIKALA U KORPI
def brojCart(request):
    user = request.user
    if user.is_authenticated:
        user=user.id
        shoviwe = ShopCart.objects.filter(id_customer = user)
    else:
        try:
            device = request.COOKIES['device']
            shoviwe = ShopCart.objects.filter(id_customer = device)
        except:
            device = {}
            shoviwe = ShopCart.objects.filter(id_customer = device)
    lista_id=[]
    lista=[]
    for sho in shoviwe:
        sho_id=sho.id
        lista_id.append(sho_id)
        lista.append(sho.id_proizvod)
    broj = len(lista)
    return broj


##### KORPA UPDATE QUANTITI!!!
def updateKart(request, idscp):
    id=idscp
    print(id)
    user = request.user
    if request.method == 'POST':
        kli = request.POST['quantity']
        kli = int(kli)
        koCijen= Computers.objects.filter(id = id)
        cijenPojedina = koCijen[0].cijena
        ukup = kli * cijenPojedina
        print("ovo je post kolicina:", kli)
        if user.is_authenticated:
            ShopCart.objects.filter(id_proizvod = id, id_customer=user.id).update(kolicina = kli, iznos= ukup)
            print("Kolicina je apdjetana:", kli)
        else:
            device = request.COOKIES['device']
            ShopCart.objects.filter(id_proizvod = id, id_customer=device).update(kolicina = kli, iznos= ukup)
            print("Kolicina je apdjetana:", kli)
    return redirect("/shoppingCart")


### PRIKAZ SHOP CARTA 
def shoppCart(request):
    

    cate2,cate3 = dropDow() 
    user = request.user
    if user.is_authenticated:
        user=user.id
        shoviwe = ShopCart.objects.filter(id_customer = user)

    else:
        try:
            device = request.COOKIES['device']
            shoviwe = ShopCart.objects.filter(id_customer = device)
        except:
            device = {}
            
    lista_id=[]
    lista=[]
    cijena=0
    for sho in shoviwe:
        cijena+=sho.iznos
        sho_kol = sho.kolicina
        sho_id=sho.id
        lista_id.append(sho_id)
        lista.append(sho.id_proizvod)
    
    lista1=[]
    for list in lista:
        listaProiz = Computers.objects.all().filter(id=list)
        lista1.append(listaProiz)

 

   
    broj=len(lista1)
    
    print("iznad liste id")
    print(lista_id)
    print("izmedu lisi")
    print(lista1)
    for lis in lista1:
        for li in lis:
            print(li.naziv)

    print(cijena)
    print("ovo je cijena")
    context = {
        'shopPr':lista1,
        'cijena':cijena,
        'broj':broj,
        'proi_sel': lista_id,
        'cate2':cate2,
        'cate3':cate3,
        'shoviwe':shoviwe,
        
    }       

    form = PayCart()
    print("iznad moje forme")    
    print(form)
    print("ispod moje forme")
    if request.method == 'POST':  
        form = PayCart(request.POST)
        print("iznad drugog forma")
        print(form)
        
        if form.is_valid():
            print("usao sam u validnost forme ")
            form.save()
            return redirect('/phome')

    return render(request,"shoppingCart.html",context)


### BRISANJE STARIJIH PROIZVODA OD 24H
def clean_time():
    date_now=datetime.datetime.now()
    s=ShopCart.objects.filter(date_start__lt = date_now).delete()
    print(s)




### DODAVANJE PROIZVODA U KORPU
def shopCart(request ,idsc):
    id=idsc
    user = request.user

    if user.is_authenticated:
        user=user.id
        koCijen= Computers.objects.filter(id = id)
        cijenPojedina = koCijen[0].cijena
        kol = ShopCart.objects.filter(id_proizvod = id, id_customer=user)

        try:
            kli = kol[0].kolicina
        except:
            kli = 1
        
        
        if kol:
            kli+=1
            ukup = kli * cijenPojedina
            ShopCart.objects.filter(id_proizvod = id, id_customer=user).update(kolicina = kli , iznos= ukup)
        
        else:

            
            ukup = kli * cijenPojedina
            print("povis usera")
            print(user)
            print("ispod usera")
            c=ShopCart(id_proizvod=id ,id_customer=user , iznos= ukup )
            c.save()
        
    
    else:
        koCijen= Computers.objects.filter(id = id)
        cijenPojedina = koCijen[0].cijena
        device = request.COOKIES['device']
        kol = ShopCart.objects.filter(id_proizvod = id, id_customer=device)
        try:
            kli = kol[0].kolicina
        except:
            kli = 1
        if kol:
            kli+=1
            ukup = kli * cijenPojedina
            ShopCart.objects.filter(id_proizvod = id, id_customer=device).update(kolicina = kli , iznos= ukup)
        
        else:
            clean_time()
        
      
            print(device)
            ukup = kli * cijenPojedina
            c=ShopCart(id_proizvod=id ,id_customer=device, iznos= ukup)
            c.save()
        
        
    return redirect('/home')


### BRISANJE ARTKALA IZ KORPE NA KLIK DELETE
def delete_shopCart(request , shop_id):

    shop_id = int(shop_id)

    try:
        proi_sel = ShopCart.objects.get(id= shop_id)
    except ShopCart.DoesNotExist :
        return redirect('/shoppingCart')
    proi_sel.delete()
    return redirect('/shoppingCart')


### DODAVANJE PROIZVODA
def creat_proiz(request):
    form = ProizvodForma()
    print("iznad prvog forma")
    print(form)
    proizvod = Computers.objects.all()
    kat=Kategorije.objects.all()
    pod_kat=Periferija_i_memorija.objects.all()
    
    if request.method == 'POST':  
        form = ProizvodForma(request.POST, request.FILES)
        print("iznad drugog forma")
        print(form)
        
        if form.is_valid():
            form.save()
            return redirect('/home')
    else:
        form = ProizvodForma()
    return render(request, "pc.html" ,{'proizvod':proizvod,'kat':kat, 'pod_kat':pod_kat})





##### EDITOVANJE PROIZVODA

def editProduct(request, pk , ik,iko):
    data = Computers.objects.get(id=pk)
    id_cat = Kategorije.objects.get(id=ik)
    if iko != "None":
        id_pod= Periferija_i_memorija.objects.get(id=iko)


        kat=Kategorije.objects.all()
        pod_kat=Periferija_i_memorija.objects.all()
        
        form = ProizvodForma(request.POST,request.FILES,instance = data)
        if form.is_valid():
            form.save()
            return redirect("/izlistavanje")
        else:
            return render(request, 'update.html', {'prod': data,'kat':kat, 'pod_kat':pod_kat, 'id_cat':id_cat, 'id_pod':id_pod})
    
    else:
        kat=Kategorije.objects.all()
        pod_kat=Periferija_i_memorija.objects.all()
        
        form = ProizvodForma(request.POST,request.FILES,instance = data)
        if form.is_valid():
            form.save()
            return redirect("/izlistavanje")
        else:
            return render(request, 'update.html', {'prod': data,'kat':kat, 'pod_kat':pod_kat, 'id_cat':id_cat})



### BRISANJE PROIZVODA IZ COMPUTERSA
def delete_proiz(request, proi_id):
	proi_id = int(proi_id)
	try:
		proi_sel = Computers.objects.get(id = proi_id)
	except Computers.DoesNotExist:
		return redirect('/izlistavanje')
	proi_sel.delete()
	return redirect('/izlistavanje')



### IZLISTAVANJE PROIZVODA
def izlistavanje_proiz(request):
    proizvod = Computers.objects.all()
    return render(request, "izlist_proizvoda.html" ,{'proizvod':proizvod})



###
def home(request):
    slide = SlideShow.objects.all()
    reklama1 = Reklama1.objects.all()
    reklama2 = Reklama2.objects.all()

    broj=brojCart(request)
    #proizvod=Computers.objects.all() 
    category=Kategorije.objects.all()
    cate3=Periferija_i_memorija.objects.all()
    lista= []
    
 
        
    #context={}
    for cat in category:
        
        
        proizvod = Computers.objects.filter(id_kategorija=cat.id).order_by('-id')[:4:-1]
        categ = Kategorije.objects.filter(id=cat.id)
        if proizvod and categ:
            lista.append((categ,proizvod))
            
        else:
            continue   
               
    proizvod=lista
    context={
        'proizvod':proizvod,
        'cate3':cate3,
        'broj':broj,
        'slide':slide,
        'reklama1':reklama1,
        'reklama2':reklama2
    }
    #context['proizvod']=proizvod 
    print(context)

    return render(request,"index.html",context)
    
    


#### IZLISTAVANJE PROIZVODA POJEINACNO
    
def single_pro(request , idp,idk,idpk):
    broj=brojCart(request)
    cate2 = Kategorije.objects.all()
    id_kategorij = Kategorije.objects.get(id=idk)
    cate3 =  Periferija_i_memorija.objects.all()




    if idpk != "None":
        id_podkategorija = Periferija_i_memorija.objects.get(id=idpk)
        proizvod=Computers.objects.all().filter(pk=idp)
        
        return render(request,"svipro.html",{'proizvod':proizvod ,'id_kategorij':id_kategorij,'id_podkategorija':id_podkategorija, 'cate2':cate2, 'cate3':cate3,'broj':broj,})
    else:
     
        proizvod=Computers.objects.all().filter(pk=idp)
        return render(request,"svipro.html",{'proizvod':proizvod ,'id_kategorij':id_kategorij, 'cate2':cate2, 'cate3':cate3,'broj':broj})



#### REGISTRACIJA

def registration_view(request):
    
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        user1=Account.objects.filter(email=email)
        for user in user1:

            print(user.id)
        current_site= get_current_site(request)
        email_subject='Confirm mail',
        message=render_to_string('activate.html',
        

        {
            'user':user,
            'domain':current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.id)),
            'token':generate_token.make_token(user)
        }
        )
        
        print(message)
        print(message[1])
        print(generate_token.make_token(user))

        email_message = EmailMessage(
        email_subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email]
        )
        print(email_message)
        email_message.send()

        
        
        return redirect('/home')

    else:
        print("nesto nije udure") 
   

    
    return render(request,"register.html")




####aKTIVACIJA ACCOUNTA PREKO EMAILA

class ActivateAccountView(View):
    def get(self, request , uidb64,token):
        try:
            uid=force_text(urlsafe_base64_decode(uidb64))
            user1=Account.objects.filter(id=uid)
            for user in user1:
                print(user.is_active)
                print("ispod usera")    
        except Exception as identifier:
            user=None
        
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            context={
                'message':'You have confirmed your email'
            }
            return render(request,'activate_failed.html', context)
            
        return render(request,'activate_failed.html',status=401)




#### sLANJE EMAILA ZA PASS RESET

class RequestResetEmailView(View):
    def get(self, request):
        return render(request, 'request-reset-email.html')

    def post(self,request):
       
        email=request.POST['email']
        
        
        
        if not validate_email(email):
            pass
            return render(request,'request-reset-email.html')
        userP=Account.objects.filter(email=email)
        if userP:
            for user in userP:
                pass
            current_site= get_current_site(request)
            email_subject='Reset your password',
            message=render_to_string('reset-user-password.html',
            {
            
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.id)),
                'token':PasswordResetTokenGenerator().make_token(user)
            }
            )
        
            email_message = EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email]
            )
            print(email_message)
            email_message.send()
    
            
        return render(request,'request-reset-email.html')


#### PASSWORD RESET!!!!

class SetNewPasswordView(View):
    def get(self, request , uidb64,token):
        context = {
            'uidb64': uidb64,
            'token':token
        }
        print(context)
        return render(request,'set-new-password.html', context)


    def post(self, request , uidb64,token):
        context = {
            'uidb64': uidb64,
            'token':token
        }
    
        password = request.POST.get('password')
        password2 = request.POST.get('password1')
        print(password2,password)
        if password == password2:
            try:
                uid=force_text(urlsafe_base64_decode(uidb64))
                print(uid)
                user1=Account.objects.filter(id=uid)
                print(user1)
                for user in user1:
                    pass
                user.set_password(password) 
                
                user.save()
                    
                return redirect('/login')
            except Exception as identifier:
                user=None
        else:
            return redirect('/request-reset-email')
            
        return render(request,'set-new-password.html' , context)




#### LOGIN!!!!

def login_view(request):

    user = request.user
    if user.is_authenticated:
        return redirect("/home")
    
    if request.POST:
        form = LoginAutentForm(request.POST)
        print("usao je u if kod forme")
        print(form)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                if user.is_staff == 1:
                    return redirect('/home')
                else:
                    return redirect('/pc')
    else:
        print("niste logovani")  

    return render(request, 'login.html')


### LOGOUZ

def logoOut_view(request):
    logout(request)
    return redirect('/home')


###VIEW ZA KATEGORIJE

def wiew_category(request, idc):
    broj=brojCart(request)
    categoryW2 = Computers.objects.filter(id_kategorija=idc).order_by('-id')[::-1]
    cate = Kategorije.objects.filter(id=idc)
    cate2 = Kategorije.objects.all()
    cate3 = Periferija_i_memorija.objects.all()
    
    catvie = []
    #context = {}
    if idc == 1:
        for podkate in cate3:
           
            categoryW1 = Computers.objects.filter(id_podkategorija=podkate.id).order_by('-id')[:4:-1]
            cate4 = Periferija_i_memorija.objects.filter(id=podkate.id)
            if categoryW1 and cate4:
                catvie.append([cate4,categoryW1]) 


        context = {
            'category':catvie,
            'cate':cate,
            'cate2':cate2,
            'cate3':cate3,
            'broj':broj,
        }        
    
        #categoryW = catvie
        #context['categoryW']=categoryW
       
   
        return render(request,"category.html",context)
    else:
        
        return render(request,"category.html",{'categoryW':categoryW2, 'cate':cate, 'cate2':cate2,'cate3':cate3,'broj':broj})

###IZLISTAVANJE SVIH PODKATEGORIJA NAKON KLINA POGLEDAJ VISE NA PERIFERIJU I MEMORIJU

def podkategorijaWiwe(request ,idom):
    broj=brojCart(request)
    podWiwe = Computers.objects.filter(id_podkategorija=idom).order_by('-id')[::-1]
    podCate = Periferija_i_memorija.objects.filter(id=idom)
    cate3 = Periferija_i_memorija.objects.all()
    cate2 = Kategorije.objects.all()
    context = {
        'podWiwe':podWiwe,
        'podCate':podCate,
        'cate2':cate2,
        'cate3':cate3,
        'broj':broj,
    }        
    #categoryW = catvie
    #context['categoryW']=categoryW
    
   
    return render(request,"podkategorija.html",context)




### SLIDESHOW I REKLAME

def slideShow(request):
    slide = SlideShow.objects.all()

    if request.method == "POST":
        slide.delete()
        form = ShopSlide(request.POST,request.FILES)
        if form.is_valid():
            form.save()

    return render(request,"showSlide.html",{'slide':slide})





def reklama1(request):
    reklama1 = Reklama1.objects.all()

    if request.method == "POST":
        reklama1.delete()
        form = Reklam1(request.POST,request.FILES)
        if form.is_valid():
            form.save()

    return render(request,"reklama1.html",{'reklama1':reklama1})




def reklama2(request):
    reklama2 = Reklama2.objects.all()

    if request.method == "POST":
        reklama2.delete()
        form = Reklam2(request.POST,request.FILES)
        if form.is_valid():
            form.save()

    return render(request,"reklama2.html",{'reklama2':reklama2})



###  TRAZI KAO KORISNIK


def trazi(request):
    broj = brojCart(request)
    cate2, cate3= dropDow()

    if request.method == 'POST':
        rijec = request.POST['searched']
        rez = Computers.objects.filter(naziv__icontains = rijec)
        print(rez)
        print(rijec)
    else:
        print("niste trazili")
    context = {
        'rez':rez,
        'broj':broj,
        'cate2':cate2,
        'cate3':cate3,


    }
    return render(request,"search.html",context)



###  TRAZI KAO ADMIN

def adminTrazi(request):
    broj = brojCart(request)
    cate2, cate3= dropDow()

    if request.method == 'POST':
        rijec = request.POST['asearched']
        rez = Computers.objects.filter(naziv__icontains = rijec)
        print(rez)
        print(rijec)
    else:
        print("niste trazili")
    context = {
        'rez':rez,
        'broj':broj,
        'cate2':cate2,
        'cate3':cate3,


    }
    return render(request,"adminSearch.html",context)



###  TABELA KORISNIKA
def table(request):
    lista = Account.objects.all()
    print("povis liste")
    print(lista)
    print("ispod liste")
    return render(request,"tables.html" ,{"lista":lista})




### PLACANJE
stripe.api_key = settings.SECRET_KEY 
class HomePageView(TemplateView):    
    template_name = 'phome.html'
    def get_context_data(self,cijena,*kwargs):
        context =super().get_context_data(*kwargs)        
        context['key'] = settings.PUBLISHABLE_KEY 
        context['cijena'] = cijena
     
        print(context)
        print("ispod contexta")
   
        return context




def charge(request,cijena):
    cijena=float(cijena)
    cijena=int(cijena)
    
    try:
        if request.method == 'POST':
            email= request.POST['email']
            firstname = request.POST['firstname']
            lastname = request.POST['lastname']
            address= request.POST['address']
            number= request.POST['number']
            print("iznad rijeci 1")
            print(firstname)
            print(lastname)
            print(email)
            print(address)
            print(number)
            user = request.user
            if user.is_authenticated:
                device=user.id
                print(device)
            else:
                device = request.COOKIES['device']
                print(device)
            lista=[]
            customers = ShopCart.objects.filter(id_customer = device)
            for cus in customers:
                print(cus)
                print("izmedu cusa i a")
                a=cus.id_proizvod
                print(a)
                customer = Computers.objects.filter(id = a)
                print(customer)
                for cus in customer:
                    lista.append(cus.naziv)
                    print("ispod cusa")
            
            print("ispod nasih rijeci , ja se nadam da ce to biti sve u radut ")
            
 
            
            
            charge= stripe.Charge.create(
                amount = cijena,
                currency = 'usd',
                description = 'Payment Gateway',
                source = request.POST ['stripeToken']
            )           
            print("proslo je stipe")
                   
            print(firstname)
            print(lastname)
            print(email)
            print(address)
            print(number)
            print(lista)
            b = Customer(email=email,lastname=lastname,address=address,number=number, id_customer=device,firstname=firstname,cijena=cijena,proizvodi=lista)
            print(b)
            print(b.save())
            b.save()

            return render(request, 'daLogin.html')
    except:
        return render(request, 'fail_charge.html')


### IZLISTAVANJE KUPADA NA ADMIN PANELU
def custom(request):
    customers= Customer.objects.all()
    context = {
        'customers':customers,
    }
    return render(request, 'customer.html', context)


### TEMPLATGE KONTAKTA
def kontakt(request):
    cate2, cate3= dropDow()
    broj=brojCart(request)
    mes = Kmesages.objects.all()
    if request.method == "POST":
        form = Mesage(request.POST)
        print(form)
        print("izmedu formi")
        if form.is_valid():
            print(form)
            form.save()

    context = {
    
        'broj':broj,
        'cate2':cate2,
        'cate3':cate3,
    }
    return render(request,"kontakt.html",context)



### IZLISTAVANJE MESS NA ADMIN PANELU
def mesages(request):
    mes = Kmesages.objects.all()
    
    return render(request, 'messages.html',{'customers':mes})


### ABOUT TEMPLATRE
def about(request):
    cate2, cate3= dropDow()
    broj=brojCart(request)
    context = {
        'broj':broj,
        'cate2':cate2,
        'cate3':cate3,
    }
    return render(request,"about.html",context)


### ADMIN INDEX. NA ADMIN PANELU
def adminViews(request):
    date_now=datetime.datetime.now()+timedelta(days=1)
    date_now1=datetime.datetime.now()+timedelta(days=-1)


    a = datetime.datetime.now().year 
    b1 = datetime.datetime.now().month

    pric=Customer.objects.filter(date_start_pay__lt = date_now , date_start_pay__gt = date_now1)
    pric2=Customer.objects.filter(date_start_pay__year=a,
                              date_start_pay__month=b1,
                              )


    
    a3 = datetime.datetime.now().year 
    a2 = datetime.datetime.now().year -1
    b3 = datetime.datetime.now().month - 1
    if b3!=0:
        a2=a3
    if b3 == 0:
        b3=12    
    b4 = datetime.datetime.now().month 
    print("ispod datuma")
    pric3=Customer.objects.filter(
                              date_start_pay__year=a2,
                              date_start_pay__month=b3,
                              
                            )

    a2 = datetime.datetime.now().year 
    pric4=Customer.objects.filter(
                              date_start_pay__year=a2,
                             )
  

    price4=0
    for pri in pric4:
        price4 +=pri.cijena

    price3=0
    for pri in pric3:
        price3 +=pri.cijena

    price=0
    for pri in pric:
        price +=pri.cijena
    print(price)
    price2=0
    for pri in pric2:
        price2 +=pri.cijena

    context = {
        'price':price,
        'price2':price2,
        'price3':price3,
        'price4':price4,
    }

    return render(request, 'adminIndex.html', context)
    

### CHAERT ZA GODISNJI PROMET
from chartjs.views.lines import BaseLineChartView
class LineChartJSONView(BaseLineChartView):
   
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July","August","September","Oktorber","November","December"]

    def get_providers(self):

        a1 = datetime.datetime.now().year 
        a2 = datetime.datetime.now().year -1

        
        
        return [a1, a2, "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""
        a2 = datetime.datetime.now().year 
        lista=[]
        print("hamo")
        customers1=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=1,)
        customers2=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=2,)
        customers3=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=3,)
        customers4=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=4,)
        customers5=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=5,)
        customers6=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=6,)
        customers7=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=7,)
        customers8=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=8,)
        customers9=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=9,)
        customers10=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=10,)
        customers11=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=11,)
        customers12=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=12,)            
                        
        ful1=0
        for cus in customers1:
            a=cus.cijena
            ful1+=a
        lista.append(ful1)
        ful2=0
        
        for cus in customers2:
            a=cus.cijena
            ful2+=a
        lista.append(ful2)
        
        ful3=0
        for cus in customers3:
            a=cus.cijena
            ful3+=a
        lista.append(ful3)
        
        ful4=0
        for cus in customers4:
            a=cus.cijena
            ful4+=a
        lista.append(ful4)
        
        ful5=0
        for cus in customers5:
            a=cus.cijena
            ful5+=a
        lista.append(ful5)

        ful6=0
        for cus in customers6:
            a=cus.cijena
            ful6+=a
        lista.append(ful6)
       
        ful7=0
        for cus in customers7:
            a=cus.cijena
            ful7+=a
        lista.append(ful7) 

        ful8=0
        for cus in customers8:
            a=cus.cijena
            ful8+=a
        lista.append(ful8)

        ful9=0
        for cus in customers9:
            a=cus.cijena
            ful9+=a
        lista.append(ful9)

        ful10=0
        for cus in customers10:
            a=cus.cijena
            ful10+=a
        lista.append(ful10)

        ful11=0
        for cus in customers11:
            a=cus.cijena
            ful11+=a
        lista.append(ful11)

        ful12=0
        for cus in customers12:
            a=cus.cijena
            ful12+=a
        lista.append(ful12)    
      
        print(lista)
        print("ispod liste")
        ### ZA PROSLU CIJELU GOD U CHARTU
        a2 = datetime.datetime.now().year -1    
        customers1=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=1,)
        customers2=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=2,)
        customers3=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=3,)
        customers4=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=4,)
        customers5=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=5,)
        customers6=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=6,)
        customers7=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=7,)
        customers8=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=8,)
        customers9=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=9,)
        customers10=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=10,)
        customers11=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=11,)
        customers12=Customer.objects.filter(
              date_start_pay__year=a2,
              date_start_pay__month=12,)            
        
        lista2=[]                
        ful1=0
        for cus in customers1:
            a=cus.cijena
            ful1+=a
        lista2.append(ful1)
        ful2=0
        
        for cus in customers2:
            a=cus.cijena
            ful2+=a
        lista2.append(ful2)
        
        ful3=0
        for cus in customers3:
            a=cus.cijena
            ful3+=a
        lista2.append(ful3)
        
        ful4=0
        for cus in customers4:
            a=cus.cijena
            ful4+=a
        lista2.append(ful4)
        
        ful5=0
        for cus in customers5:
            a=cus.cijena
            ful5+=a
        lista2.append(ful5)

        ful6=0
        for cus in customers6:
            a=cus.cijena
            ful6+=a
        lista2.append(ful6)
       
        ful7=0
        for cus in customers7:
            a=cus.cijena
            ful7+=a
        lista2.append(ful7) 

        ful8=0
        for cus in customers8:
            a=cus.cijena
            ful8+=a
        lista2.append(ful8)

        ful9=0
        for cus in customers9:
            a=cus.cijena
            ful9+=a
        lista2.append(ful9)

        ful10=0
        for cus in customers10:
            a=cus.cijena
            ful10+=a
        lista2.append(ful10)

        ful11=0
        for cus in customers11:
            a=cus.cijena
            ful11+=a
        lista2.append(ful11)

        ful12=0
        for cus in customers12:
            a=cus.cijena
            ful12+=a
        lista2.append(ful12)  
        return [lista,
                lista2,]

    
line_chart = TemplateView.as_view(template_name='charts.html')
line_chart_json = LineChartJSONView.as_view()

