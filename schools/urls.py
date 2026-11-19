from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    EducationSystemsView,
    MySchoolView,
    PlatformDashboardView,
    SchoolRegistrationView,
    SchoolViewSet,
    StarterSubjectsView,
)

router = DefaultRouter()
router.register("", SchoolViewSet, basename="school")

urlpatterns = [
    path("register/", SchoolRegistrationView.as_view(), name="school-register"),
    path("my-school/", MySchoolView.as_view(), name="my-school"),
    path("education-systems/", EducationSystemsView.as_view(), name="education-systems"),
    path("starter-subjects/", StarterSubjectsView.as_view(), name="starter-subjects"),
    path("platform-dashboard/", PlatformDashboardView.as_view(), name="platform-dashboard"),
    path("", include(router.urls)),
]
