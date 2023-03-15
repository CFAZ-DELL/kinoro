from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from .models import Certificate
from .models import Order,Tracking
from .models import Package, Cart, CartQuantity

# Create your views here.
def tracking(request):
    query = request.GET.get('query')
    tracking = []
    q = None
    found = False
    if query:
        try:
            q = Order.objects.get(pk=query)
            tracking = Tracking.objects.filter(order__id=query)
            found = True
        except Order.DoesNotExist:
            q=query

    return render(request, 'customer/tracking.html', {'q': q, 'found': found, 'tracking': tracking })

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

    product = Package.objects.all()

    return render(request, 'customer/product.html', {
        'product': product
    })

def cart(request):
    return render(request, 'customer/cart.html')

def addtocart(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        quantity = int(request.POST.get('quantity'))

        package = Package.objects.get(pk=package_id)

        #retrieve current cart
        if 'cart_id' in request.session:
            cart = Cart.objects.get(pk=1)
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

        return render(request, 'customer/cart.html', {
            'cart_quantity': cart_quantity
        })
    else:
        return render(request, 'customer/cart.html')