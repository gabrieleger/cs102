from rest_framework import serializers

from accounts.models import User
from notes.models import Note, Tag


class NoteSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Tag.objects.all(),
        required=False
    )

    shared_to = serializers.SlugRelatedField(
        many=True,
        slug_field='email',
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Note
        fields = ('id', 'title', 'body', 'tags', 'shared_to', 'pub_date')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'is_active', 'is_staff', 'activation')
