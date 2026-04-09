from django.shortcuts import render, get_object_or_404
from .models import Course, Lesson, TextbookPage, NotesPage

def home(request):
    courses = Course.objects.all()
    return render(request, 'catalog/home.html', {'courses': courses})

def course_detail(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            'units__lessons',
            'units__textbook_pages',
            'units__notes_pages',
            'units__practice_sets',
        ),
        id=course_id
    )
    return render(request, 'catalog/course_detail.html', {'course': course})

def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related('unit__course'),
        id=lesson_id
        
    )
    return render(request, 'catalog/lesson_detail.html', {'lesson': lesson})

def textbook_detail(request, textbook_id):
    page = get_object_or_404(
        TextbookPage.objects.select_related('unit__course'),
        id=textbook_id
    )
    return render(request, 'catalog/textbook_detail.html', {'page': page})

def notes_detail(request, notes_id):
    note = get_object_or_404(
        NotesPage.objects.select_related('unit__course'),
        id=notes_id
    )
    return render(request, 'catalog/notes_detail.html', {'note': note})