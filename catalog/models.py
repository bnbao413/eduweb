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
    order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)

    # Video: use video_url for external embeds (YouTube, Vimeo), or upload a file.
    # video_url takes priority over video_file in the template.
    video_url = models.URLField(blank=True, help_text="Paste an embed URL, e.g. https://www.youtube.com/embed/VIDEO_ID")
    video_file = models.FileField(upload_to='lessons/videos/', blank=True)
    thumbnail = models.ImageField(upload_to='lessons/thumbnails/', blank=True)

    duration = models.CharField(max_length=20, blank=True, help_text="e.g. 12:34")
    transcript = models.TextField(blank=True)

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
    






class VideoCheckpoint(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='checkpoints')
    timestamp = models.PositiveIntegerField(
        help_text="Time in seconds when the video pauses. e.g. 90 = 1:30"
    )
    question = models.TextField(help_text="The question shown to the student at this timestamp.")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.lesson.title} @ {self.timestamp}s"


class CheckpointChoice(models.Model):
    checkpoint = models.ForeignKey(VideoCheckpoint, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        label = 'correct' if self.is_correct else 'wrong'
        return f"{self.text[:60]} ({label})"


class CheckpointResponse(models.Model):
    """
    Records a user's response to a VideoCheckpoint.

    One record per user+checkpoint (unique_together). If the user answers
    again in a later session, update_or_create overwrites it — last attempt
    wins. answered_at auto-updates on every save.

    is_correct is None for reflection checkpoints (no choices to grade).
    selected_choice is None for reflection checkpoints.
    """
    user             = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkpoint_responses')
    checkpoint       = models.ForeignKey(VideoCheckpoint, on_delete=models.CASCADE, related_name='responses')
    selected_choice  = models.ForeignKey(CheckpointChoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='responses')
    is_correct       = models.BooleanField(null=True, blank=True)
    answered_at      = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'checkpoint')

    def __str__(self):
        grade = 'correct' if self.is_correct else ('wrong' if self.is_correct is False else 'reflected')
        return f"{self.user.username} — {self.checkpoint} — {grade}"


class FinalExam(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='final_exam')
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    numbas_url = models.URLField(blank=True)

    def __str__(self):
        return self.title