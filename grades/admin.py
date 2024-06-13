from django.contrib import admin
from .models import Assignment
from .models import Submission

# Register your models here.
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline', 'weight', 'points')
    list_filter = ('deadline', 'weight', 'points')
    search_fields = ('title', 'description')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'author', 'grader', 'score')
    list_filter = ('assignment', 'author', 'grader', 'score')
    search_fields = ('assignment', 'author', 'grader', 'score')