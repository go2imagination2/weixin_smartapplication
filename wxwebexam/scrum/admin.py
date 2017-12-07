from django.contrib import admin

from scrum.models import *


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1


class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class EntryOptionInline(admin.StackedInline):
    model = EntryOption
    extra = 4


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    inlines = [EntryOptionInline]


class ExamRecordInline(admin.StackedInline):
    model = ExamRecord
    extra = 3


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    inlines = [ExamRecordInline]


@admin.register(ExamRecord)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'update_time', 'score')
    date_hierarchy = 'update_time'


admin.site.register(Paper)
