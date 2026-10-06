from django.contrib import admin
from import_export import resources
from import_export.admin import ExportMixin

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


class ParticipantResource(resources.ModelResource):
    full_name = resources.Field(
        attribute="full_name",
        column_name="Full name",
    )
    phone = resources.Field(
        attribute="phone",
        column_name="Phone",
    )
    birth_date = resources.Field(
        attribute="birth_date",
        column_name="Birth date",
    )

    class Meta:
        model = Participant
        fields = (
            "id",
            "full_name",
            "phone",
            "birth_date",
        )
        export_order = fields


@admin.register(Participant)
class ParticipantAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ParticipantResource
    list_display = ("full_name", "phone", "birth_date")


class AttemptResource(resources.ModelResource):
    full_name = resources.Field(
        attribute="participant__full_name", column_name="Full name"
    )
    phone = resources.Field(attribute="participant__phone", column_name="Phone")
    birth_date = resources.Field(
        attribute="participant__birth_date", column_name="Birth date"
    )
    test = resources.Field(attribute="test__title", column_name="Test")

    class Meta:
        model = Attempt
        fields = (
            "id",
            "full_name",
            "phone",
            "birth_date",
            "test",
            "score",
            "level",
            "started_at",
            "completed_at",
        )
        export_order = fields


@admin.register(Attempt)
class AttemptAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = AttemptResource
    list_display = (
        "participant",
        "test",
        "score",
        "level",
        "started_at",
        "completed_at",
    )
    list_filter = ("test", "level")


class UserAnswerResource(resources.ModelResource):
    full_name = resources.Field(
        attribute="attempt__participant__full_name",
        column_name="Full name",
    )
    phone = resources.Field(
        attribute="attempt__participant__phone",
        column_name="Phone",
    )
    test = resources.Field(
        attribute="attempt__test__title",
        column_name="Test",
    )
    question = resources.Field(
        attribute="question__text",
        column_name="Question",
    )
    answer = resources.Field(
        attribute="answer__text",
        column_name="Answer",
    )

    class Meta:
        model = UserAnswer
        fields = (
            "id",
            "full_name",
            "phone",
            "test",
            "question",
            "answer",
            "is_correct",
        )
        export_order = fields


@admin.register(UserAnswer)
class UserAnswerAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = UserAnswerResource
    list_display = (
        "attempt",
        "question",
        "answer",
        "is_correct",
    )
    list_filter = ("is_correct",)
