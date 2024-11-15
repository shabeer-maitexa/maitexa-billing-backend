## Rest framework imports

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

## auth import 
from django.contrib.auth import authenticate

## serializer import
from .serializers import WebRegisterSerializer

## Other
from .models import RoleChoices,Profile


## Login api
class Login(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')

        user=authenticate(email=email,password=password)

        if user is None:
            return Response({'message':'invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)        

        token=RefreshToken.for_user(user)
        role=user.role
        data={
            'access':str(token.access_token),
            'refresh':str(token),
            'role':role
        }

        return Response({'data':data},status=status.HTTP_200_OK)
    

## Website registration
class WebRegistrationAPIView(APIView):
    serializer_class=WebRegisterSerializer
    # permission_classes=[]
    def post(self,request):
        data=request.data.copy()
        intern_or_project=data.get('intern_or_project_status')
        intern_or_project_title=data.get('intern_or_project_title')
        
        if intern_or_project=='intern':
            data['internship']=intern_or_project_title
        elif intern_or_project=='project':
            data['project_title'] =intern_or_project_title

        data['role']=RoleChoices.USER
        serializer=self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":'registration successfull'},status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class GetRegisterdUsersAPIView(APIView):
    serializer_class=WebRegisterSerializer
    def get(self,request):
        data_set=Profile.objects.all()
        serializer=self.serializer_class(data_set,many=True)
        if serializer:
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response({'message':'no student found'},status=status.HTTP_400_BAD_REQUEST)