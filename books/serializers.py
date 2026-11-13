from rest_framework import serializers

from .models import Book, Category, Thread


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'title', 'author', 'isbn', 'cover')


class BookThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('id', 'title', 'content', 'reading_date')


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    threads = BookThreadSerializer(many=True, read_only=True)
    num_of_threads = serializers.IntegerField(source='threads.count', read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class BookTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title',)


class ThreadListSerializer(serializers.ModelSerializer):
    book = BookTitleSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'title', 'book')
