from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('editor/', views.general_editor, name='general_editor'),
    path('search/', views.search, name='search'),
    path('page-overlay/save/', views.page_overlay_save, name='page_overlay_save'),
    path('page-overlay/upload/', views.page_overlay_upload, name='page_overlay_upload'),
    path('theme/save/', views.theme_save, name='theme_save'),
    path('subject/<int:subject_id>/', views.subject_detail, name='subject_detail'),
    path('accounts/register/', views.register, name='register'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
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
    path('course/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),


    

]

