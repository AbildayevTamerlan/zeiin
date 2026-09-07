from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ParticipantForm
from .models import Attempt, Question, Test, UserAnswer


def home(request):
    return render(request, "placement/home.html")


def start_test(request):
    test = get_object_or_404(
        Test,
        title="English Placement Test",
    )

    if request.method == "POST":
        form = ParticipantForm(request.POST)

        if form.is_valid():
            participant = form.save()

            total_questions = Question.objects.filter(section__test=test).count()

            attempt = Attempt.objects.create(
                participant=participant,
                test=test,
                total_questions=total_questions,
            )

            request.session["attempt_id"] = attempt.id

            return redirect(
                "question",
                attempt_id=attempt.id,
                question_number=1,
            )
    else:
        form = ParticipantForm()

    return render(
        request,
        "placement/start_test.html",
        {"form": form},
    )


def question(request, attempt_id, question_number):
    session_attempt_id = request.session.get("attempt_id")

    if session_attempt_id != attempt_id:
        return redirect("home")

    attempt = get_object_or_404(
        Attempt,
        id=attempt_id,
        completed_at__isnull=True,
    )

    questions = list(
        Question.objects.filter(section__test=attempt.test)
        .select_related("section", "reading")
        .prefetch_related("answers")
        .order_by("section__order", "order")
    )

    total_questions = len(questions)

    if question_number < 1 or question_number > total_questions:
        return redirect(
            "question",
            attempt_id=attempt.id,
            question_number=1,
        )

    current_question = questions[question_number - 1]

    if request.method == "POST":
        answer_id = request.POST.get("answer")
        action = request.POST.get("action")

        if answer_id:
            answer = get_object_or_404(
                current_question.answers,
                id=answer_id,
            )

            UserAnswer.objects.update_or_create(
                attempt=attempt,
                question=current_question,
                defaults={
                    "answer": answer,
                    "is_correct": answer.is_correct,
                },
            )

        answered_questions = set(
            UserAnswer.objects.filter(attempt=attempt).values_list(
                "question_id", flat=True
            )
        )

        if action == "finish":
            unanswered_questions = [
                index + 1
                for index, question in enumerate(questions)
                if question.id not in answered_questions
            ]

            if unanswered_questions and not request.POST.get("confirm_finish"):
                user_answer = UserAnswer.objects.filter(
                    attempt=attempt,
                    question=current_question,
                ).first()

                return render(
                    request,
                    "placement/question.html",
                    {
                        "attempt": attempt,
                        "question": current_question,
                        "question_number": question_number,
                        "total_questions": total_questions,
                        "user_answer": user_answer,
                        "answered_questions": answered_questions,
                        "questions": questions,
                        "previous_question_number": (
                            question_number - 1 if question_number > 1 else None
                        ),
                        "next_question_number": (
                            question_number + 1
                            if question_number < total_questions
                            else None
                        ),
                        "unanswered_questions": unanswered_questions,
                        "show_finish_warning": True,
                    },
                )

            score = UserAnswer.objects.filter(
                attempt=attempt,
                is_correct=True,
            ).count()

            attempt.score = score
            attempt.level = get_level(score)
            attempt.completed_at = timezone.now()
            attempt.save()

            return redirect(
                "result",
                attempt_id=attempt.id,
            )

        if action == "previous":
            return redirect(
                "question",
                attempt_id=attempt.id,
                question_number=question_number - 1,
            )

        if action == "next":
            return redirect(
                "question",
                attempt_id=attempt.id,
                question_number=question_number + 1,
            )

    answered_questions = set(
        UserAnswer.objects.filter(attempt=attempt).values_list("question_id", flat=True)
    )

    user_answer = UserAnswer.objects.filter(
        attempt=attempt,
        question=current_question,
    ).first()

    return render(
        request,
        "placement/question.html",
        {
            "attempt": attempt,
            "question": current_question,
            "question_number": question_number,
            "total_questions": total_questions,
            "user_answer": user_answer,
            "answered_questions": answered_questions,
            "questions": questions,
            "previous_question_number": (
                question_number - 1 if question_number > 1 else None
            ),
            "next_question_number": (
                question_number + 1 if question_number < total_questions else None
            ),
        },
    )


def result(request, attempt_id):
    session_attempt_id = request.session.get("attempt_id")

    if session_attempt_id != attempt_id:
        return redirect("home")

    attempt = get_object_or_404(
        Attempt,
        id=attempt_id,
    )

    if attempt.completed_at is None:
        return redirect(
            "question",
            attempt_id=attempt.id,
            question_number=1,
        )

    return render(
        request,
        "placement/result.html",
        {"attempt": attempt},
    )


def get_level(score):
    if score <= 10:
        return "A1 Beginner"
    elif score <= 18:
        return "A2 Elementary"
    elif score <= 26:
        return "B1 Pre-Intermediate"
    elif score <= 33:
        return "B1+ Intermediate"
    elif score <= 40:
        return "B2 Upper-Intermediate"
    elif score <= 46:
        return "C1 Advanced"
    else:
        return "C2 Proficiency"
