from django.db import models


class Participant(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    birth_date = models.DateField()

    def __str__(self):
        return self.full_name


class Test(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class Section(models.Model):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="sections",
    )
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class Reading(models.Model):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="readings",
    )
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title


class Question(models.Model):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    reading = models.ForeignKey(
        Reading,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="questions",
    )
    text = models.TextField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Attempt(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    score = models.PositiveIntegerField(null=True, blank=True)
    level = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.participant} - {self.test}"


class UserAnswer(models.Model):
    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name="user_answers",
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["attempt", "question"],
                name="unique_answer_per_question",
            ),
        ]

    def __str__(self):
        return f"{self.attempt} - Question {self.question_id}"
