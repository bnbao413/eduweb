from django.contrib import admin
from django.contrib.auth.models import User, Group
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display  = ['username', 'email', 'is_staff', 'date_joined']
    list_editable = ['is_staff']
    list_filter   = ['is_staff']
    search_fields = ['username', 'email']
    readonly_fields = ['date_joined', 'last_login']
    fields = ['username', 'email', 'is_staff', 'date_joined', 'last_login']
    ordering = ['username']

    # Only superusers can view or touch the Users section at all.
    def has_module_perms(self, request, app_label=None):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

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

class UnitInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Unit
    extra = 1
    can_delete = True
    show_change_link = True
    readonly_fields = ['delete_link']

    def delete_link(self, obj):
        if obj.pk:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:catalog_unit_delete', args=[obj.pk])
            return format_html('<a href="{}" style="color:red;">Delete</a>', url)
        return ''
    delete_link.short_description = ''

@admin.register(Course)
class CourseAdmin(SortableAdminBase, admin.ModelAdmin):
    search_fields = ['title']
    inlines = [UnitInline]

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    ordering = ['course', 'order']
    search_fields = ['title', 'course__title']
    autocomplete_fields = ['course']

@admin.register(TextbookPage)
class TextbookPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit', 'order']
    list_filter = ['unit__course']
    ordering = ['unit', 'order']
    search_fields = ['title']
    autocomplete_fields = ['unit']

@admin.register(NotesPage)
class NotesPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit', 'order']
    list_filter = ['unit__course']
    ordering = ['unit', 'order']
    search_fields = ['title']
    autocomplete_fields = ['unit']

@admin.register(PracticeSet)
class PracticeSetAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit', 'order']
    list_filter = ['unit__course']
    ordering = ['unit', 'order']
    search_fields = ['title']
    autocomplete_fields = ['unit']

@admin.register(UnitTest)
class UnitTestAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit']
    list_filter = ['unit__course']
    search_fields = ['title']
    autocomplete_fields = ['unit']

@admin.register(FinalExam)
class FinalExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'course']
    search_fields = ['title']
    autocomplete_fields = ['course']


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
    search_fields = ['title']
    autocomplete_fields = ['unit']
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
    search_fields = ['question', 'lesson__title']
    autocomplete_fields = ['lesson']
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