from rest_framework import serializers
from .models import User
from drf_yasg import openapi

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    class Meta():
        model = User
        fields = "__all__"


    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.user_id = validated_data.get('user_id', instance.user_id)
        instance.user_name = validated_data.get('user_name', instance.user_name)
        instance.balance = validated_data.get('balance', instance.balance)
        instance.save()
        return instance

class WalletSerializer(serializers.Serializer):
    recharge = serializers.IntegerField()


UserNotFound = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(
            type=openapi.TYPE_STRING
        )
    }
)