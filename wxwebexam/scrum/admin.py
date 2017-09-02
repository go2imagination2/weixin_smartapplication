from django.contrib import admin

from scrum.models import *


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 1


class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Entry)
admin.site.register(Paper)


class ExamRecordInline(admin.StackedInline):
    model = ExamRecord
    extra = 3


class ExamAdmin(admin.ModelAdmin):
    inlines = [ExamRecordInline]


admin.site.register(Exam, ExamAdmin)
