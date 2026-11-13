from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Book, Category, Comment, Thread
from .serializers import (
    BookListSerializer,
    BookSerializer,
    CategorySerializer,
    CommentSerializer,
    ThreadDetailSerializer,
    ThreadListSerializer,
    ThreadSerializer,
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


@api_view(['POST'])
def create_thread(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    serializer = ThreadSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(book=book)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_comment(request, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(thread=thread)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def comment_detail(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    if request.method == 'GET':
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CommentSerializer(comment, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        comment.delete()
        data = {'message': f'comment {comment_pk} is deleted.'}
        return Response(data, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def book_search(request):
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'message': '검색어를 입력해주세요.'})

    books = Book.objects.filter(
        Q(title__icontains=query) | Q(author__icontains=query)
    )
    serializer = BookListSerializer(books, many=True)
    return Response(serializer.data)
