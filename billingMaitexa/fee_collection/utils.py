from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from decouple import config
import random
from time import time
from weasyprint import HTML
from io import BytesIO

def convert_to_words(num):
    below_20 = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", 
                "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    thousands = ["", "Thousand", "Million"]

    if num == 0:
        return "Zero"

    def words(n):
        if n < 20:
            return below_20[n]
        elif n < 100:
            return tens[n // 10] + ('' if n % 10 == 0 else ' ' + below_20[n % 10])
        elif n < 1000:
            return below_20[n // 100] + ' Hundred' + ('' if n % 100 == 0 else ' ' + words(n % 100))
        else:
            for i, v in enumerate(thousands):
                divisor = 1000 ** (i + 1)
                if n < divisor * 1000:
                    main_part = words(n // divisor)
                    remaining_part = n % divisor
                    return main_part + ' ' + v + ('' if remaining_part == 0 else ' ' + words(remaining_part))

    return words(num).strip()


def generate_pdf_from_html(html_content):
    pdf = HTML(string=html_content).write_pdf()
    
    buffer = BytesIO()
    buffer.write(pdf)
    buffer.seek(0)
    return buffer


### Send email ###
def send_email(template,subject,content,recipient,pdf_filename='payment',pdf_content=None):
    sender = settings.EMAIL_HOST_USER
    try:
        html_content = render_to_string(template, {'content': content})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email=sender, to=[recipient])
        msg.attach_alternative(html_content, 'text/html')
        
        if pdf_filename:
            template_pdf='./invoice.html'
            pdf_html_content = render_to_string(template_pdf,pdf_content)
            pdf_file = generate_pdf_from_html(pdf_html_content)
            msg.attach(pdf_filename, pdf_file.getvalue(), 'application/pdf')


        msg.send()
        print('mail success')
        return True
    except Exception as e:
        print(e ,'not working')
        return False