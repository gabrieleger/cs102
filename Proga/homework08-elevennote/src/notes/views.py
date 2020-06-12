from django.db.models import Q
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.urls import reverse, reverse_lazy

from django.views.generic.base import ContextMixin

from .models import Note, Tag
from .forms import NoteForm
from .mixins import NoteMixin


class NoteList(LoginRequiredMixin, ListView):
    paginate_by = 5
    template_name = 'notes/index.html'
    context_object_name = 'latest_note_list'

    def set_extra_context(self, key: str, value):
        if self.extra_context is None:
            self.extra_context = {}
        self.extra_context[key] = value

    def get_queryset(self):
        user_notes = Note.objects.filter(Q(owner=self.request.user) | Q(shared_to=self.request.user))

        filter_set = {}
        if tag_filter_name := self.request.GET.get('tag'):
            tag_filter = Tag.objects.filter(name=tag_filter_name)
            filter_set['tags__in'] = tag_filter
            self.set_extra_context('tag_filter', tag_filter_name)
        if search_title := self.request.GET.get('search'):
            filter_set['title'] = search_title
            self.set_extra_context('search_title', search_title)

        return user_notes.filter(**filter_set).order_by('-pub_date')


class NoteDetail(LoginRequiredMixin, DetailView):
    model = Note
    template_name = 'notes/detail.html'
    context_object_name = 'note'

    def get_queryset(self):
        return Note.objects.filter(Q(owner=self.request.user) | Q(shared_to=self.request.user))


class NoteCreate(LoginRequiredMixin, NoteMixin, CreateView):
    form_class = NoteForm
    template_name = 'notes/form.html'
    success_url = reverse_lazy('notes:index')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(NoteCreate, self).form_valid(form)


class NoteUpdate(LoginRequiredMixin, NoteMixin, UpdateView):
    model = Note
    form_class = NoteForm
    template_name = 'notes/form.html'

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse('notes:update', kwargs={
            'pk': self.object.pk
        })


class NoteDelete(LoginRequiredMixin, DeleteView):
    model = Note
    success_url = reverse_lazy('notes:create')

    def get_queryset(self):
        return Note.objects.filter(owner=self.request.user)

