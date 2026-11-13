from django.urls import path

from . import views

urlpatterns = [
    path('categories/', views.category_list),
    path('books/', views.book_list),
    path('books/<int:book_pk>/', views.book_detail),
    path('books/<int:book_pk>/threads/', views.create_thread),
    path('threads/', views.thread_list),
    path('threads/<int:thread_pk>/', views.thread_detail),
    path('threads/<int:thread_pk>/comments/', views.create_comment),
    path('comments/<int:comment_pk>/', views.comment_detail),
]
