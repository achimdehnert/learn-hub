"""Admin registrations for iil_learnfw models."""

from django.contrib import admin

from iil_learnfw.models import (
    Answer,
    Attempt,
    AttemptAnswer,
    Badge,
    Category,
    CertificateTemplate,
    Chapter,
    Course,
    Enrollment,
    IssuedCertificate,
    Lesson,
    OnboardingFlow,
    OnboardingStep,
    PointsTransaction,
    Question,
    Quiz,
    ScormPackage,
    ScormTracking,
    UserBadge,
    UserOnboardingState,
    UserPoints,
    UserProgress,
)


# --- Course ---


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ("title", "ordering")


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "ordering", "content_type")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant_id")
    search_fields = ("name",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title",)
    inlines = [ChapterInline]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "ordering")
    list_filter = ("course",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter", "ordering", "content_type")
    list_filter = ("content_type", "chapter__course")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "enrolled_at")
    list_filter = ("course",)
    raw_id_fields = ("user",)


# --- Assessment ---


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "chapter", "passing_score")
    list_filter = ("chapter__course",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "question_type")
    list_filter = ("question_type",)
    inlines = [AnswerInline]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "passed", "started_at")
    list_filter = ("passed",)
    raw_id_fields = ("user",)


admin.site.register(Answer)
admin.site.register(AttemptAnswer)


# --- Certificate ---


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default")


@admin.register(IssuedCertificate)
class IssuedCertificateAdmin(admin.ModelAdmin):
    list_display = ("user", "template", "tenant_id")
    raw_id_fields = ("user",)


# --- Gamification ---


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "trigger", "is_active")
    list_filter = ("trigger", "is_active")


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "awarded_at")
    raw_id_fields = ("user",)


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ("user", "total_points")
    raw_id_fields = ("user",)


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "points", "reason", "created_at")
    raw_id_fields = ("user",)


# --- Onboarding ---


class OnboardingStepInline(admin.TabularInline):
    model = OnboardingStep
    extra = 0
    fields = ("title", "ordering", "is_required")


@admin.register(OnboardingFlow)
class OnboardingFlowAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    inlines = [OnboardingStepInline]


@admin.register(OnboardingStep)
class OnboardingStepAdmin(admin.ModelAdmin):
    list_display = ("title", "flow", "ordering", "is_required")


@admin.register(UserOnboardingState)
class UserOnboardingStateAdmin(admin.ModelAdmin):
    list_display = ("user", "flow", "status")
    raw_id_fields = ("user",)


# --- Progress ---


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "status", "completed_at")
    list_filter = ("status",)
    raw_id_fields = ("user",)


# --- SCORM ---


@admin.register(ScormPackage)
class ScormPackageAdmin(admin.ModelAdmin):
    list_display = ("scorm_version", "course", "imported_at")


@admin.register(ScormTracking)
class ScormTrackingAdmin(admin.ModelAdmin):
    list_display = ("user", "package", "status")
    raw_id_fields = ("user",)
