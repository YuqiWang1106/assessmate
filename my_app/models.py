from django.db import models
import uuid

# 1. User Table
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. Course Table
class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_number = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    course_semester =models.CharField(max_length = 20)
    course_year = models.CharField(max_length = 20)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_number} - {self.course_name}"
    

# 3. CourseMember Table
class CourseMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})  # 只能是学生
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "user")

    def __str__(self):
        return f"{self.user.name} in {self.course.course_number}"

# 4. Team Table
class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.team_name

# 5. TeamMember Table
class TeamMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    course_member = models.ForeignKey(CourseMember, on_delete=models.CASCADE)  # 📌 ForeignKey 改成 CourseMember
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "course_member")

    def __str__(self):
        return f"{self.course_member.user.name} in {self.team.team_name}"

# 6. Assessment Table
class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('finished', 'Finished'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    publish_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    results_released = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 7. AssessmentQuestion Table
class AssessmentQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    QUESTION_TYPES = [
        ('likert', 'Likert Scale'),
        ('open', 'Open-ended'),
    ]
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    content = models.TextField()

    def __str__(self):
        return self.content

# 8. AssessmentResponse Table
class AssessmentResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responses_given")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responses_received")
    answers = models.JSONField()
    last_saved = models.DateTimeField(auto_now=True)
    submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"Response from {self.from_user} to {self.to_user} ({self.assessment.title})"

# 9. TeamAssessmentAnalysis: overall (LLM)
class TeamAssessmentAnalysis(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    overall_rating = models.FloatField()
    keywords = models.JSONField()
    summary = models.TextField()
    suggestions = models.TextField()
    radar_scores = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "assessment")


# 10. QuestionAnalysisCache: Detail (LLM)
class QuestionAnalysisCache(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=10)  # "likert" or "open"
    summary = models.TextField()
    analysis = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "assessment", "question")


# 11. LLM Improvement for Open Ended Question
class OpenEndedToneAnalysis(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tone_given")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tone_received")
    tone_feedback = models.TextField()
    rewritten_answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assessment", "question", "from_user", "to_user")
