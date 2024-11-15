from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('login/',views.Login.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('web-registration/',views.WebRegistrationAPIView.as_view(), name='register-user'),
    path('list-students/',views.GetRegisterdUsersAPIView.as_view(), name='registered_students'),
]