from django.db.models import Q
from rest_framework import viewsets

from notes.models import Note, Tag, User
from .serializers import NoteSerializer, UserSerializer


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    queryset = Note.objects.all()

    def filter_queryset(self, queryset):
        user_notes = Note.objects.filter(Q(owner=self.request.user) | Q(shared_to=self.request.user))

        filter_set = {}
        if tag_filter_name := self.request.GET.get('tag'):
            tag_filter = Tag.objects.filter(name=tag_filter_name)
            filter_set['tags__in'] = tag_filter
        if search_title := self.request.GET.get('search'):
            filter_set['title'] = search_title

        return user_notes.filter(**filter_set).order_by('-pub_date')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        serializer.save()
