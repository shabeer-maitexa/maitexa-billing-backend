from django.db import models
from authentication.models import Profile,BaseClass


class PaymentModes(models.TextChoices):
    CREDIT_CARD = 'credit_card', 'Credit Card'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    CASH = 'cash', 'Cash'
    CHEQUE = 'cheque', 'Cheque'
    UPI = 'upi', 'Upi'


class PaymentStatus(models.TextChoices):
    PAID = 'Paid', 'Paid'
    PARTIALLY_PAID = 'partially_paid', 'Partially Paid'
    UNPAID = 'Unpaid', 'Unpaid'


class Course(BaseClass):
    course_name = models.CharField(max_length=255)
    course_description = models.TextField(blank=True, null=True)
    course_duration = models.CharField(max_length=100)
    course_type = models.CharField(max_length=50, choices=[
        ('internship', 'internship'),
        ('academic', 'Academic'),
    ])
    def __str__(self):
        return self.course_name


class CourseFees(BaseClass):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='courses',null=True,blank=True)
    course = models.ForeignKey('Course',on_delete=models.SET_NULL,null=True,blank=True)
    domain_fee = models.FloatField(default=0.0)
    fee_discount = models.FloatField(default=0.0)
    number_of_installments = models.PositiveIntegerField(default=0)
    is_installment = models.BooleanField(default=False)
    paid_amount = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)
    payment_completed=models.BooleanField(default=False)
    amount_with_discount = models.FloatField(default=0.0)
    amount_with_gst=models.FloatField(default=0.0)


    def fee_with_discount(self):
        domain_fee = float(self.domain_fee)
        fee_discount = float(self.fee_discount)
        return domain_fee - fee_discount


    def calculate_balance(self):
        if self.paid_amount > self.amount_with_gst:
            return 0
        return self.amount_with_gst - self.paid_amount
    
    def payment_status_update(self):
        if self.paid_amount > self.amount_with_gst:
            return True
        return True if self.paid_amount - self.amount_with_gst  == 0 else False

    def save(self, *args, **kwargs):
        self.amount_with_discount=self.fee_with_discount()
        self.balance = self.calculate_balance()
        self.payment_completed=self.payment_status_update()
        super().save(*args, **kwargs)
        return self

    def __str__(self):
        return f" {self.profile.email}"

    class Meta:
        verbose_name='Course fees'  
        verbose_name_plural='Course fees'  


class Invoice(BaseClass):
    # profile = models.ForeignKey('authentication.Profile', on_delete=models.CASCADE, related_name='invoices')
    # client = models.ForeignKey('ClientDetails', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    # project = models.ForeignKey('Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    
    course = models.ForeignKey('CourseFees', on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    invoice_date = models.DateTimeField(auto_now_add=True)
    current_paid_amount = models.FloatField(default=0.0)
    current_paid_amount_with_gst = models.FloatField(default=0.0)
    installment_number=models.IntegerField(default=1)
    mode_of_payment = models.CharField(max_length=50, choices=PaymentModes.choices,null=True,blank=True)


    def __str__(self):
        return f"Invoice #{self.id} - {self.course.profile.email if self.course else 'unknown user'}"

    class Meta:
        verbose_name='Invoice'  
        verbose_name_plural='Invoice'  



