from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Book, Category, Thread
from .serializers import (
    BookListSerializer,
    BookSerializer,
    CategorySerializer,
    ThreadDetailSerializer,
    ThreadListSerializer,
)


@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()
    serializer = BookListSerializer(books, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def book_detail(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    serializer = BookSerializer(book)
    return Response(serializer.data)


@api_view(['GET'])
def thread_list(request):
    threads = Thread.objects.all()
    serializer = ThreadListSerializer(threads, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def thread_detail(request, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)

    if request.method == 'GET':
        serializer = ThreadDetailSerializer(thread)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ThreadDetailSerializer(thread, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        thread.delete()
        data = {'message': f'thread {thread_pk} is deleted.'}
        return Response(data, status=status.HTTP_204_NO_CONTENT)
