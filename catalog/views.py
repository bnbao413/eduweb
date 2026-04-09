import markdown
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, TextbookPage, NotesPage, PracticeSet, UnitTest
from .forms import TextbookPageForm

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
    page = get_object_or_404(TextbookPage, id=textbook_id)
    html_content = markdown.markdown(page.content)

    previous_page = TextbookPage.objects.filter(
        unit=page.unit,
        order__lt=page.order
    ).order_by('-order').first()

    next_page = TextbookPage.objects.filter(
        unit=page.unit,
        order__gt=page.order
    ).order_by('order').first()

    all_pages = TextbookPage.objects.filter(
        unit=page.unit
    ).order_by('order')

    return render(request, 'catalog/textbook_detail.html', {
        'page': page,
        'html_content': html_content,
        'previous_page': previous_page,
        'next_page': next_page,
        'all_pages': all_pages,
    })



def notes_detail(request, notes_id):
    note = get_object_or_404(
        NotesPage.objects.select_related('unit__course'),
        id=notes_id
    )
    return render(request, 'catalog/notes_detail.html', {'note': note})

def practice_detail(request, practice_id):
    practice = get_object_or_404(
        PracticeSet.objects.select_related('unit__course'),
        id=practice_id
    )
    return render(request, 'catalog/practice_detail.html', {'practice': practice})

def unit_test_detail(request, test_id):
    unit_test = get_object_or_404(
        UnitTest.objects.select_related('unit__course'),
        id=test_id
    )
    return render(request, 'catalog/unit_test_detail.html', {'test': test})

def textbook_edit(request, textbook_id):
    page = get_object_or_404(TextbookPage, id=textbook_id)

    if request.method == 'POST':
        form = TextbookPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('textbook_detail', textbook_id=page.id)
    else:
        form = TextbookPageForm(instance=page)

    return render(request, 'catalog/textbook_edit.html', {
        'form': form,
        'page': page,
    })
