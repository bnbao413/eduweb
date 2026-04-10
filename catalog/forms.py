from django import forms
from .models import TextbookPage, NotesPage




class TextbookPageForm(forms.ModelForm):
    class Meta:
        model = TextbookPage
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Page title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 20,
                'placeholder': 'Write textbook content here. Use Markdown and LaTeX math syntax later.'
            }),
        }




class NotesPageForm(forms.ModelForm):
    class Meta:
        model = NotesPage
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Page title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 20,
                'placeholder': 'Write notes content here. Use Markdown and LaTeX math syntax later.'
            }),
        }

