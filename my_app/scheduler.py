from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils.timezone import now
from django.core.mail import send_mail
from datetime import timedelta

from my_app.models import Assessment, CourseMember

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

def send_12h_reminder():
    from my_app.models import Assessment

    upcoming = Assessment.objects.filter(
        status='published',
        due_date__gt=now(),
        # due_date__lte=now() + timedelta(hours=12) # 12 hour warning 
        due_date__lte=now() + timedelta(minutes=1) # 1 min warning
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
    scheduler.add_job(
        send_12h_reminder,
        trigger='cron',
        # minute='*/5',  # 5 mins check
        minute='*',  # 1 min check
        id='12h_reminder',
        replace_existing=True,
        timezone='America/New_York'
    )
    scheduler.start()
    print("Scheduler started.")
