## Rest framework imports

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

## auth import 
from django.contrib.auth import authenticate



class Login(APIView):
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')

        user=authenticate(email=email,password=password)

        if user is None:
            return Response({'message':'invalid credentials'},status=status.HTTP_400_BAD_REQUEST)        

        token=RefreshToken.for_user(user)
        role=user.role
        data={
            'access':str(token.access_token),
            'refresh':str(token),
            'role':role
        }

        return Response({'data':data},status=status.HTTP_200_OK)