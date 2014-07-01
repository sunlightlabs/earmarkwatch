from django.contrib import admin

class SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'chamber', 'type', 'year')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question')
