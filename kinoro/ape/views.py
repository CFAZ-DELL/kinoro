from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
import io
from django.http import HttpResponse
from django.shortcuts import redirect, render
from customer.models import Report, Certificate
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from io import BytesIO
import magic
from PIL import Image
from plantingteam.views import createTrackingStatus

# Create your views here.
@login_required
def listreport(request):
    certificate = Certificate.objects.all().exclude(photo="").order_by('order__id')
    allcertificate = Certificate.objects.all().order_by('order__id')

    reports = []
    #same report from several certificates is not added to reports
    for cert in certificate:
        if cert.report not in reports:
            reports.append(cert.report)

    reports_copy = reports.copy()

     #if one certifate not have a photo, the report is removed from reports & approved
    for report in reports_copy:
        for cert in allcertificate:
            if cert.report == report and cert.photo == "" or report.approval == True:
                reports.remove(report)
                break

    return render(request, 'ape/listreport.html', {'reports': reports})


@login_required
def report(request, pk):
    report = Report.objects.get(pk=pk)
    certificates = Certificate.objects.all().filter(order=report.order)
    return render(request, 'ape/report.html', {
        'report': report,
        'certificates': certificates
    })

@login_required
def approve(request, pk):
    certificates = Certificate.objects.all().filter(report__id=pk)

    try:
        for cert in certificates:
            if(cert.receiverName):
                receiverName = cert.receiverName
            else:
                receiverName = cert.order.bill.firstName + ' ' + cert.order.bill.lastName
            
            if(cert.receiverEmail):
                receiverEmail = cert.receiverEmail
            else:
                receiverEmail = cert.order.bill.email

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

            photo_path = cert.photo.path
            with Image.open(photo_path) as img:
                img = img.convert('RGB')
                img.thumbnail((800, 800), Image.ANTIALIAS)
                photo_file = BytesIO()
                img.save(photo_file, 'JPEG', optimize=True, quality=70)
                photo = photo_file.getvalue()

            mime_type = magic.from_buffer(photo, mime=True)

            subject = 'Certificate of Appreciation'
            message = 'Dear ' + receiverName + ',\n\n' + 'Thank you for your participation in the event. Please find the attached certificate of appreciation.\n\n' + 'Best regards,\n' + 'Kinoro Team'
            from_email = 'kinoro@inbox.mailtrap.io'
            to_email = [receiverEmail]
            email = EmailMessage(subject, message, from_email, to_email)
            email.attach("certificate.pdf", pdf, 'application/pdf')
            email.attach(f"{cert.orderQuantity.package.name}.jpg", photo, mime_type)
            email.send()
        
        report = Report.objects.get(pk=pk)
        report.approval = True
        report.save()
        createTrackingStatus(certificates, 'Planted')
        createTrackingStatus(certificates, 'Certificate Sent')
        return redirect('ape:listreport')
    except Exception as e:
        print(e)
        return HttpResponse('Certificate failed to send.')
    
def login(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # log in the user
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'ape/dashboard.html')

@login_required
def logout(request):
    logout(request)
    return redirect('registration/login.html')




        
        

    
        



    


