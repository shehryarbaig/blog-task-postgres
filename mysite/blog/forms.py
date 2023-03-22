from django import forms
from blog.models import Post
from blog.models import Tag


class PostForm(forms.ModelForm):
    tags = forms.CharField(required=True)

    class Meta:
        model = Post
        fields = ['title', 'content']

    def save(self, commit=True):
        post = super().save(commit=False)
        tags = self.cleaned_data['tags'].split(',')
        tag_objects = [Tag.objects.get_or_create(name=tag_name.strip())[0] for tag_name in tags]
        post.save()
        post.tags.set(tag_objects)
        if commit:
            post.save()
        return post
