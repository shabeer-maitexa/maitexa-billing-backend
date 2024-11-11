from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView,CreateAPIView

from .serializers import InvoiceSerializer,CourseFeesSerializer,CoursesSerializer,ViewInvoiceSerializer,ListCourseFeesSerializer,InvoiceListSerializer
from .models import Invoice , CourseFees,PaymentStatus,Course
from authentication.models import Profile

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from datetime import date
from billingMaitexa.pdf import generate_pdf
import threading

from datetime import datetime
from .utils import send_email


def payment_status_update(obj):
    if obj.balance <= 0:
        return PaymentStatus.PAID
    elif 0 < obj.paid_amount < obj.amount_with_discount:
        return PaymentStatus.PARTIALLY_PAID
    else:
        return PaymentStatus.UNPAID


## Genarate a bill for new admission
class RegisterUserAPIView(APIView):
    permission_classes = []

    def post(self, request):
        data = request.data
        email = data.get('email')
        course_id = data.get('course')

        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not course_id:
            return Response({'message': 'Course ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        course_fee_serializer = CourseFeesSerializer(data=data)
        if not course_fee_serializer.is_valid():
            return Response(course_fee_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get or create the profile
        profile, created = Profile.objects.get_or_create(
            email=email,
            defaults={
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'phone': data.get('phone'),
                'phone_b': data.get('phone_b',''),
                'email':email,
                'password': '',
                'address_line1':data.get('address_line1',''),
                'address_line2':data.get('address_line2',''),
                'city':data.get('city',''),
                'state':data.get('state',''),
                'zip_code':data.get('zip_code',''),
            }
        )

        if CourseFees.objects.filter(profile=profile, course__id=course_id).exists():
            return Response({'message': 'User exists'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            course_fees = course_fee_serializer.save(profile=profile)
            return Response({'message': 'Registration success'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            CourseFees.objects.filter(profile=profile).delete()
            return Response({'message': 'user creation failed'}, status=status.HTTP_400_BAD_REQUEST)


## Pay installment
class PayInstallmentAPIView(APIView):
    def post (self,request):
        course_fees=get_object_or_404(CourseFees,uuid=request.data.get('uuid'))
        invoices=Invoice.objects.filter(course=course_fees).count()+1
        payment_mode=request.data.get('mode_of_payment')
        current_payment=request.data.get('current_payment',0)
        current_payment_with_gst=round(float(current_payment)+float(current_payment)*0.18)

        if request.data.get('new_user') == False:
            invoice_data={
                'course':course_fees.id,
                'installment_number':invoices,
                'current_paid_amount':current_payment,
                "current_paid_amount_with_gst":current_payment_with_gst,
                'mode_of_payment':payment_mode
            }
            serializer=InvoiceSerializer(data=invoice_data)
            if serializer.is_valid():
                course_fees.paid_amount=course_fees.paid_amount+float(current_payment)
                course_obj=course_fees.save()
                invoice_instance=serializer.save()

                template = "./base.html"
                recipient = course_obj.profile.email
                subject = "Payment Completed"
                content = 'Your payment is done'
                pdf_content = {'invoice':invoice_instance,'client':course_obj.profile}

                email_thread = threading.Thread(target=send_email, args=(template, subject, content, recipient), kwargs={'pdf_content': pdf_content})
                email_thread.start()
                # send_email(template, subject, content, recipient,pdf_content=pdf_content)


                return Response({'message': 'Fee paid successfully', 'invoice_id': invoice_instance.uuid}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        domain_fee=request.data.get('total_fees',0)
        total_amount_to_pay=round(float(domain_fee)+float(domain_fee)*0.18)
        fee_discount=request.data.get('fee_discount',0)

        invoice_data={
            'course':course_fees.id,
            'installment_number':invoices,
            'current_paid_amount':current_payment,
            "current_paid_amount_with_gst":current_payment_with_gst,
            'mode_of_payment':payment_mode
        }

        serializer=InvoiceSerializer(data=invoice_data)
        if serializer.is_valid():
            course_fees.paid_amount=course_fees.paid_amount+float(current_payment)
            course_fees.domain_fee=domain_fee
            course_fees.fee_discount=fee_discount
            course_fees.amount_with_gst=float(total_amount_to_pay)
            course_obj=course_fees.save()
            invoice_instance=serializer.save()

            template = "./base.html"
            recipient = course_obj.profile.email
            subject = "Payment Completed"
            content = 'Your payment is done'
            pdf_content = {'invoice':invoice_instance,'client':course_obj.profile}

            email_thread = threading.Thread(target=send_email, args=(template, subject, content, recipient), kwargs={'pdf_content': pdf_content})
            email_thread.start()
            return Response({'message': 'Fee paid successfully', 'invoice_id': invoice_instance.uuid}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


                            ## INVOICES ## 

## List invoices
class InvoiceListAPIView(ListAPIView):
    serializer_class = InvoiceListSerializer
    # permission_classes = []
    # pagination_class = CustomPagination  

    def get_queryset(self):
        payment_status = self.request.query_params.get('status')
        date = self.request.query_params.get('date')
        year = self.request.query_params.get('year')
        uuid = self.request.query_params.get('course_uuid')
        print(uuid)

        queryset = Invoice.objects.filter(course__uuid=uuid)
        if payment_status=='paid':
            queryset=queryset.filter(payment_status=PaymentStatus.PAID)
        elif payment_status=='partial':
            queryset=queryset.filter(payment_status=PaymentStatus.PARTIALLY_PAID)
        elif payment_status=='unpaid':
            queryset=queryset.filter(payment_status=PaymentStatus.UNPAID)

        if date:
            try:
                queryset = queryset.filter(invoice_date=date)
            except ValueError:
                queryset = queryset.none()
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(invoice_date__year=year)
            except ValueError:
                queryset = queryset.none()
        return queryset


## update invoice
class UpdateInvoice(APIView):
    def get(self,request):
        invoice_uuid=request.GET.get('invoice_uuid')
        obj=get_object_or_404(Invoice,uuid=invoice_uuid)
        serializer=ViewInvoiceSerializer(obj)
        course_serializer=CourseFeesSerializer(obj.course)
        profile=obj.course.profile
        user={
            'name':profile.first_name,
            'phone':profile.phone,
            'email':profile.email,
            'address_line1':profile.address_line1,
            'city':profile.city,
            'state':profile.state,
            'zip_code':profile.zip_code,
        }
        if serializer:
            return Response({'data':serializer.data,'user':user,'course':course_serializer.data}, status=status.HTTP_200_OK)
        return Response({'message':'no data found'}, status=status.HTTP_400_BAD_REQUEST)


## download invoice
class InvoiceDownloadAPIView(APIView):
    serializer_class = InvoiceSerializer
    http_method_names = ['get']

    def get(self, request, format=None):
        user = request.user
        uuid = request.query_params.get('invoice_uuid', None)
        invoice_data=get_object_or_404(Invoice,uuid=uuid)
        client=invoice_data.course.profile
        print(invoice_data.course.course.course_name)
      
        if invoice_data:
            content= {'invoice':invoice_data,'client':client}
            template = './invoice.html'
            filename = 'invoice-'+str(date.today())
            ### option set for portrait and landscape landscape-1,portrait-2
            option=1
            pdf_response = generate_pdf(content, template, filename, option)
            return pdf_response
        else:
            return Response({'message': 'invoice download failed '}, status=status.HTTP_400_BAD_REQUEST)




                              ## ADMISSIONS ##

## List admissions and fees
class AdmissionsListAPIView(ListAPIView):
    serializer_class = CourseFeesSerializer
    # permission_classes = []
    # pagination_class = CustomPagination  

    def get_queryset(self):
        payment_completed = self.request.query_params.get('payment_completed')
        date = self.request.query_params.get('joined_date')
        year = self.request.query_params.get('joined_year')
        course = self.request.query_params.get('course_uuid')
        course_type = self.request.query_params.get('course_type')

        queryset = CourseFees.objects.all()
        if course:
            queryset=queryset.filter(course_course_uuid=course)

        if payment_completed=='true':
            queryset=queryset.filter(payment_completed=True)

        if course_type:
            queryset = queryset.filter(course__course_type=course_type)


        if date:
            try:
                queryset = queryset.filter(created_at=date)
            except ValueError:
                queryset = queryset.none()
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(created_at__year=year)
            except ValueError:
                queryset = queryset.none()
        return queryset


                                 ## COURSES ##

## add course
class CreateACourseAPIView(CreateAPIView):
    queryset = Course.objects.filter(active_status=True)
    serializer_class=CoursesSerializer
    # permission_classes=[IsAdmin]

    def perform_create(self, serializer):
        return serializer.save()


## update course
class UpdateCourseAPIView(APIView):
    # permission_classes = [IsAdmin]

    def post(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(Course, pk=pk, active_status=True)

        serializer = CoursesSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


## List courses
class CoursesListAPIView(ListAPIView):
    serializer_class = CoursesSerializer
    # permission_classes = []
    # pagination_class = CustomPagination  

    def get_queryset(self):
        course_type = self.request.query_params.get('course_type')

        queryset = Course.objects.filter(active_status=True)
        if course_type:
            queryset = queryset.filter(course_type=course_type)
        return queryset

## List coursefees
class CoursesFeesListAPIView(ListAPIView):
    serializer_class = ListCourseFeesSerializer
    # permission_classes = []
    # pagination_class = CustomPagination  

    def get_queryset(self):
        payment_completed = self.request.query_params.get('payment_completed')
        course = self.request.query_params.get('course_uuid')
        email = self.request.query_params.get('email')
        is_new_user = self.request.query_params.get('is_new_user')
        

        queryset = CourseFees.objects.all()

        print(is_new_user)
        if is_new_user == 'true':
            queryset = queryset.filter(
            invoices__isnull=True 
         ).distinct()
        else:
            queryset = queryset.filter(
            invoices__isnull=False 
         ).distinct()
            

        if course:
            queryset=queryset.filter(course__uuid=course)

        if payment_completed=='true':
            queryset=queryset.filter(payment_completed=True)
        elif payment_completed=='false':
            queryset=queryset.filter(payment_completed=False)
 
        if email:
            queryset = queryset.filter(profile__email__contains=email)
        return queryset

    

class GetACourseFeesAPIView(APIView):
    def get(self,request):
        uuid=request.GET.get('uuid')
        obj=get_object_or_404(CourseFees,uuid=uuid)
        serializer=ListCourseFeesSerializer(obj)
        if serializer:
            return Response({'data':serializer.data}, status=status.HTTP_200_OK)
        return Response({'message':'no data found in this uuid'}, status=status.HTTP_400_BAD_REQUEST)
   

def get_financial_year():
    now = datetime.now()
    
    if now.month >= 4:
        start_year = now.year
        end_year = now.year + 1
    else:
        start_year = now.year - 1
        end_year = now.year
    
    start_date = datetime(start_year, 4, 1)
    end_date = datetime(end_year, 3, 31)
    return start_date, end_date


from django.db.models import Sum
## Graph data
class GetGraphDataAPIView(APIView):
    def get(self,request):
        month_dict = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December'
        }

        start_date, end_date = get_financial_year()
        invoices = Invoice.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        if invoices:
            month_data=[]
            for num in range(1,13):
                amount=0
                data = invoices.filter(invoice_date__month=num).aggregate(total_paid_amount=Sum('current_paid_amount_with_gst'))
                amount = data.get('total_paid_amount', 0)

                month_data.append({
                    'month': month_dict[num],
                    'completed': amount
                })

            return Response(month_data, status=status.HTTP_200_OK)
        return Response({'message':'no data found'}, status=status.HTTP_400_BAD_REQUEST)
   