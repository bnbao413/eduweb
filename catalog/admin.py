from django.contrib import admin
from .models import (
    Course,
    Unit,
    Lesson,
    TextbookPage,
    NotesPage,
    PracticeSet,
    UnitTest,
    FinalExam,
    VideoCheckpoint,
    CheckpointChoice,
    CheckpointResponse,
)

admin.site.register(Course)
admin.site.register(Unit)
admin.site.register(TextbookPage)
admin.site.register(NotesPage)
admin.site.register(PracticeSet)
admin.site.register(UnitTest)
admin.site.register(FinalExam)


class VideoCheckpointInline(admin.TabularInline):
    """
    Shows a lesson's checkpoints as a quick summary on the Lesson edit page.
    To add/edit choices for a checkpoint, save the lesson first then click
    through to the checkpoint from the VideoCheckpoints admin section.
    """
    model = VideoCheckpoint
    extra = 1
    fields = ['timestamp', 'question', 'order']
    ordering = ['timestamp']
    show_change_link = True  # adds a link to the checkpoint's own edit page


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit', 'order', 'is_published', 'duration']
    list_filter = ['unit__course', 'is_published']
    list_editable = ['order', 'is_published']
    ordering = ['unit', 'order']
    inlines = [VideoCheckpointInline]
    fieldsets = [
        (None, {
            'fields': ['unit', 'title', 'order', 'is_published']
        }),
        ('Description', {
            'fields': ['content']
        }),
        ('Video', {
            'fields': ['video_url', 'video_file', 'thumbnail', 'duration'],
            'description': (
                'For video_url, use an embed URL: '
                'YouTube → https://www.youtube.com/embed/VIDEO_ID  |  '
                'Vimeo → https://player.vimeo.com/video/VIDEO_ID. '
                'If both are filled, video_url takes priority. '
                'Note: timestamp checkpoints only work with uploaded video files, not embed URLs.'
            ),
        }),
        ('Transcript', {
            'fields': ['transcript'],
            'classes': ['collapse'],
        }),
    ]


class CheckpointChoiceInline(admin.TabularInline):
    model = CheckpointChoice
    extra = 3
    fields = ['text', 'is_correct', 'order']


@admin.register(VideoCheckpoint)
class VideoCheckpointAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'timestamp', 'question_preview', 'choice_count']
    list_filter = ['lesson__unit__course', 'lesson']
    ordering = ['lesson', 'timestamp']
    inlines = [CheckpointChoiceInline]
    fields = ['lesson', 'timestamp', 'question', 'order']

    def question_preview(self, obj):
        return obj.question[:80] + '...' if len(obj.question) > 80 else obj.question
    question_preview.short_description = 'Question'

    def choice_count(self, obj):
        return obj.choices.count()
    choice_count.short_description = 'Choices'


@admin.register(CheckpointResponse)
class CheckpointResponseAdmin(admin.ModelAdmin):
    list_display  = ['user', 'checkpoint', 'is_correct', 'selected_choice', 'answered_at']
    list_filter   = ['is_correct', 'checkpoint__lesson__unit__course']
    search_fields = ['user__username', 'checkpoint__question']
    ordering      = ['-answered_at']
    readonly_fields = ['user', 'checkpoint', 'selected_choice', 'is_correct', 'answered_at']

    # Responses are records, not something you'd manually create from admin.
    def has_add_permission(self, request):
        return False