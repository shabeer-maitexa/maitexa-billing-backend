from .models import *
from rest_framework import serializers
from dateutil.relativedelta import relativedelta



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'email']

class CourseFeesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFees
        fields='__all__'
    
class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields ='__all__'


    
class InvoiceListSerializer(serializers.ModelSerializer):
    first_name=serializers.SerializerMethodField()
    email = serializers.CharField(source='course.profile.email',read_only=True)

    class Meta:
        model = Invoice
        fields ='__all__'

    def get_first_name(self,obj):
        return obj.course.profile.first_name



class CoursesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields ='__all__'

## list course fees serializer
class ListCourseFeesSerializer(serializers.ModelSerializer):
    payement_status=serializers.SerializerMethodField()
    current_installment=serializers.SerializerMethodField()
    is_new_payment=serializers.SerializerMethodField()
    email = serializers.EmailField(source='profile.email')
    course_name = serializers.CharField(source='course.course_name')
    user_name = serializers.CharField(source='profile.first_name')
    last_name = serializers.CharField(source='profile.last_name')
    phone = serializers.CharField(source='profile.phone')

    class Meta:
        model = CourseFees
        fields ='__all__'
        depth=2
    
    def get_payement_status(self,obj):
        if obj.amount_with_gst and obj.amount_with_gst-obj.paid_amount<= 0:
            return 'Paid'
        else:
            return 'Unpaid' 

    def get_current_installment(self,obj):
        return Invoice.objects.filter(course=obj).exists()

    def get_is_new_payment(self,obj):
        return True if not Invoice.objects.filter(course=obj).exists() else False


from .utils import convert_to_words
## view invoice
class ViewInvoiceSerializer(serializers.ModelSerializer):
    amount_in_words = serializers.SerializerMethodField()
    installment_count = serializers.SerializerMethodField()
    joining_date = serializers.SerializerMethodField()
    course_duration = serializers.SerializerMethodField()
    class Meta:
        model = Invoice
        fields ='__all__'
        depth=2  

    def get_amount_in_words(self,obj):
        amount=convert_to_words(int(obj.current_paid_amount_with_gst))
        return amount
    
    def get_installment_count(self,obj):
        course=obj.course
        invoices=Invoice.objects.filter(course=course).count()
        if course.balance==0 and invoices==1:    
            return 0
        return obj.installment_number 

    def get_joining_date(self,obj):
        course=obj.course
        invoices=Invoice.objects.filter(course=course).first()
        return invoices.invoice_date
    
    def get_course_duration(self, obj):
        course = obj.course
        months = int(course.course.course_duration)
        invoices = Invoice.objects.filter(course=course).first()
        
        if invoices and invoices.invoice_date:
            start_date = invoices.invoice_date
            end_date = start_date + relativedelta(months=months)
            return end_date
        return None 