from datetime import datetime,timedelta
from django.http import HttpResponse
import base64
import pdfkit
import openpyxl
from django.template.loader import get_template
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side


import warnings
################## PDFs #################
def generate_pdf(content,template,file_name,option):
   
   
    template = get_template(template)
    context = {'logo_base64': ''}
    context.update(content)
    html = template.render(context)
    
    # Create a PDF file from the HTML using pdfkit
    if option==1:
        options = {
        'page-size': 'A3',
        'orientation':'Landscape',
        'margin-top': '0.2854in',
        'margin-right': '0.5in',
        'margin-bottom': '0.2854in',
        'margin-left': '0.5in',
        }
    elif option==2:
        options = {
        'page-size': 'A4',
        'orientation':'portrait',
        'margin-top': '0.3854in',
        'margin-right': '0.5291in',
        'margin-bottom': '0.3854in',
        'margin-left': '0.5292in',
    }
    pdf_file = pdfkit.from_string(html, False, options=options, configuration=pdfkit.configuration(
        wkhtmltopdf='/usr/bin/wkhtmltopdf'))
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{0}".pdf'.format(file_name)
    return response

