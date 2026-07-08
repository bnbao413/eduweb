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


class PageOverlay(models.Model):
    """Staff-placed free-form overlay items (images/GIFs/text) for a given page
    URL path. Rendered on top of the page for everyone; editable by staff."""
    path = models.CharField(max_length=300, unique=True)
    items = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"overlay {self.path} ({len(self.items or [])} items)"


class SiteTheme(models.Model):
    """Singleton-ish row of site-wide colour overrides, editable by staff from
    the Edit-page panel. Each field holds a hex colour; blank = fall back to the
    default government palette defined in app.css."""
    bg = models.CharField(max_length=20, blank=True)         # desktop background
    surface = models.CharField(max_length=20, blank=True)    # paper / cards
    surface_2 = models.CharField(max_length=20, blank=True)  # panels
    border = models.CharField(max_length=20, blank=True)     # lines
    text = models.CharField(max_length=20, blank=True)       # ink
    accent = models.CharField(max_length=20, blank=True)     # links / buttons
    on_accent = models.CharField(max_length=20, blank=True)  # text on accent
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "site theme"







