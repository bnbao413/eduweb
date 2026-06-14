import markdown
import re

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST


def page_not_found(request, exception):
    return render(request, '404.html', status=404)


def server_error(request):
    return render(request, '500.html', status=500)


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.db import IntegrityError
from .models import (
    Subject, Course, TextbookPage, NotesPage, PracticeSet, UnitTest, FinalExam,
)
from .forms import TextbookPageForm, NotesPageForm, RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                return redirect('home')
            except IntegrityError:
                form.add_error('username', 'That username is already taken. Please choose another.')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    subjects = Subject.objects.all()
    return render(request, 'catalog/home.html', {'subjects': subjects})

def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    courses = subject.courses.all()
    return render(request, 'catalog/subject_detail.html', {'subject': subject, 'courses': courses})

@staff_member_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('home')
    return render(request, 'catalog/course_confirm_delete.html', {'course': course})


def course_detail(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related(
            'units__textbook_pages',
            'units__notes_pages',
            'units__practice_sets',
        ),
        id=course_id
    )
    return render(request, 'catalog/course_detail.html', {'course': course})


def textbook_detail(request, textbook_id):
    page = get_object_or_404(TextbookPage, id=textbook_id)

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
        'raw_content': page.content,
        'previous_page': previous_page,
        'next_page': next_page,
        'all_pages': all_pages,
    })



def notes_detail(request, notes_id):
    page = get_object_or_404(NotesPage, id=notes_id)

    unit_pages = list(page.unit.notes_pages.all())

    index = unit_pages.index(page)

    prev_page = unit_pages[index - 1] if index > 0 else None
    next_page = unit_pages[index + 1] if index < len(unit_pages) - 1 else None

    return render(request, 'catalog/notes_detail.html', {
        'page': page,
        'raw_content': page.content,
        'prev_page': prev_page,
        'next_page': next_page,
    })




@staff_member_required
def notes_edit(request, notes_id):
    page = get_object_or_404(NotesPage, id=notes_id)


    if request.method == 'POST':
        form = NotesPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('notes_detail', notes_id=page.id)
    else:
        form = NotesPageForm(instance=page)


    return render(request, 'catalog/notes_edit.html', {
        'form': form,
        'page': page,
    })


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
    return render(request, 'catalog/unit_test_detail.html', {'test': unit_test})

def start_practice(request, practice_id):
    practice = get_object_or_404(
        PracticeSet.objects.select_related('unit__course'),
        id=practice_id
    )
    return render(request, 'catalog/start_practice.html', {'practice': practice})

def start_unit_test(request, test_id):
    test = get_object_or_404(
        UnitTest.objects.select_related('unit__course'),
        id=test_id
    )
    return render(request, 'catalog/start_unit_test.html', {'test': test})

def final_exam_detail(request, exam_id):
    exam = get_object_or_404(
        FinalExam.objects.select_related('course'),
        id=exam_id
    )
    return render(request, 'catalog/final_exam_detail.html', {'exam': exam})

def start_final_exam(request, exam_id):
    exam = get_object_or_404(
        FinalExam.objects.select_related('course'),
        id=exam_id
    )
    return render(request, 'catalog/start_final_exam.html', {'exam': exam})

# ---------------------------------------------------------------------------
# PDF export — serialized preview DOM (KaTeX already rendered) → Playwright PDF
# ---------------------------------------------------------------------------

@staff_member_required
@require_POST
def export_pdf(request):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return HttpResponse(
            'playwright not installed.\nRun: pip install playwright && playwright install chromium',
            status=500, content_type='text/plain',
        )

    rendered_html = request.POST.get('rendered_html', '')
    title = request.POST.get('title', 'document').strip() or 'document'

    if not rendered_html:
        return HttpResponse('rendered_html is required', status=400, content_type='text/plain')

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            pg = browser.new_page()
            pg.set_content(rendered_html, wait_until='domcontentloaded')
            pdf_bytes = pg.pdf(
                format='Letter',
                margin={'top': '1in', 'right': '1in', 'bottom': '1in', 'left': '1in'},
                print_background=True,
            )
            browser.close()
    except Exception as e:
        return HttpResponse(
            f'Playwright/Chromium error:\n{e}',
            status=500, content_type='text/plain',
        )

    fname = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_') or 'document'
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{fname}.pdf"'
    return response


@staff_member_required
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


