from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from customer.models import Certificate
from .forms import upload, uploadLatLong
from PIL import Image
from PIL.ExifTags import TAGS
from xhtml2pdf import pisa
from django.template.loader import get_template
import zipfile
from django.contrib.auth.decorators import login_required
from customer.models import Tracking

# Create your views here.

@login_required
def generate(request):
    yesterday = timezone.now().date()
    certificates = Certificate.objects.all().filter(order__orderDate__date=yesterday)

    zip_file = BytesIO()
    with zipfile.ZipFile(zip_file, mode='w') as zip_archive:
        for cert in certificates:
            pdf_file = generateThankYou(cert)
            zip_archive.writestr(f"{cert.receiverName}.pdf", pdf_file.getvalue())
        
        order_list_pdf_file = generateOrderList(certificates)
        zip_archive.writestr(f"{yesterday}.pdf", order_list_pdf_file.getvalue())

    zip_file.seek(0)
    response = HttpResponse(zip_file, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{yesterday}.zip"'
    createTrackingStatus(certificates, "Planting")

    return response
    
    

def generateOrderList(certificates):
    yesterday = timezone.now().date() - timezone.timedelta(days=1)

    template_path = 'plantingteam/generate.html'
    context = {'certificates': certificates}
    template = get_template(template_path)
    html = template.render(context)
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf_file)

    pdf_file.seek(0)
    pdf = pdf_file.read()
    pdf_file.close()
    filename = f"{yesterday}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

def createTrackingStatus(certs, status):
    order = []
    for cert in certs:
        if cert.order not in order:
            order.append(cert.order)
    
    for o in order:
        found = False
        allTracking = Tracking.objects.all().filter(order=o)
        for t in allTracking:
            if t.status == status:
                found = True
                break
        if not found:
            tracking = Tracking.objects.create(order=o, status=status)
            tracking.save()
    
    return
    


def generateThankYou(cert):
    template_path = 'plantingteam/thankyou.html'
    context = {'receiverName': cert.receiverName, 'treeCount': cert.getTotalTrees()}
    template = get_template(template_path)
    html = template.render(context)
    pdf_file = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=pdf_file)

    pdf_file.seek(0)
    pdf = pdf_file.read()
    pdf_file.close()
    filename = f"{cert.receiverName}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response

@login_required
def orderlist(request):
    # yesterday = timezone.now().date() - timezone.timedelta(days=1)
    yesterday = timezone.now().date()
    certificates = Certificate.objects.all().filter(order__orderDate__date=yesterday, photo='')
    return render(request, 'plantingteam/listorder.html', {'certificates': certificates})

@login_required
def order(request, pk):
    certificate = Certificate.objects.get(pk=pk)
    if request.method == 'POST':
        form = upload(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            form.save()
            photo = form.cleaned_data.get('photo')
            if(photo != ''):
                latitude, longitude = get_lat_lon(request.FILES['photo'])
                if (latitude and longitude):
                    certificate.latitude = latitude
                    certificate.longitude = longitude
                    certificate.save()
                    createTrackingStatus([certificate], "Planted")
                    return redirect('plantingteam:orderlist')
            return redirect('plantingteam:orderlatlong', pk=pk)
    else:
        form = upload(instance=certificate)
    certificate = Certificate.objects.get(pk=pk)
    return render(request, 'plantingteam/order.html', {'certificate': certificate, 'form': form})

@login_required
def orderlatlong(request, pk):
    certificate = Certificate.objects.get(pk=pk)
    if request.method == 'POST':
        form = uploadLatLong(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            createTrackingStatus([certificate], "Planted")
            return redirect('plantingteam:orderlist')
    else:
        form = uploadLatLong(instance=certificate)
    certificate = Certificate.objects.get(pk=pk)
    return render(request, 'plantingteam/order.html', {'certificate': certificate, 'form': form})


def get_lat_lon(photo):
    img = Image.open(photo)
    exif = img._getexif()
    if exif:
        exif_data = {
            TAGS[k]: v
            for k, v in exif.items()
            if k in TAGS
        }
        if 'GPSInfo' in exif_data:
            gps_data = exif_data['GPSInfo']
            latitude = convert_degrees(gps_data[2])
            if gps_data[1] == 'S':
                latitude = -latitude
            longitude = convert_degrees(gps_data[4])
            if gps_data[3] == 'W':
                longitude = -longitude
            return latitude, longitude
    return None, None

def convert_degrees(coords):
    """Convert GPS coordinates from degrees, minutes, and seconds to decimal degrees."""
    degrees = coords[0].numerator / coords[0].denominator
    minutes = coords[1].numerator / coords[1].denominator
    seconds = coords[2].numerator / coords[2].denominator
    return degrees + (minutes / 60.0) + (seconds / 3600.0)

@login_required
def dashboard(request):
    return render(request, 'plantingteam/dashboard.html')