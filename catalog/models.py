from django.db import models





class Subject(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Course(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
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

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


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
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class UnitTest(models.Model):
    unit = models.OneToOneField(Unit, on_delete=models.CASCADE, related_name='unit_test')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return self.title


class FinalExam(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='final_exam')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return self.title







