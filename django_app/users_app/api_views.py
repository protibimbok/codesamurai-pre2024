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


