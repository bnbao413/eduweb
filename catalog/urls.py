from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('textbook/<int:textbook_id>/', views.textbook_detail, name='textbook_detail'),
    path('notes/<int:notes_id>/', views.notes_detail, name='notes_detail'),
    path('pratice/<int:practice_id>/', views.practice_detail, name='practice_detail'),
    path('unit-test/<int:test_id>/', views.unit_test_detail, name='unit_test_detail'),
    path('textbook/<int:textbook_id>/edit/', views.textbook_edit, name='textbook_edit'),
]

