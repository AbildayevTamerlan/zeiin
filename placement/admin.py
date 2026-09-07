from django.contrib import admin

from .models import (
    Answer,
    Attempt,
    Participant,
    Question,
    Reading,
    Section,
    Test,
    UserAnswer,
)


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "test", "order")
    list_filter = ("test",)
    ordering = ("test", "order")


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("title", "section")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "section", "reading", "order")
    list_filter = ("section",)
    ordering = ("section", "order")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct")
    list_filter = ("is_correct",)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "birth_date")


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        "participant",
        "test",
        "score",
        "level",
        "started_at",
        "completed_at",
    )
    list_filter = ("test", "level")


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "answer", "is_correct")
    list_filter = ("is_correct",)
