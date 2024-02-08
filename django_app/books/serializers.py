from rest_framework import serializers
from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required = False)
    class Meta():
        model = Book
        fields = "__all__"
    

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Book.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.author = validated_data.get('author', instance.author)
        instance.area = validated_data.get('area', instance.area)
        instance.genre = validated_data.get('genre', instance.genre)
        instance.price = validated_data.get('price', instance.price)
        instance.save()
        return instance
    

class BookSeachQuery(serializers.Serializer):
    title = serializers.CharField(required = False)
    author = serializers.CharField(required = False)
    genre = serializers.CharField(required = False)
    sort = serializers.ChoiceField(choices=['title', 'author', 'genre', 'price'], required = False)
    order = serializers.ChoiceField(choices=['ASC', 'DESC'], required = False)
    

class BookSearchResponse(serializers.Serializer):
    books = BookSerializer(many = True)

class BookNotFound(serializers.Serializer):
    error = serializers.CharField()

class InvalidBookData(serializers.Serializer):
    title = serializers.ListField(child = serializers.CharField(), required = False)
    author = serializers.ListField(child = serializers.CharField(), required = False)
    genre = serializers.ListField(child = serializers.CharField(), required = False)
    area = serializers.ListField(child = serializers.CharField(), required = False)
    price  = serializers.ListField(child = serializers.CharField(), required = False)