from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TextbookPage, NotesPage


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. You will use this to reset your password.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        # Usernames must be unique case-insensitively: "JOHN" == "john".
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('That username is already taken. Please choose another.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user




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

