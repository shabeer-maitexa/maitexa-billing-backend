from django.urls import path
from . import views

urlpatterns = [
    path('registration/',views.RegisterUserAPIView.as_view()),
    path('pay-fee/',views.PayInstallmentAPIView.as_view()),

    path('list-invoice/',views.InvoiceListAPIView.as_view()),
    path('update-invoice/',views.UpdateInvoice.as_view()),
    path('download-invoice/',views.InvoiceDownloadAPIView.as_view()),

    path('list-admissions/',views.AdmissionsListAPIView.as_view()),
    path('list-coursefees/',views.CoursesFeesListAPIView.as_view()),
    path('get-a-coursefees/',views.GetACourseFeesAPIView.as_view()),

    path('create-a-course/',views.CreateACourseAPIView.as_view()),
    path('update-a-course/<int:pk>/',views.UpdateCourseAPIView.as_view()),
    path('list-courses/',views.CoursesListAPIView.as_view()),

    path('graph/',views.GetGraphDataAPIView.as_view()),
]