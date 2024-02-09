from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .serializers import *


@swagger_auto_schema(
    method='POST',
    request_body=UserSerializer, 
    responses={
        201: UserSerializer,
    }
)
@api_view(['POST'])
def users_root(request):
    """
    List all users, or create a new user.
    """
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@swagger_auto_schema(
    method='GET',
    request_body=None, 
    responses={
        200: openapi.Schema(type=openapi.TYPE_OBJECT, properties= {}),
    }
)
@swagger_auto_schema(
    method='PUT',
    request_body=WalletSerializer, 
    responses={
        200: openapi.Schema(type=openapi.TYPE_OBJECT, properties= {}),
    }
)
@api_view(['GET', 'PUT'])
def get_wallet(request, wallet_id):
    try:
        user = User.objects.get(pk=wallet_id)
    except ObjectDoesNotExist:
        return Response({
            "message": "wallet with id: %d was not found" % wallet_id
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        serializer = WalletSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        amount = serializer.data['recharge']
        if amount < 100 or amount > 10000:
            return Response({
                "message": "invalid amount: %d" % amount
            }, status=status.HTTP_400_BAD_REQUEST)
        user.balance += amount
        user.save()
    return Response({
        "wallet_id": user.user_id,
        "balance": user.balance,
        "wallet_user": {
            "user_id": user.user_id,
            "user_name": user.user_name
        }
    })

