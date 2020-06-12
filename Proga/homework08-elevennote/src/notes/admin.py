from django.contrib import admin

from .models import User, Note, Tag


# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     pass


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ['name']
