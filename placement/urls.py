from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("start/", views.start_test, name="start_test"),
    path(
        "test/<int:attempt_id>/question/<int:question_number>/",
        views.question,
        name="question",
    ),
    path(
        "test/<int:attempt_id>/result/",
        views.result,
        name="result",
    ),
]
