import json
import markdown

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import (
    Course, Lesson, TextbookPage, NotesPage, PracticeSet, UnitTest, FinalExam,
    VideoCheckpoint, CheckpointChoice, CheckpointResponse,
)
from .forms import TextbookPageForm, NotesPageForm

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

    unit = lesson.unit

    prev_lesson = Lesson.objects.filter(
        unit=unit, order__lt=lesson.order
    ).order_by('-order').first()

    next_lesson = Lesson.objects.filter(
        unit=unit, order__gt=lesson.order
    ).order_by('order').first()

    # Build checkpoint data — is_correct is intentionally NOT included here.
    # Answer validation happens server-side via the check_checkpoint endpoint.
    checkpoints_data = []
    for cp in lesson.checkpoints.prefetch_related('choices').order_by('timestamp'):
        checkpoints_data.append({
            'id': cp.id,
            'timestamp': cp.timestamp,
            'question': cp.question,
            'choices': [
                {'id': c.id, 'text': c.text}
                for c in cp.choices.all()
            ],
        })

    total_checkpoints = len(checkpoints_data)

    # For logged-in users, load which checkpoints they have already completed
    # so the page initialises with correct progress and doesn't re-trigger them.
    answered_ids = []
    completed_count = 0

    if request.user.is_authenticated and total_checkpoints > 0:
        answered_ids = list(
            CheckpointResponse.objects.filter(
                user=request.user,
                checkpoint__lesson=lesson,
            ).values_list('checkpoint_id', flat=True)
        )
        completed_count = len(answered_ids)

    lesson_completed = (total_checkpoints > 0 and completed_count == total_checkpoints)

    return render(request, 'catalog/lesson_detail.html', {
        'lesson': lesson,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson,
        'checkpoints_json': json.dumps(checkpoints_data),
        'answered_ids_json': json.dumps(answered_ids),
        'total_checkpoints': total_checkpoints,
        'completed_count': completed_count,
        'lesson_completed': lesson_completed,
    })


@require_POST
def check_checkpoint(request):
    """
    Validates a student's checkpoint answer server-side and saves the response.

    Accepts JSON: { checkpoint_id: int, choice_id: int|null }
    choice_id is null for reflection checkpoints (no choices).

    Saves a CheckpointResponse for authenticated users.
    Anonymous users receive validation feedback but nothing is persisted.

    Returns JSON: { correct: bool|null, feedback: str }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid request body.'}, status=400)

    checkpoint_id = data.get('checkpoint_id')
    choice_id     = data.get('choice_id')

    if not checkpoint_id:
        return JsonResponse({'error': 'checkpoint_id is required.'}, status=400)

    checkpoint = get_object_or_404(VideoCheckpoint, id=checkpoint_id)

    selected_choice = None
    is_correct      = None
    feedback        = ''

    if choice_id is not None:
        # Multiple-choice checkpoint: validate the selected answer.
        selected_choice = get_object_or_404(
            CheckpointChoice, id=choice_id, checkpoint=checkpoint
        )
        is_correct = selected_choice.is_correct

        if is_correct:
            feedback = 'Correct!'
        else:
            correct = checkpoint.choices.filter(is_correct=True).first()
            correct_text = f'"{correct.text}"' if correct else 'the correct option'
            feedback = f'Not quite. The correct answer is {correct_text}.'
    # else: reflection checkpoint — no answer to grade, no feedback needed.

    # Persist response for logged-in users.
    # update_or_create means a later attempt overwrites the earlier one.
    if request.user.is_authenticated:
        CheckpointResponse.objects.update_or_create(
            user=request.user,
            checkpoint=checkpoint,
            defaults={
                'selected_choice': selected_choice,
                'is_correct': is_correct,
            },
        )

    return JsonResponse({
        'correct': is_correct,
        'feedback': feedback,
    })

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
    page = get_object_or_404(NotesPage, id=notes_id)
    html_content = markdown.markdown(page.content)

    unit_pages = list(page.unit.notes_pages.all())

    index = unit_pages.index(page)

    prev_page = unit_pages[index - 1] if index > 0 else None
    next_page = unit_pages[index + 1] if index < len(unit_pages) - 1 else None

    return render(request, 'catalog/notes_detail.html', {
        'page': page,
        'html_content': html_content,
        'prev_page': prev_page,
        'next_page': next_page,
    })




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

def start_practice(request, practice_id):
    practice = get_object_or_404(
        PracticeSet.objects.select_related('unit__course'),
        id=practice_id
    )
    return render(request, 'catalog/start_practice.html', {
        'practice': practice,
    })




def start_unit_test(request, test_id):
    test = get_object_or_404(
        UnitTest.objects.select_related('unit__course'),
        id=test_id
    )
    return render(request, 'catalog/start_unit_test.html', {
        'test': test,
    })

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

