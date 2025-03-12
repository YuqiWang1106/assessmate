from django.db import models
import uuid

# 1. 用户表 (User)
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

# 2. 课程表 (Course)
class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_number = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course_number} - {self.course_name}"

# 3. 团队表 (Team)
class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.team_name

# 4. 团队成员表 (TeamMember)
class TeamMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

# 5. 评估表 (Assessment)
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
    results_released = models.BooleanField(default=False)  # 结果是否已发布
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 6. 评估问题表 (AssessmentQuestion)
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

# 7. 评估反馈表 (AssessmentResponse)
class AssessmentResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responses_given")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="responses_received")
    answers = models.JSONField()  # 存储 Likert 和 Open-ended 回答
    last_saved = models.DateTimeField(auto_now=True)
    submitted = models.BooleanField(default=False)  # 是否提交

    def __str__(self):
        return f"Response from {self.from_user} to {self.to_user} ({self.assessment.title})"
