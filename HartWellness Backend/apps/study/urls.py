from django.urls import re_path
from . import views

urlpatterns = [
    # ── User / Mobile ─────────────────────────────────────────

    # Study Topics
    re_path(r'^study/topics/?$', views.StudyTopicListView.as_view()),
    re_path(r'^study/topics/(?P<pk>\d+)/?$', views.StudyTopicDetailView.as_view()),

    # Study Materials
    re_path(r'^study/materials/?$', views.StudyMaterialListView.as_view()),
    re_path(r'^study/materials/complete/?$', views.MarkMaterialCompleteView.as_view()),
    re_path(r'^study/materials/(?P<pk>\d+)/?$', views.StudyMaterialDetailView.as_view()),

    # Quiz
    re_path(r'^study/quizzes/submit/?$', views.QuizSubmitView.as_view()),
    re_path(r'^study/quizzes/?$', views.QuizListView.as_view()),
    re_path(r'^study/quizzes/(?P<pk>\d+)/?$', views.QuizDetailView.as_view()),

    # Attempts / History
    re_path(r'^study/attempts/by-topic/?$', views.MyQuizAttemptsByTopicView.as_view()),
    re_path(r'^study/attempts/?$', views.MyQuizAttemptsView.as_view()),
    re_path(r'^study/attempts/(?P<pk>\d+)/?$', views.QuizAttemptDetailView.as_view()),

    # Progress (profile page)
    re_path(r'^study/progress/?$', views.StudyProgressView.as_view()),

    # ── Admin ─────────────────────────────────────────────────

    # Topics
    re_path(r'^admin/study/topics/?$', views.AdminStudyTopicListCreateView.as_view()),
    re_path(r'^admin/study/topics/(?P<pk>\d+)/?$', views.AdminStudyTopicDetailView.as_view()),

    # Materials
    re_path(r'^admin/study/materials/?$', views.AdminStudyMaterialListCreateView.as_view()),
    re_path(r'^admin/study/materials/(?P<pk>\d+)/?$', views.AdminStudyMaterialDetailView.as_view()),

    # Quizzes
    re_path(r'^admin/study/quizzes/?$', views.AdminQuizListCreateView.as_view()),
    re_path(r'^admin/study/quizzes/(?P<pk>\d+)/?$', views.AdminQuizDetailView.as_view()),

    # Questions
    re_path(r'^admin/study/questions/?$', views.AdminQuestionListCreateView.as_view()),
    re_path(r'^admin/study/questions/(?P<pk>\d+)/?$', views.AdminQuestionDetailView.as_view()),

    # Quiz Results
    re_path(r'^admin/study/attempts/?$', views.AdminQuizAttemptListView.as_view()),
]