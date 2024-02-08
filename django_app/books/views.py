from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from books.models import Book
from books.serializers import BookSerializer


@api_view(['GET', 'POST'])
def get_books(request):
    """
    List all books, or create a new book.
    """
    if request.method == 'GET':
        books = search_and_sort_books(request)
        serializer = BookSerializer(books, many=True)
        return Response({
            'books': serializer.data
        })

    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT'])
def update_book(request, id):
    try:
        book = Book.objects.get(pk=id)
    except Book.DoesNotExist:
        return Response("book with id: %d was not found" % id, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = BookSerializer(book, many=True)
        return Response(serializer.data)
    
    serializer = BookSerializer(book, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def search_and_sort_books(req):
    # Construct base queryset
    queryset = Book.objects.all()

    q_params = req.GET.dict()

    if 'title' in q_params:
        queryset = queryset.filter(title__exact=q_params['title'])
    elif 'author' in q_params:
        queryset = queryset.filter(author__exact=q_params['author'])
    elif 'genre' in q_params:
        queryset = queryset.filter(genre__exact=q_params['genre'])

    sorting_order = q_params.get('order', 'asc').lower()
    # Apply sorting order
    if 'sort' in q_params:
        # If sorting order is not provided, assume ascending
        if sorting_order == 'desc':
            queryset = queryset.order_by('-' + q_params['sort'], 'id')
        else:
            queryset = queryset.order_by(q_params['sort'], 'id')
    else:
        # Default sorting by ID in ascending order
        queryset = queryset.order_by('-id' if sorting_order == 'desc' else 'id')

    return queryset