"""
Management command to load the English Placement Test questions/answers
from a JSON file into the database.

Место в проекте:
    <your_app>/management/commands/load_placement_test.py

(management/ и management/commands/ — обычные Python-пакеты,
не забудьте положить в них пустые __init__.py, если их ещё нет)

Запуск:
    python manage.py load_placement_test path/to/placement_test_data.json

Команда идемпотентна:
    - Test ищется/создаётся по title.
    - Section ищется/создаётся по (test, title), order обновляется.
    - Reading ищется/создаётся по (section, title), text обновляется.
    - Question ищется/создаётся по (section, order), text и reading обновляются.
    - Answers для каждого вопроса при повторном запуске полностью
      пересоздаются (старые удаляются, новые вставляются) — так
      правки в JSON-файле всегда корректно долетают до базы.
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from placement.models import Test, Section, Reading, Question, Answer


class Command(BaseCommand):
    help = "Loads placement test data (sections, readings, questions, answers) from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file",
            type=str,
            help="Path to the JSON file with test data",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate the file without writing to the database",
        )

    def handle(self, *args, **options):
        path = Path(options["json_file"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        self._validate(data)

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — no changes will be saved."))
            with transaction.atomic():
                self._load(data)
                transaction.set_rollback(True)
            self.stdout.write(self.style.SUCCESS("Dry run finished, data is valid."))
            return

        with transaction.atomic():
            self._load(data)

        self.stdout.write(self.style.SUCCESS("Placement test data loaded successfully."))

    def _validate(self, data):
        for section in data["sections"]:
            for question in section["questions"]:
                answers = question["answers"]
                if len(answers) < 2:
                    raise CommandError(
                        f"Question order={question['order']} has fewer than 2 answers"
                    )
                correct_count = sum(1 for _, is_correct in answers if is_correct)
                if correct_count != 1:
                    raise CommandError(
                        f"Question order={question['order']} has "
                        f"{correct_count} correct answers (expected exactly 1)"
                    )

    def _load(self, data):
        test, created = Test.objects.get_or_create(title=data["test"]["title"])
        self._log_obj("Test", test.title, created)

        for section_data in data["sections"]:
            section, created = Section.objects.get_or_create(
                test=test,
                title=section_data["title"],
                defaults={"order": section_data["order"]},
            )
            if not created and section.order != section_data["order"]:
                section.order = section_data["order"]
                section.save(update_fields=["order"])
            self._log_obj("Section", section.title, created)

            reading = None
            reading_data = section_data.get("reading")
            if reading_data:
                reading, r_created = Reading.objects.get_or_create(
                    section=section,
                    title=reading_data["title"],
                    defaults={"text": reading_data["text"]},
                )
                if not r_created and reading.text != reading_data["text"]:
                    reading.text = reading_data["text"]
                    reading.save(update_fields=["text"])
                self._log_obj("Reading", reading.title, r_created)

            for question_data in section_data["questions"]:
                question, q_created = Question.objects.get_or_create(
                    section=section,
                    order=question_data["order"],
                    defaults={
                        "text": question_data["text"],
                        "reading": reading,
                    },
                )
                if not q_created:
                    question.text = question_data["text"]
                    question.reading = reading
                    question.save(update_fields=["text", "reading"])

                # Пересоздаём варианты ответов — просто и надёжно при повторном запуске
                question.answers.all().delete()
                Answer.objects.bulk_create(
                    [
                        Answer(question=question, text=answer_text, is_correct=is_correct)
                        for answer_text, is_correct in question_data["answers"]
                    ]
                )

            self.stdout.write(
                f"  -> {len(section_data['questions'])} questions loaded for '{section.title}'"
            )

    def _log_obj(self, label, name, created):
        verb = "created" if created else "found existing"
        self.stdout.write(f"{label} {verb}: {name}")
