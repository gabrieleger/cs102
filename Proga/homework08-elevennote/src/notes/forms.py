from django import forms
from django.core.exceptions import ValidationError

from .models import Note, Tag, User


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'body']

    field_order = ['title', 'tags', 'shared_to', 'body']

    tags = forms.CharField(label='Tags', required=False, widget=forms.TextInput(attrs={'data-role':   'tagsinput',
                                                                                       'placeholder': 'Add a tag',
                                                                                       'class':       'd-block w-25'}))

    shared_to = forms.CharField(label='Shared to', required=False, widget=forms.TextInput(attrs={'data-role':   'tagsinput',
                                                                                                 'placeholder': 'Add user',
                                                                                                 'class':       'd-block w-25'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk is not None:
            existing_tags = ','.join(map(str, self.instance.tags.all()))
            if existing_tags:
                self.fields['tags'].widget.attrs['value'] = existing_tags
            existing_users = ','.join(map(str, self.instance.shared_to.all()))
            if existing_users:
                self.fields['shared_to'].widget.attrs['value'] = existing_users

    def clean_shared_to(self):
        data = self.cleaned_data['shared_to']
        user_list = data.strip().split(',') if data else []
        for user_email in user_list:
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                raise ValidationError(f"User {user_email} doesn't exist!")
        return user_list

    def save(self, commit=True):
        instance = super().save(commit=commit)
        instance.tags.clear()
        instance.shared_to.clear()

        tags = self.cleaned_data.get('tags')
        tags_list = tags.split(',')

        for tag in tags_list:
            tag, created = Tag.objects.get_or_create(name=tag)
            instance.tags.add(tag)

        shared_to_list = self.cleaned_data.get('shared_to')
        for user_email in shared_to_list:
            user = User.objects.get(email=user_email)
            instance.shared_to.add(user)

        instance.save()
        return instance
