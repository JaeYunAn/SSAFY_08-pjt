from django.urls import path

from . import views

urlpatterns = [
    path('categories/', views.category_list),
    path('books/', views.book_list),
    path('books/<int:book_pk>/', views.book_detail),
]
