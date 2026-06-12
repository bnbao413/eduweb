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
    Subject,
    Course,
    Unit,
    TextbookPage,
    NotesPage,
    PracticeSet,
    UnitTest,
    FinalExam,
)

class CourseInline(admin.TabularInline):
    model = Course
    extra = 1
    fields = ['title', 'description', 'order', 'delete_link']
    readonly_fields = ['delete_link']
    show_change_link = True
    can_delete = True

    def delete_link(self, obj):
        if obj.pk:
            from django.urls import reverse
            from django.utils.html import format_html
            url = reverse('admin:catalog_course_delete', args=[obj.pk])
            return format_html('<a href="{}" style="color:red;">Delete</a>', url)
        return ''
    delete_link.short_description = ''

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'order']
    search_fields = ['title']
    inlines = [CourseInline]

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
    list_display = ['title', 'subject']
    list_filter = ['subject']
    autocomplete_fields = ['subject']
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

