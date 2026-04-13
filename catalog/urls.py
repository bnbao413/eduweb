from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/register/', views.register, name='register'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('textbook/<int:textbook_id>/', views.textbook_detail, name='textbook_detail'),
    path('notes/<int:notes_id>/', views.notes_detail, name='notes_detail'),
    path('practice/<int:practice_id>/', views.practice_detail, name='practice_detail'),
    path('unit-test/<int:test_id>/', views.unit_test_detail, name='unit_test_detail'),
    path('textbook/<int:textbook_id>/edit/', views.textbook_edit, name='textbook_edit'),
    path('notes/<int:notes_id>/edit/', views.notes_edit, name='notes_edit'),
    path('practice/<int:practice_id>/start/', views.start_practice, name='start_practice'),
    path('unit-test/<int:test_id>/start/', views.start_unit_test, name='start_unit_test'),
    path('final-exam/<int:exam_id>/', views.final_exam_detail, name='final_exam_detail'),
    path('final-exam/<int:exam_id>/start/', views.start_final_exam, name='start_final_exam'),
    path('lesson/checkpoint/check/', views.check_checkpoint, name='check_checkpoint'),


    

]

