from django import forms
from .models import Board


class BoardCreateForm(forms.ModelForm):
    """Form for creating a new board"""
    
    class Meta:
        model = Board
        fields = ['title', 'description', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'placeholder': 'Board title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'What is your board about?'
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 focus:ring-pink-500 border-gray-300 rounded'
            }),
        }


class BoardUpdateForm(forms.ModelForm):
    """Form for updating an existing board"""
    
    class Meta:
        model = Board
        fields = ['title', 'description', 'is_private']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'rows': 3,
            }),
            'is_private': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 focus:ring-pink-500 border-gray-300 rounded'
            }),
        }
