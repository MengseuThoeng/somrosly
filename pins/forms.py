from django import forms
from .models import Pin
from boards.models import Board


class PinCreateForm(forms.ModelForm):
    """Form for creating a new pin"""
    
    board = forms.ModelChoiceField(
        queryset=Board.objects.none(),
        required=False,
        empty_label="Select a board (optional)",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent'
        })
    )
    
    class Meta:
        model = Pin
        fields = ['title', 'description', 'image', 'board', 'source_url', 'tags', 'is_premium_only']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'placeholder': 'Add a title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Tell everyone what your pin is about'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'source_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'placeholder': 'https://example.com (optional)'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'placeholder': 'art, design, inspiration (comma-separated)'
            }),
            'is_premium_only': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-pink-600 bg-gray-100 border-gray-300 rounded focus:ring-pink-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter boards by current user
            self.fields['board'].queryset = Board.objects.filter(user=user)
    
    def clean_image(self):
        """Validate image file"""
        image = self.cleaned_data.get('image')
        
        if image:
            # Check file size (max 10MB)
            if image.size > 10 * 1024 * 1024:
                raise forms.ValidationError('Image file too large ( > 10MB )')
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError('File type not supported. Please upload an image.')
        
        return image


class PinUpdateForm(forms.ModelForm):
    """Form for updating an existing pin"""
    
    board = forms.ModelChoiceField(
        queryset=Board.objects.none(),
        required=False,
        empty_label="Select a board (optional)",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent'
        })
    )
    
    class Meta:
        model = Pin
        fields = ['title', 'description', 'board', 'source_url', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
                'rows': 4,
            }),
            'source_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
            }),
            'tags': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['board'].queryset = Board.objects.filter(user=user)
