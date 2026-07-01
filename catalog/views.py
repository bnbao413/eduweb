import json
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
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import (
    Subject, Course, Unit, TextbookPage, NotesPage, PracticeSet, UnitTest, FinalExam,
    PageOverlay, SiteTheme,
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


@login_required
def general_editor(request):
    """Standalone math/markdown editor, open to any logged-in account
    (not staff-only, unlike the textbook/notes editors)."""
    return render(request, 'catalog/general_edit.html')


@staff_member_required
@require_POST
def page_overlay_save(request):
    """Save staff-placed overlay items (images/GIFs/text/link-buttons) for a page path."""
    from django.http import JsonResponse

    path = (request.POST.get('path') or '').strip()
    if not path or not path.startswith('/'):
        return HttpResponse('valid path required', status=400, content_type='text/plain')
    try:
        raw = json.loads(request.POST.get('items', '[]'))
        if not isinstance(raw, list):
            raise ValueError
    except (ValueError, TypeError):
        return HttpResponse('invalid items', status=400, content_type='text/plain')

    def _i(v, default=0):
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return default

    def _flip(v):
        return -1 if _i(v, 1) < 0 else 1

    clean = []
    for it in raw[:200]:                       # cap how many items per page
        if not isinstance(it, dict):
            continue
        t = it.get('type')
        geo = {'x': _i(it.get('x')), 'y': _i(it.get('y')),
               'rot': _i(it.get('rot')) % 360, 'fx': _flip(it.get('fx')), 'fy': _flip(it.get('fy'))}
        if t == 'image':
            url = str(it.get('url', ''))[:2000]
            if not url:
                continue
            clean.append({'type': 'image', 'url': url,
                          'w': _i(it.get('w'), 200), 'h': _i(it.get('h')), **geo})
        elif t == 'text':
            color = str(it.get('color', '')).strip()
            if not re.fullmatch(r'#[0-9A-Fa-f]{3,8}', color):
                color = ''                          # only a safe hex colour, else inherit
            size = _i(it.get('size'))
            size = max(8, min(400, size)) if size else 0
            font = str(it.get('font', ''))
            if font not in ('sans', 'serif', 'mono', 'cursive', 'fancy'):
                font = ''                           # whitelist → maps to a .po-font-* class
            clean.append({'type': 'text', 'text': str(it.get('text', ''))[:5000],
                          'w': _i(it.get('w'), 220), 'h': _i(it.get('h')),
                          'color': color, 'size': size, 'font': font, **geo})
        elif t == 'button':
            label = str(it.get('text', ''))[:300]
            url = str(it.get('url', '')).strip()[:2000]
            low = url.lower()
            # only safe link targets (staff-only, but still block javascript:/data: etc.)
            if url and not (url.startswith('/') or url.startswith('#')
                            or low.startswith('http://') or low.startswith('https://')
                            or low.startswith('mailto:')):
                url = ''
            color = str(it.get('color', '')).strip()
            if not re.fullmatch(r'#[0-9A-Fa-f]{3,8}', color):
                color = ''
            bg = str(it.get('bg', '')).strip()
            if not re.fullmatch(r'#[0-9A-Fa-f]{3,8}', bg):
                bg = ''
            size = _i(it.get('size'))
            size = max(8, min(400, size)) if size else 0
            font = str(it.get('font', ''))
            if font not in ('sans', 'serif', 'mono', 'cursive', 'fancy'):
                font = ''
            shape = str(it.get('shape', ''))
            if shape not in ('rect', 'round', 'pill', 'ellipse'):
                shape = 'round'
            clean.append({'type': 'button', 'text': label, 'url': url,
                          'w': _i(it.get('w'), 160), 'h': _i(it.get('h'), 48),
                          'color': color, 'bg': bg, 'size': size, 'font': font,
                          'shape': shape, **geo})

    PageOverlay.objects.update_or_create(path=path, defaults={'items': clean})
    return JsonResponse({'ok': True, 'count': len(clean)})


@staff_member_required
@require_POST
def page_overlay_upload(request):
    """Upload an image/GIF file for a page overlay; returns its media URL."""
    import os
    import uuid
    from django.http import JsonResponse
    from django.core.files.storage import default_storage

    f = request.FILES.get('file')
    if not f:
        return HttpResponse('no file', status=400, content_type='text/plain')
    if not (f.content_type or '').lower().startswith('image/'):
        return HttpResponse('only image / GIF files are allowed', status=400, content_type='text/plain')
    if f.size > 15 * 1024 * 1024:
        return HttpResponse('file too large (max 15 MB)', status=400, content_type='text/plain')

    ext = os.path.splitext(f.name)[1].lower()
    if ext not in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.svg', '.apng', '.avif'):
        ext = '.img'
    saved = default_storage.save('overlays/' + uuid.uuid4().hex + ext, f)
    return JsonResponse({'url': default_storage.url(saved)})


@staff_member_required
@require_POST
def theme_save(request):
    """Save the site-wide colour theme (staff only, from the Edit-page panel).
    Each posted field is kept only if it's a safe hex colour, else cleared so it
    falls back to the default palette. `reset=1` clears the whole theme."""
    from django.http import JsonResponse

    t = SiteTheme.objects.first() or SiteTheme()
    fields = ('bg', 'surface', 'surface_2', 'border', 'text', 'accent', 'on_accent')

    if request.POST.get('reset'):
        for f in fields:
            setattr(t, f, '')
    else:
        for f in fields:
            if f in request.POST:
                v = (request.POST.get(f) or '').strip()
                setattr(t, f, v if re.fullmatch(r'#[0-9A-Fa-f]{3,8}', v) else '')

    t.save()
    return JsonResponse({'ok': True})


def search(request):
    """Live site search across all content types; returns JSON for the
    front-page search box. Each result links straight to its page."""
    from django.http import JsonResponse
    from django.urls import reverse

    q = (request.GET.get('q') or '').strip()
    results = []
    if q:
        for s in Subject.objects.filter(title__icontains=q)[:6]:
            results.append({'title': s.title, 'type': 'Subject', 'context': '',
                            'url': reverse('subject_detail', args=[s.id])})
        for c in Course.objects.filter(title__icontains=q).select_related('subject')[:6]:
            results.append({'title': c.title, 'type': 'Course',
                            'context': c.subject.title if c.subject else '',
                            'url': reverse('course_detail', args=[c.id])})
        for u in Unit.objects.filter(title__icontains=q).select_related('course')[:6]:
            results.append({'title': u.title, 'type': 'Unit', 'context': u.course.title,
                            'url': reverse('course_detail', args=[u.course.id])})
        for p in TextbookPage.objects.filter(title__icontains=q).select_related('unit__course')[:8]:
            results.append({'title': p.title, 'type': 'Textbook',
                            'context': f'{p.unit.course.title} · {p.unit.title}',
                            'url': reverse('textbook_detail', args=[p.id])})
        for p in NotesPage.objects.filter(title__icontains=q).select_related('unit__course')[:8]:
            results.append({'title': p.title, 'type': 'Notes',
                            'context': f'{p.unit.course.title} · {p.unit.title}',
                            'url': reverse('notes_detail', args=[p.id])})
        for p in PracticeSet.objects.filter(title__icontains=q).select_related('unit__course')[:6]:
            results.append({'title': p.title, 'type': 'Practice',
                            'context': f'{p.unit.course.title} · {p.unit.title}',
                            'url': reverse('practice_detail', args=[p.id])})
        for t in UnitTest.objects.filter(title__icontains=q).select_related('unit__course')[:6]:
            results.append({'title': t.title, 'type': 'Unit test',
                            'context': f'{t.unit.course.title} · {t.unit.title}',
                            'url': reverse('unit_test_detail', args=[t.id])})
        for e in FinalExam.objects.filter(title__icontains=q).select_related('course')[:6]:
            results.append({'title': e.title, 'type': 'Final exam', 'context': e.course.title,
                            'url': reverse('final_exam_detail', args=[e.id])})
    return JsonResponse({'results': results})

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

# Export is available to any logged-in account so the public general editor can
# produce PDFs (the staff-only textbook/notes editors also use it).
@login_required
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
    page_format = request.POST.get('page_format', 'Letter')
    if page_format not in ('Letter', 'A4'):
        page_format = 'Letter'

    if not rendered_html:
        return HttpResponse('rendered_html is required', status=400, content_type='text/plain')

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            pg = browser.new_page()
            pg.set_content(rendered_html, wait_until='domcontentloaded')
            pdf_bytes = pg.pdf(
                format=page_format,
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


