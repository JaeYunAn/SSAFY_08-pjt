from rest_framework import serializers

from .models import Book, Category, Comment, Thread


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


class ThreadTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    thread = ThreadTitleSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class ThreadDetailSerializer(serializers.ModelSerializer):
    book = BookTitleSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    num_of_comments = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Thread
        fields = '__all__'
