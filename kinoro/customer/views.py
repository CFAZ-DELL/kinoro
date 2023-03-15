from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from .models import Certificate, OrderQuantity, Report
from .models import Order,Tracking
from .models import Package, Cart, CartQuantity, Bill
from .forms import BillForm, AddressForm, CertificateForm

# Create your views here.
def tracking(request):
    query = request.GET.get('query')
    tracking = []
    q = None
    found = False
    if query:
        try:
            q = Order.objects.get(pk=query)
            tracking = Tracking.objects.filter(order__id=query).order_by('-date')
            certificates = Certificate.objects.filter(order__id=query)
            found = True
        except Order.DoesNotExist:
            q=query
    else:
        certificates = []

    return render(request, 'customer/tracking.html', {'q': q, 'found': found, 'tracking': tracking, 'certificates': certificates })


def index(request):
    return render(request, 'customer/index.html')

def getCertificate(request, pk):
    cert = Certificate.objects.get(pk=pk)

    receiverName = cert.receiverName
    receiverEmail = cert.receiverEmail

    # Generate the certificate PDF file
    template_path = 'ape/certificate.html'
    context = {'certificate': cert}
    template = get_template(template_path)
    html = template.render(context)
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf_file)

    pdf_file.seek(0)
    pdf = pdf_file.read()
    pdf_file.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificate.pdf"'

    return response

def product(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        quantity = int(request.POST.get('quantity'))

        package = Package.objects.get(pk=package_id)

        #retrieve current cart
        if 'cart_id' in request.session:
            try:
                cart = Cart.objects.get(pk=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id

        #retrieve cart quantity
        try:
            cart_quantity = CartQuantity.objects.get(cart=cart, package=package)
            cart_quantity.quantity += quantity
            cart_quantity.save()
        except CartQuantity.DoesNotExist:
            cart_quantity = CartQuantity.objects.create(cart=cart, package=package, quantity=quantity)

        cart_quantities = CartQuantity.objects.filter(cart=cart)
        total_price = sum([cart_quantity.quantity * cart_quantity.package.price for cart_quantity in cart_quantities])
        total_quantity = sum([cart_quantity.quantity for cart_quantity in cart_quantities])
        
        bill = BillForm()
        address = AddressForm()

        return redirect('customer:viewcart')
    else:
        product = Package.objects.all()

    return render(request, 'customer/product.html', {
        'product': product
    })

def viewcart(request):
    if request.method == 'POST':
        bill = BillForm(request.POST)
        address = AddressForm(request.POST)

        #assign certificate to bill
        cert = CertificateForm()
        if bill.is_valid() and address.is_valid():

            #save the address
            alamat = address.save()

            #save the bill
            bil = bill.save(commit=False)
            bil.address = alamat
            bil.save()

            #retrieve current cart
            if 'cart_id' in request.session:
                try:
                    cart = Cart.objects.get(pk=request.session['cart_id'])
                except Cart.DoesNotExist:
                    cart = Cart.objects.create()
                    request.session['cart_id'] = cart.id
            else:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id

            cart_quantities = CartQuantity.objects.filter(cart=cart)
            
            return redirect('customer:certificate', pk=bil.id)
    
    if 'cart_id' in request.session:
        try:
            cart = Cart.objects.get(pk=request.session['cart_id'])
        except Cart.DoesNotExist:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id

    cart_quantities = CartQuantity.objects.filter(cart=cart)
    total_price = sum([cart_quantity.quantity * cart_quantity.package.price for cart_quantity in cart_quantities])
    total_quantity = sum([cart_quantity.quantity for cart_quantity in cart_quantities])

    bill = BillForm()
    address = AddressForm()



    return render(request, 'customer/cart.html', {
            'cart':cart,
            'total_price': total_price,
            'total_quantity': total_quantity,
            'cart_quantities': cart_quantities,
            'bill': bill,
            'address': address,          
        })

def addtocart(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        quantity = int(request.POST.get('quantity'))

        package = Package.objects.get(pk=package_id)

        #retrieve current cart
        if 'cart_id' in request.session:
            try:
                cart = Cart.objects.get(pk=request.session['cart_id'])
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id

        #retrieve cart quantity
        try:
            cart_quantity = CartQuantity.objects.get(cart=cart, package=package)
            cart_quantity.quantity += quantity
            cart_quantity.save()
        except CartQuantity.DoesNotExist:
            cart_quantity = CartQuantity.objects.create(cart=cart, package=package, quantity=quantity)

        cart_quantities = CartQuantity.objects.filter(cart=cart)
        total_price = sum([cart_quantity.quantity * cart_quantity.package.price for cart_quantity in cart_quantities])
        total_quantity = sum([cart_quantity.quantity for cart_quantity in cart_quantities])
        
        bill = BillForm()
        address = AddressForm()

        return render(request, 'customer/cart.html', {
            'cart':cart,
            'cart_quantity': cart_quantity,
            'total_price': total_price,
            'total_quantity': total_quantity,
            'cart_quantities': cart_quantities,
            'bill': bill,
            'address': address,          
        })
    else:
        return render(request, 'customer/cart.html')
    
def deletecart(request, cart_quantity_id):
    cart_quantity = get_object_or_404(CartQuantity, id=cart_quantity_id)
    cart_quantity.delete()
    return render(request, 'customer/cart.html')

def certificate(request, pk):
    if request.method == 'POST':
        #cert in form is array
        cert = CertificateForm(request.POST)

        temp = -1
        for c in cert:
            temp+=1
        
        
        if cert.is_valid():
            bil = Bill.objects.get(pk=pk)
            order = Order.objects.create(bill=bil)
            report = Report.objects.create(order=order)
            tracking = Tracking.objects.create(order=order, status='Created')
            cart = Cart.objects.get(pk=request.session['cart_id'])
            cartQuantities = CartQuantity.objects.filter(cart=cart)
            index = 0
            for c in cert:
                #get cart quantity
                cartQuantity = cartQuantities[index]
                #save orderQuantity from cartQuantity
                orderQuantity = OrderQuantity.objects.create(order=order, package=cartQuantity.package, quantity=cartQuantity.quantity)
                cer = cert.save(commit=False)
                cer.order = order
                cer.orderQuantity = orderQuantity
                cer.report = report
                cer.save()
                index += 1
                if index > temp - 1:
                    break

            # return redirect('customer:tracking')
            #redirect link to tracking
            return redirect('http://127.0.0.1:8000/tracking/?query='+str(order.id))
        else:
            return redirect('customer:index')

    cert = CertificateForm()
    #retrieve current cart
    if 'cart_id' in request.session:
        try:
            cart = Cart.objects.get(pk=request.session['cart_id'])
        except Cart.DoesNotExist:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id

    cart_quantities = CartQuantity.objects.filter(cart=cart)

    return render(request, 'customer/cert.html', {
        'cert': cert,
        'cart_quantities': cart_quantities,
        'pk': pk,
    })

def createbill(request):
    if request.method == 'POST':
        bill = BillForm(request.POST)
        address = AddressForm(request.POST)

        #assign certificate to bill
        cert = CertificateForm()
        if bill.is_valid() and address.is_valid():

            #save the address
            alamat = address.save()

            #save the bill
            bil = bill.save(commit=False)
            bil.address = alamat
            bil.save()

            #retrieve current cart
            if 'cart_id' in request.session:
                try:
                    cart = Cart.objects.get(pk=request.session['cart_id'])
                except Cart.DoesNotExist:
                    cart = Cart.objects.create()
                    request.session['cart_id'] = cart.id
            else:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id

            cart_quantities = CartQuantity.objects.filter(cart=cart)
            
            return render(request, 'customer/cert.html', {
                'cert': cert,
                'cart_quantities': cart_quantities,
                'bil': bil,
            })
    else:
        bill = BillForm()
        address = AddressForm()

def checkout(request):
    cert_form = CertificateForm(request.POST)
    if cert_form.is_valid():
        cart = Cart.objects.get(pk=request.session['cart_id'])
        cart_quantities = CartQuantity.objects.filter(cart=cart)
        bil = Bill.objects.get(pk=request.POST.get('bill_id'))
        
        order = Order.objects.create(bill=bil)
        
        return redirect('customer:index')
