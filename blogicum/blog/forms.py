from django import forms

from .models import Post, Comment


# не совсем поняла про группировку импортов: разделить каждую группу импортов пустой строкой
# или с новой строки каждый импорт прописывать, а не через запятую

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'datetime-local'})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
