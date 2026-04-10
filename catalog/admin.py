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
    CourseAccess,
)

admin.site.register(CourseAccess)
admin.site.register(Course)
admin.site.register(Unit)
admin.site.register(Lesson)
admin.site.register(TextbookPage)
admin.site.register(NotesPage)
admin.site.register(PracticeSet)
admin.site.register(UnitTest)
admin.site.register(FinalExam)