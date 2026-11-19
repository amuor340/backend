from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .homework_views import ClassAssignmentViewSet
from .submission_views import HomeworkSubmissionViewSet
from .views import (
    TeacherProfileListView,
    TeacherAssignmentListView,
    TeacherAssignmentCreateView,
    TeacherAssignmentDetailView,
    TeacherAssignmentUpdateView,
    TeacherAssignmentDeleteView,
    TeacherProfileViewSet,
)

router = SimpleRouter()
router.register(r"my-profile", TeacherProfileViewSet, basename="my-profile")
router.register(r"homework", ClassAssignmentViewSet, basename="class-assignment")
router.register(r"submissions", HomeworkSubmissionViewSet, basename="homework-submission")

urlpatterns = [
    # Specific routes must precede the empty-path assignment list.
    path("teachers/", TeacherProfileListView.as_view(), name="teacher-list"),
    path("create/", TeacherAssignmentCreateView.as_view(), name="assignment-create"),
    path("update/<int:pk>/", TeacherAssignmentUpdateView.as_view(), name="assignment-update"),
    path("delete/<int:pk>/", TeacherAssignmentDeleteView.as_view(), name="assignment-delete"),
    path("<int:pk>/", TeacherAssignmentDetailView.as_view(), name="assignment-detail"),
    path("", include(router.urls)),
    path("", TeacherAssignmentListView.as_view(), name="assignment-list"),
]
