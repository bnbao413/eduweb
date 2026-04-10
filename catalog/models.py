from django.db import models
from django.contrib.auth.models import User




class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Unit(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='units')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class TextbookPage(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='textbook_pages')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class NotesPage(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='notes_pages')
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class PracticeSet(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='practice_sets')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    numbas_url = models.URLField(blank=True)
    order = models.IntegerField(default=0)


    def __str__(self):
        return self.title




class UnitTest(models.Model):
    unit = models.OneToOneField(Unit, on_delete=models.CASCADE, related_name='unit_test')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    numbas_url = models.URLField(blank=True)


    def __str__(self):
        return self.title
    
class CourseAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_access')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_access')
    has_access = models.BooleanField(default=False)


    class Meta:
        unique_together = ('user', 'course')


    def __str__(self):
        return f"{self.user.username} - {self.course.title} - {self.has_access}"






class FinalExam(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='final_exam')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return self.title