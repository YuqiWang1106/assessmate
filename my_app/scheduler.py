from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from django.utils.timezone import now
from django.core.mail import send_mail
from datetime import timedelta
from my_app.models import Assessment, CourseMember

def send_12h_reminder():
    upcoming = Assessment.objects.filter(
        status='published',
        due_date__gt=now(),
        due_date__lte=now() + timedelta(minutes=1) # before time
    )

    for a in upcoming:
        course = a.course
        students = CourseMember.objects.filter(course=course)
        emails = [cm.user.email for cm in students]

        send_mail(
            subject=f"[Assessmate] Reminder: {a.title} due in 12 hours",
            message=f"""
Hello,

Just a reminder that your assessment "{a.title}" in course {course.course_number} is due in 12 hours.

Make sure to submit it before the deadline!

See you on Assessmate!
""",
            from_email="no-reply@assessmate.edu",
            recipient_list=emails,
            fail_silently=False
        )

        print(f"Sent 12h reminder for: {a.title}")

def start():
    scheduler = BackgroundScheduler(
        jobstores={'default': MemoryJobStore()},
        timezone="America/New_York"
    )

    scheduler.add_job(
        send_12h_reminder,
        trigger='cron',
        minute='*',
        id='12h_reminder',
        replace_existing=True
    )

    scheduler.start()
